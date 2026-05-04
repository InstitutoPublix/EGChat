// Frontend do chat.
// mantem o historico curto no navegador;
// renderiza mensagens e markdown;
// chama a API Flask /api/chat sem manter sessao no servidor.
const config = window.MENTOR_CONFIG || {};
const welcomeMessage =
  config.welcomeMessage ||
  "Ola! Sou o Mentor Virtual e estou aqui para ajudar com o curso de Transformacao Digital.\n\nVoce pode perguntar sobre cronograma, horarios, atividades, aulas presenciais, mentorias e projeto final.";
const maxHistoryInteractions = Number(config.maxHistoryInteractions || 2);
const maxVisibleMessages = maxHistoryInteractions * 2;

const messagesEl = document.querySelector("#messages");
const formEl = document.querySelector("#chatForm");
const inputEl = document.querySelector("#messageInput");
const statusEl = document.querySelector("#statusLine");
const clearButton = document.querySelector("#clearChat");
const sendButton = document.querySelector(".send-button");

// sessionStorage guarda dados apenas enquanto a aba/sessao do navegador existe.
// Isso mantem o backend stateless e reduz custo operacional.
const storageKeys = {
  messages: "mentor_virtual_tjce_messages",
  history: "mentor_virtual_tjce_history",
};

// SVG inline evita dependencias externas e garante que os icones renderizem
// bem em Cloud Run mesmo sem CDN ou pacote de icones.
const avatarIcons = {
  assistant: `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="5" y="8" width="14" height="10" rx="3"></rect>
      <path d="M12 4v4"></path>
      <path d="M9 4h6"></path>
      <path d="M9 13h.01"></path>
      <path d="M15 13h.01"></path>
      <path d="M8 18v2"></path>
      <path d="M16 18v2"></path>
    </svg>
  `,
  user: `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20 21a8 8 0 0 0-16 0"></path>
      <circle cx="12" cy="8" r="4"></circle>
    </svg>
  `,
};

if (window.marked) {
  window.marked.setOptions({
    breaks: true,
    gfm: true,
  });
}

let messages = loadJson(storageKeys.messages, [
  {
    role: "assistant",
    content: welcomeMessage,
  },
]);
let chatHistory = loadJson(storageKeys.history, []);

function loadJson(key, fallback) {
  // Leitura defensiva, se o sessionStorage estiver corrompido ou bloqueado,
  // o app continua funcionando com o estado inicial.
  try {
    const value = sessionStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

function saveState() {
  // Persiste mensagens visiveis e historico RAG separadamente. As mensagens
  // sao para UI; o historico e enviado ao backend para manter contexto curto.
  sessionStorage.setItem(storageKeys.messages, JSON.stringify(messages));
  sessionStorage.setItem(storageKeys.history, JSON.stringify(chatHistory));
}

function trimVisibleMessages() {
  // mantem a saudacao e apenas as ultimas
  // interacoes, evitando que a tela cresca indefinidamente.
  const welcome = messages.slice(0, 1);
  const interactionMessages = messages.slice(1);
  messages = welcome.concat(interactionMessages.slice(-maxVisibleMessages));
}

function renderMessages() {
  // Re-render simples e previsivel. Como o historico e curto, nao precisamos
  // de framework ou reconciliacao complexa.
  messagesEl.innerHTML = "";
  messages.forEach((message) => appendMessage(message));
  scrollToBottom();
}

function appendMessage(message, options = {}) {
  // Cada mensagem e criada com DOM APIs para evitar interpolar texto do usuario
  // diretamente em HTML. Respostas do assistente passam por renderizacao segura.
  const row = document.createElement("article");
  row.className = `message ${message.role}`;
  if (options.loading) {
    row.classList.add("loading");
    row.dataset.loading = "true";
  }

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.setAttribute(
    "aria-label",
    message.role === "user" ? "Usuario" : "Mentor Virtual"
  );
  avatar.innerHTML =
    message.role === "user" ? avatarIcons.user : avatarIcons.assistant;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (message.role === "assistant") {
    renderAssistantMarkdown(bubble, message.content);
  } else {
    bubble.textContent = message.content;
  }

  if (options.loading) {
    const span = document.createElement("span");
    span.className = "loading-dots";
    span.textContent = message.content;
    bubble.textContent = "";
    bubble.appendChild(span);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
}

function escapeHtml(value) {
  // Fallback seguro quando marked/DOMPurify nao carregam.
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderAssistantMarkdown(target, markdown) {
  // marked entende markdown completo; DOMPurify remove HTML perigoso antes
  // de inserir no DOM. Sem as libs, mantemos fallback seguro em texto.
  if (!window.marked || !window.DOMPurify) {
    target.innerHTML = escapeHtml(markdown).replace(/\n/g, "<br>");
    return;
  }

  const parsedHtml = window.marked.parse(String(markdown || ""));
  target.innerHTML = window.DOMPurify.sanitize(parsedHtml, {
    USE_PROFILES: { html: true },
  });

  target.querySelectorAll("a[href]").forEach((link) => {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });
}

function removeLoadingMessage() {
  // Remove apenas o balão temporario criado enquanto aguardamos /api/chat.
  const loading = messagesEl.querySelector("[data-loading='true']");
  if (loading) {
    loading.remove();
  }
}

function setBusy(isBusy) {
  // Bloqueia novo envio durante a chamada para evitar duplicidade e corrida
  // entre historicos diferentes.
  inputEl.disabled = isBusy;
  sendButton.disabled = isBusy;
  statusEl.textContent = isBusy ? "Consultando o material de apoio..." : "";
}

function scrollToBottom() {
  // Mantem a experiencia de chat: novas mensagens sempre ficam visiveis.
  requestAnimationFrame(() => {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  });
}

function autoResizeInput() {
  // Textarea cresce com o conteudo ate um limite, preservando o layout mobile.
  inputEl.style.height = "auto";
  inputEl.style.height = `${Math.min(inputEl.scrollHeight, 144)}px`;
}

function clearChat() {
  // Limpa UI e contexto enviado ao RAG, mas nao remove configuracoes do app.
  messages = [
    {
      role: "assistant",
      content: welcomeMessage,
    },
  ];
  chatHistory = [];
  saveState();
  renderMessages();
  inputEl.focus();
}

async function submitMessage(event) {
  // Fluxo principal:
  // 1. mostra a pergunta imediatamente;
  // 2. envia pergunta + historico curto ao backend;
  // 3. renderiza resposta e salva o historico atualizado.
  event.preventDefault();

  const message = inputEl.value.trim();
  if (!message) {
    return;
  }

  messages.push({ role: "user", content: message });
  trimVisibleMessages();
  saveState();
  renderMessages();

  inputEl.value = "";
  autoResizeInput();
  setBusy(true);
  appendMessage(
    {
      role: "assistant",
      content: "Consultando",
    },
    { loading: true }
  );
  scrollToBottom();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history: chatHistory,
      }),
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Erro ao gerar resposta.");
    }

    const answer = payload.answer || "Informacao nao disponivel no material de apoio.";
    chatHistory = Array.isArray(payload.history) ? payload.history : chatHistory;
    messages.push({ role: "assistant", content: answer });
  } catch (error) {
    messages.push({
      role: "assistant",
      content:
        error.message ||
        "Nao consegui gerar a resposta agora. A equipe tecnica deve verificar os logs do Cloud Run.",
    });
  } finally {
    removeLoadingMessage();
    trimVisibleMessages();
    saveState();
    renderMessages();
    setBusy(false);
    inputEl.focus();
  }
}

inputEl.addEventListener("input", autoResizeInput);
inputEl.addEventListener("keydown", (event) => {
  // Enter envia; Shift+Enter quebra linha, comportamento comum em chats.
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});
formEl.addEventListener("submit", submitMessage);
clearButton.addEventListener("click", clearChat);

// Inicializacao da tela com o estado salvo da aba ou a mensagem de boas-vindas.
renderMessages();
autoResizeInput();
