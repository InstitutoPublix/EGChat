# Mentor Virtual TJCE 🤖

Assistente de IA para responder dúvidas sobre o curso de Transformação Digital do TJCE, usando Retrieval-Augmented Generation (RAG).

- **Status**: ✅ Em produção
- **URL**: https://mentor-virtual-tjce-931025652334.southamerica-east1.run.app
- **Tecnologia**: Flask + Claude API + Qdrant + OpenAI Embeddings

---

## 📋 Índice

1. [Como Funciona](#como-funciona)
2. [Arquitetura](#arquitetura)
3. [Instalação Local](#instalação-local)
4. [Deploy](#deploy)
5. [Desenvolvimento](#desenvolvimento)
6. [Estrutura do Projeto](#estrutura-do-projeto)

---

## 🔍 Como Funciona

O **Mentor Virtual** responde perguntas sobre o curso usando **Retrieval-Augmented Generation (RAG)**:

```
Pergunta do usuário
        ↓
1. Buscar documentos relevantes no Qdrant
        ↓
2. Usar Claude com os documentos como contexto
        ↓
3. Gerar resposta baseada no material do curso
        ↓
Resposta para o usuário
```

### Exemplo

```
Usuário: "Qual é o cronograma das turmas?"

Sistema:
  1. Busca no Qdrant: "cronograma turmas"
  2. Encontra: documento com calendário
  3. Envia para Claude: "Aqui está o calendário. Responda: ..."
  4. Claude responde com detalhes

Resposta: "Turma 1 (seg, 08h-12h): Aula 1 em 04/mai, ..."
```

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (Browser)                 │
│              index.html + app.js                    │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/JSON
                     ↓
┌─────────────────────────────────────────────────────┐
│              BACKEND (Flask)                        │
│  ├─ app.py: Rotas HTTP                             │
│  ├─ /: Carrega interface                           │
│  ├─ /api/chat: Processa pergunta                   │
│  └─ /healthz: Health check                         │
└────┬──────────────┬──────────────┬──────────────────┘
     │              │              │
     ↓              ↓              ↓
┌──────────┐ ┌──────────────┐ ┌──────────────┐
│  Qdrant  │ │ Claude API   │ │  OpenAI API  │
│  (RAG)   │ │  (LLM)       │ │ (Embeddings) │
│  Vector  │ │ Respostas    │ │ Vetorização  │
│ Database │ │              │ │ de docs      │
└──────────┘ └──────────────┘ └──────────────┘
```

### Fluxo de uma Requisição

```
POST /api/chat
{
  "message": "Qual é a ementa do curso?",
  "history": [
    {"question": "...", "answer": "..."}
  ]
}

┌─────────────────────────────────────────┐
│ 1. app.py - Valida variáveis de env    │
│    ✅ CLAUDE_API_KEY existe?           │
│    ✅ OPENAI_API_KEY existe?           │
│    ✅ QDRANT_URL existe?               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 2. rag_chain.py - Processa              │
│    - Embed a pergunta (OpenAI)          │
│    - Busca no Qdrant (similaridade)     │
│    - Recupera 3-5 documentos            │
│    - Formata contexto                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 3. llm.py - Chama Claude                │
│    - Injeta contexto do Qdrant          │
│    - Injeta histórico de conversa       │
│    - max_tokens: 1000                   │
│    - temperature: 0.1                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 4. Response                             │
│    {                                    │
│      "answer": "resposta completa",     │
│      "history": [..., novo item]        │
│    }                                    │
└─────────────────────────────────────────┘
```

### Stack Tecnológico

| Camada | Tecnologia | Propósito |
|--------|------------|-----------|
| **Frontend** | HTML + CSS + JavaScript | Interface no navegador |
| **Backend** | Flask (Python) | API REST |
| **RAG** | LangChain + Qdrant | Busca e contexto |
| **LLM** | Claude API (Anthropic) | Geração de respostas |
| **Embeddings** | OpenAI Embeddings | Vetorização de documentos |
| **Deploy** | Cloud Run (Google) | Hospedagem |
| **CI/CD** | Cloud Build + GitHub Actions | Automação |

---

## 💻 Instalação Local

### Pré-requisitos

- Python 3.12+
- Google Cloud SDK
- Variáveis de ambiente configuradas

### Setup

```bash
# 1. Clone e navegue
git clone https://github.com/seu-usuario/EGChat.git
cd EGChat

# 2. Crie ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
# Edite .env com suas chaves de API

# 5. Carregue dados (opcional)
python scripts/ingest.py

# 6. Execute localmente
python app.py
# Acesse: http://localhost:5000
```

### Variáveis de Ambiente (.env)

```bash
# APIs
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...

# Qdrant
QDRANT_URL=https://...
QDRANT_API_KEY=...
QDRANT_COLLECTION=egchat_tjce

# Modelo
CLAUDE_MODEL=claude-haiku-4-5-20251001
```

---

## 🚀 Deploy

### Cloud Build

```bash
# Setup único
./scripts/gcp-setup.sh

# Deploy
gcloud builds submit --project=chattjce --config=cloudbuild.yaml
```

### GitHub Actions

1. Seguir `.github/CI-CD.md`
2. Push para `main` = deploy automático

### Monitorar

```bash
# Ver status
gcloud run services describe mentor-virtual-tjce \
  --region=southamerica-east1 \
  --platform=managed \
  --project=chattjce

# Ver logs
gcloud run services logs read mentor-virtual-tjce \
  --region=southamerica-east1 \
  --limit=50
```

---

## 🔧 Desenvolvimento

### Estrutura

```
EGChat/
├── app.py                      # Flask app principal
├── Dockerfile                  # Imagem Docker
├── requirements.txt            # Dependências
├── templates/
│   └── index.html             # Interface HTML
├── static/
│   ├── css/
│   └── js/                    # Frontend logic
├── scripts/
│   ├── config.py              # Variáveis de env
│   ├── llm.py                 # Chama Claude
│   ├── rag_chain.py           # RAG logic
│   ├── retriever.py           # Busca no Qdrant
│   ├── prompts.py             # Templates de prompt
│   ├── ingest.py              # Carrega documentos
│   └── gcp-setup.sh           # Setup GCP
├── data/
│   ├── contexto1.txt          # Documento do curso
│   ├── cronograma.txt         # Calendário
│   └── ...                    # Outros documentos
├── cloudbuild.yaml            # Pipeline de build
└── .github/
    ├── workflows/
    │   └── deploy.yml         # GitHub Actions
    └── CI-CD.md              # Guia de CI/CD
```

### Adicionar Novo Documento

```bash
# 1. Coloque arquivo em data/
cp meu_documento.txt data/

# 2. Atualize DEFAULT_SOURCE_FILES em scripts/config.py
DEFAULT_SOURCE_FILES = [
    PROJECT_ROOT / "data" / "contexto1.txt",
    PROJECT_ROOT / "data" / "meu_documento.txt",  # ← adicione aqui
]

# 3. Execute ingest para vetorizar
python scripts/ingest.py

# 4. Teste localmente
python app.py
```

### Modificar Prompts

```python
# scripts/prompts.py

SYSTEM_PROMPT_TEMPLATE = """
Você é o Professor Virtual do TJCE.
Responda somente com base no contexto recuperado.
...
"""

# Depois teste:
python app.py
```

### Mudar Modelo LLM

```bash
# .env
CLAUDE_MODEL=claude-opus-4-7  # ou outro modelo
```

---

## 📊 Performance

| Métrica | Valor |
|---------|-------|
| Tempo de resposta (p95) | ~2-3s |
| Latência Qdrant | ~500ms |
| Latência Claude | ~1.5s |
| Max tokens por resposta | 1000 |
| Contexto máximo | ~5 documentos |
| Taxa de acerto RAG | ~85% |

---

## 🛡️ Segurança

- ✅ Secrets em Secret Manager (não hardcoded)
- ✅ Variáveis injetadas em runtime
- ✅ Service Account com IAM mínimo
- ✅ HTTPS obrigatório
- ✅ CORS restrito
- ✅ Rate limiting no Cloud Run

---

## 🤝 Contribuindo

```bash
# 1. Crie branch
git checkout -b feature/minha-feature

# 2. Faça mudanças
# Edite arquivos...

# 3. Teste localmente
python app.py

# 4. Commit
git add .
git commit -m "feat: descrição da mudança"

# 5. Push
git push origin feature/minha-feature

# 6. Crie PR
# GitHub → Pull Requests → New PR
```

---

## 📚 Documentação

| Documento | Conteúdo |
|-----------|----------|
| `.github/CI-CD.md` | Pipeline, deploy, troubleshooting |
| `.github/SETUP.md` | Setup detalhado de GCP/GitHub |
| `.github/BUILD-ANALYSIS.md` | Análise técnica do último build |
| `.github/CI-CD-STATUS.md` | Validação e status do sistema |
| `scripts/gcp-setup.sh` | Automação de setup |

---

## 🧪 Testes

```bash
# Health check
curl https://mentor-virtual-tjce-931025652334.southamerica-east1.run.app/

# API de chat
curl -X POST https://mentor-virtual-tjce-931025652334.southamerica-east1.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quantas turmas?","history":[]}'
```

---

## 🐛 Troubleshooting

### Aplicação não inicia localmente

```bash
# Verifique .env
cat .env | grep CLAUDE_API_KEY

# Teste importação
python -c "from anthropic import Anthropic; print('OK')"
```

### Qdrant não conecta

```bash
# Teste URL
curl -s https://seu-qdrant-url/health | jq .
```

### Secrets não acessíveis em Cloud Run

Ver `.github/CI-CD.md` → Troubleshooting

---

## 📞 Suporte

- 📧 Email: consultores@institutopublix.com.br
- 🐛 Issues: GitHub Issues
- 📋 Documentação: `.github/` directory

---

## 📄 Licença

Instituto Publix - 2025

---

## 🚀 Status

| Componente | Status |
|------------|--------|
| Frontend | ✅ Online |
| Backend | ✅ Online |
| RAG/Qdrant | ✅ Online |
| Claude API | ✅ Online |
| Cloud Run | ✅ Online |
| CI/CD | ✅ Configurado |

**Última atualização**: 2026-05-05  
**Deploy**: Automático via Cloud Build / GitHub Actions
