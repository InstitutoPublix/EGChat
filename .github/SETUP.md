# CI/CD Setup Guide

Este guia descreve como configurar a integração contínua e o deploy automático para Google Cloud.

## 📋 Índice

1. [Google Cloud Setup](#google-cloud-setup)
2. [GitHub Secrets](#github-secrets)
3. [GitHub Actions](#github-actions)
4. [Cloud Build](#cloud-build)

---

## Google Cloud Setup

### 1. Executar script de configuração

O script `scripts/gcp-setup.sh` configura automaticamente:
- Secrets no Secret Manager
- Service Accounts
- Permissões IAM

```bash
# Navegar até o diretório do projeto
cd /path/to/EGChat

# Executar o script (usa valores default)
./scripts/gcp-setup.sh

# Ou com parâmetros customizados
./scripts/gcp-setup.sh [PROJECT_ID] [REGION] [SERVICE_NAME]
```

**Requisitos:**
- Google Cloud CLI (`gcloud`) instalado
- Arquivo `.env` com variáveis de API
- Autenticado com `gcloud auth login`

### 2. O que o script faz

```
✓ Cria/atualiza secrets no Secret Manager:
  - openai-api-key
  - claude-api-key
  - qdrant-api-key

✓ Cria service account (se não existir):
  - mentor-virtual-tjce-run-sa

✓ Configura permissões IAM:
  - Cloud Build → Cloud Run Admin
  - Cloud Build → Artifact Registry Writer
  - Cloud Build → pode impersonar Runtime SA
  - Runtime SA → pode acessar secrets
```

---

## GitHub Secrets

Para usar GitHub Actions, configure estes secrets no repositório:

**Acesso:** Settings → Secrets and variables → Actions → New repository secret

### Variáveis de Ambiente (não-sensíveis)

Crie estas como variáveis de repositório:

- `QDRANT_URL`: URL da instância Qdrant
- `QDRANT_COLLECTION`: Nome da collection
- `CLAUDE_MODEL`: Modelo Claude a usar

### Workload Identity Federation (WIF)

Para autenticação sem credenciais de longa duração:

```bash
# 1. Criar Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project=$PROJECT_ID \
  --location=global \
  --display-name="GitHub Actions"

# 2. Criar Workload Identity Provider
gcloud iam workload-identity-providers create-oidc "github-provider" \
  --project=$PROJECT_ID \
  --location=global \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.aud=assertion.aud,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --workload-identity-pool="github-pool"

# 3. Criar Service Account para GitHub
gcloud iam service-accounts create "github-actions" \
  --project=$PROJECT_ID \
  --display-name="GitHub Actions"

# 4. Vincular WIF ao Service Account
gcloud iam service-accounts add-iam-policy-binding \
  "github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/seu-usuario/seu-repositorio"

# 5. Conceder permissões necessárias
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud iam service-accounts add-iam-policy-binding \
  "mentor-virtual-tjce-run-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --project=$PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# 6. Adicionar secrets ao GitHub
WIF_PROVIDER=$(gcloud iam workload-identity-providers describe "github-provider" \
  --project=$PROJECT_ID \
  --location=global \
  --format='value(name)')

gh secret set WIF_PROVIDER --body "$WIF_PROVIDER"
gh secret set WIF_SERVICE_ACCOUNT --body "github-actions@$PROJECT_ID.iam.gserviceaccount.com"
```

### Alternativa: Service Account Key (menos seguro)

Se não puder usar WIF:

```bash
# 1. Criar Service Account
gcloud iam service-accounts create github-actions \
  --project=$PROJECT_ID

# 2. Criar chave
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --project=$PROJECT_ID

# 3. Adicionar como secret
gh secret set GCP_SA_KEY < key.json

# 4. Remover arquivo localmente
rm key.json

# 5. Adicionar permissões
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
```

---

## GitHub Actions

### Configuração do Workflow

O arquivo `.github/workflows/deploy.yml` já está configurado.

**Triggers:**
- ✅ Push para `main`
- ✅ Dispatch manual (Actions → Deploy)

**O que faz:**
1. Checkout do código
2. Autenticação com Google Cloud (WIF)
3. Build da imagem Docker
4. Push para Artifact Registry
5. Deploy para Cloud Run
6. Output da URL do serviço

### Executar manualmente

```bash
# Via GitHub CLI
gh workflow run deploy.yml

# Ou via interface: Actions → Build and Deploy → Run workflow
```

### Monitorar execução

```bash
# Ver últimos runs
gh run list --workflow=deploy.yml

# Ver detalhes de um run
gh run view <RUN_ID> --log

# Aguardar conclusão
gh run watch <RUN_ID>
```

---

## Cloud Build

### Setup

```bash
# Executar script de setup
./scripts/gcp-setup.sh

# Ou manualmente via gcloud
gcloud builds submit --project=chattjce --config=cloudbuild.yaml
```

### Monitorar builds

```bash
# Listar builds
gcloud builds list --project=$PROJECT_ID

# Ver detalhes
gcloud builds describe BUILD_ID --project=$PROJECT_ID

# Ver logs
gcloud builds log BUILD_ID --project=$PROJECT_ID

# Aguardar build
gcloud builds log BUILD_ID --stream --project=$PROJECT_ID
```

### Disparar manualmente

```bash
gcloud builds submit \
  --project=$PROJECT_ID \
  --config=cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=mentor-virtual-tjce
```

---

## Troubleshooting

### "Permission denied on secret"

Service account não tem acesso aos secrets:

```bash
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:mentor-virtual-tjce-run-sa@chattjce.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=chattjce
```

### "Failed to create revision"

Verificar logs do Cloud Run:

```bash
gcloud run services describe mentor-virtual-tjce \
  --region=southamerica-east1 \
  --platform=managed \
  --format=json \
  --project=chattjce | jq '.status'
```

### Build trava ou timeout

Aumentar tempo de build em `cloudbuild.yaml`:

```yaml
timeout: 1800s  # 30 minutos
```

---

## Referências

- [Google Cloud Build Docs](https://cloud.google.com/build/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Google Workload Identity Federation](https://cloud.google.com/docs/authentication/workload-identity-federation)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
