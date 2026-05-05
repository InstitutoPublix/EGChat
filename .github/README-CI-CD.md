# CI/CD Pipeline Configuration

Pipelines configurados para deploy automático em Google Cloud.

## 🚀 Quick Start

### Option 1: Cloud Build (Recomendado para GCP nativo)

```bash
# Setup único (configura secrets e permissões)
./scripts/gcp-setup.sh

# Deploy via Cloud Build
gcloud builds submit --project=chattjce --config=cloudbuild.yaml
```

### Option 2: GitHub Actions (Recomendado para Git-driven)

```bash
# 1. Seguir instruções em .github/SETUP.md para WIF
# 2. Fazer push para main branch
# 3. Actions executa automaticamente
```

## 📋 Arquivos de Configuração

| Arquivo | Propósito | Trigger |
|---------|-----------|---------|
| `cloudbuild.yaml` | Google Cloud Build config | `gcloud builds submit` |
| `.github/workflows/deploy.yml` | GitHub Actions workflow | Push para `main` |
| `scripts/gcp-setup.sh` | Setup inicial (secrets + IAM) | Manual: `./scripts/gcp-setup.sh` |
| `.github/SETUP.md` | Documentação detalhada | Referência |

## 🔄 Fluxo de Deploy

### Cloud Build

```
gcloud builds submit
         ↓
    [1] Build Docker image
         ↓
    [2] Push para Artifact Registry
         ↓
    [3] Deploy para Cloud Run
         ↓
    Service rodando
```

### GitHub Actions

```
Push para main
     ↓
  [1] Build Docker image
     ↓
  [2] Push para Artifact Registry
     ↓
  [3] Deploy para Cloud Run
     ↓
  Service rodando
```

## 🔐 Secrets & Configuration

### Environment Variables (não-sensíveis)

Cloud Build (em `cloudbuild.yaml`):
```yaml
_REGION: southamerica-east1
_SERVICE_NAME: mentor-virtual-tjce
_QDRANT_URL: https://...
_QDRANT_COLLECTION: egchat_tjce
_CLAUDE_MODEL: claude-haiku-4-5-20251001
```

GitHub Actions (em `SETUP.md`):
```
QDRANT_URL
QDRANT_COLLECTION
CLAUDE_MODEL
```

### Secret Manager

Criados automaticamente por `scripts/gcp-setup.sh`:
- `openai-api-key`
- `claude-api-key`
- `qdrant-api-key`

## 📊 Monitorar Builds

### Cloud Build

```bash
# Listar builds
gcloud builds list --project=chattjce

# Ver logs
gcloud builds log BUILD_ID --project=chattjce

# Aguardar conclusão
gcloud builds log BUILD_ID --stream --project=chattjce
```

### GitHub Actions

```bash
# Listar runs
gh run list --workflow=deploy.yml

# Ver detalhes
gh run view RUN_ID --log

# Aguardar conclusão
gh run watch RUN_ID
```

## ✅ Checklist de Deploy

- [ ] `.env` configurado com chaves de API
- [ ] `gcloud` instalado e autenticado
- [ ] Projeto GCP criado (chattjce)
- [ ] `./scripts/gcp-setup.sh` executado
- [ ] Secrets criados no Secret Manager
- [ ] Service Account com permissões corretas
- [ ] GitHub secrets configurados (se usando Actions)

## 🐛 Troubleshooting

### Build falha com "Permission denied on secret"

```bash
# Conceder permissão
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:mentor-virtual-tjce-run-sa@chattjce.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=chattjce
```

### Cloud Run não consegue iniciar

```bash
# Ver detalhes do erro
gcloud run services describe mentor-virtual-tjce \
  --region=southamerica-east1 \
  --platform=managed \
  --project=chattjce --format=json | jq '.status'
```

### GitHub Actions falha com autenticação

Verificar `WIF_PROVIDER` e `WIF_SERVICE_ACCOUNT` em `.github/SETUP.md`

## 📝 Customização

### Mudar região

```bash
# Em cloudbuild.yaml
_REGION: us-central1

# Em .github/workflows/deploy.yml
REGION: us-central1
```

### Mudar limites de recursos

```yaml
# Em cloudbuild.yaml
Cloud Run args:
  --memory=1Gi        # alterar memória
  --cpu=2             # alterar CPU
  --max-instances=5   # alterar limite
```

## 🔗 Links Úteis

- [Build Status](https://console.cloud.google.com/cloud-build/builds?project=chattjce)
- [Cloud Run Services](https://console.cloud.google.com/run?project=chattjce)
- [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=chattjce)
- [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts?project=chattjce)
- [GitHub Actions Runs](https://github.com/seu-usuario/EGChat/actions)
