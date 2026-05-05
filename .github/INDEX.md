# 📋 Índice de Documentação

Guia rápido para navegar pela documentação do Mentor Virtual TJCE.

---

## 🎯 Por Caso de Uso

### "Quero começar do zero"
1. Leia: [README.md](/README.md) - Visão geral
2. Veja: [Como Funciona](/README.md#como-funciona)
3. Siga: [Instalação Local](/README.md#instalação-local)

### "Quero fazer deploy"
1. Rápido: [.github/CI-CD.md](/CI-CD.md) - Quick Start
2. Detalhes: [README.md → Deploy](/README.md#deploy)
3. Troubleshooting: [CI-CD.md → Troubleshooting](/CI-CD.md#troubleshooting)

### "Estou desenvolvendo uma feature"
1. Entenda: [README.md → Arquitetura](/README.md#arquitetura)
2. Siga: [README.md → Desenvolvimento](/README.md#desenvolvimento)
3. Configure: [Setup local](/README.md#instalação-local)

### "Preciso monitorar / troubleshoot"
1. Ver status: [CI-CD.md → Monitorar](/CI-CD.md#monitorar)
2. Resolver: [CI-CD.md → Troubleshooting](/CI-CD.md#troubleshooting)
3. Logs: [CI-CD.md → Cloud Run Logs](/CI-CD.md#cloud-run)

### "Quero entender a arquitetura"
1. Visão geral: [README.md → Arquitetura](/README.md#arquitetura)
2. Stack: [README.md → Stack Tecnológico](/README.md#stack-tecnológico)
3. Fluxo: [README.md → Fluxo de uma Requisição](/README.md#fluxo-de-uma-requisição)

---

## 🔗 Documentação por Componente

### Frontend
- Arquivos: `templates/`, `static/`
- Documentação: [README.md → Arquitetura](/README.md#componentes-principais)
- Setup: [README.md → Instalação Local](/README.md#instalação-local)

### Backend (Flask)
- Arquivo: `app.py`
- Documentação: [README.md → Fluxo de uma Requisição](/README.md#fluxo-de-uma-requisição)
- Setup: [README.md → Instalação Local](/README.md#instalação-local)

### RAG (LangChain + Qdrant)
- Arquivos: `scripts/rag_chain.py`, `scripts/retriever.py`
- Documentação: [README.md → Como Funciona](/README.md#como-funciona)
- Setup: [README.md → Instalação Local](/README.md#instalação-local)

### LLM (Claude API)
- Arquivo: `scripts/llm.py`
- Documentação: [README.md → Arquitetura](/README.md#stack-tecnológico)
- Setup: [README.md → Variáveis de Ambiente](/README.md#variáveis-de-ambiente-env)

### Embeddings (OpenAI)
- Arquivo: `scripts/vectorstore.py`
- Documentação: [README.md → Stack Tecnológico](/README.md#stack-tecnológico)
- Setup: [README.md → Variáveis de Ambiente](/README.md#variáveis-de-ambiente-env)

### Ingestão de Dados
- Arquivo: `scripts/ingest.py`
- Documentação: [README.md → Adicionar Novo Documento](/README.md#adicionar-novo-documento)
- Dados: `data/`

### CI/CD & Deploy
- Arquivos: `cloudbuild.yaml`, `.github/workflows/deploy.yml`
- Documentação: **[CI-CD.md](CI-CD.md)** - Documento principal
- Setup: [CI-CD.md → Quick Start](/CI-CD.md#quick-start)

---

## 📄 Arquivos Principais

| Arquivo | Propósito | Leia Quando... |
|---------|-----------|-------------------|
| [README.md](/README.md) | Documentação geral do projeto | Quer entender tudo |
| [.github/CI-CD.md](/CI-CD.md) | Documentação de deploy/ops | Precisa fazer deploy ou troubleshoot |
| [.github/workflows/deploy.yml](/workflows/deploy.yml) | GitHub Actions workflow | Configurando GitHub Actions |
| [cloudbuild.yaml](/cloudbuild.yaml) | Cloud Build config | Usando Cloud Build |
| [Dockerfile](/Dockerfile) | Imagem Docker | Entendendo build |
| [scripts/gcp-setup.sh](/scripts/gcp-setup.sh) | Setup automático de secrets | Setup inicial ou troubleshoot |

---

## 🚀 Links Úteis

### Documentação
- [README.md](/README.md) - Overview do projeto
- [CI-CD.md](/CI-CD.md) - Guia de deploy
- Este arquivo - Índice

### Produção
- [Aplicação](https://mentor-virtual-tjce-931025652334.southamerica-east1.run.app)
- [Cloud Build](https://console.cloud.google.com/cloud-build/builds?project=chattjce)
- [Cloud Run](https://console.cloud.google.com/run?project=chattjce)
- [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=chattjce)

### Código
- [app.py](/app.py) - Flask app
- [scripts/rag_chain.py](/scripts/rag_chain.py) - RAG logic
- [scripts/llm.py](/scripts/llm.py) - Claude integration
- [scripts/config.py](/scripts/config.py) - Configuração

---

## ❓ FAQ Rápido

**P: Onde começo?**  
R: [README.md](/README.md)

**P: Como faço deploy?**  
R: [CI-CD.md → Quick Start](/CI-CD.md#quick-start)

**P: Secrets não funcionam**  
R: [CI-CD.md → Troubleshooting](/CI-CD.md#troubleshooting)

**P: Quero adicionar um documento para o RAG**  
R: [README.md → Adicionar Novo Documento](/README.md#adicionar-novo-documento)

**P: Como monitoro a aplicação?**  
R: [CI-CD.md → Monitorar](/CI-CD.md#-monitorar)

**P: Qual é a arquitetura?**  
R: [README.md → Arquitetura](/README.md#-arquitetura)

**P: Preciso de ajuda!**  
R: [README.md → Suporte](/README.md#-suporte) ou [CI-CD.md → Troubleshooting](/CI-CD.md#-troubleshooting)

---

## 📊 Estrutura de Documentação

```
EGChat/
├── README.md                    ← COMECE AQUI
├── .github/
│   ├── CI-CD.md                 ← Deploy & Ops
│   ├── INDEX.md                 ← Este arquivo
│   └── workflows/
│       └── deploy.yml           ← GitHub Actions
├── cloudbuild.yaml              ← Cloud Build
├── Dockerfile                   ← Build Docker
└── scripts/
    └── gcp-setup.sh             ← Setup automático
```

---

**Última atualização**: 2026-05-05  
**Versão**: 1.0
