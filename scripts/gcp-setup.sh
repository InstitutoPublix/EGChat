#!/bin/bash
set -euo pipefail

# GCP Setup Script - Configuração de Secrets e IAM
# Uso: ./scripts/gcp-setup.sh [PROJECT_ID] [REGION] [SERVICE_NAME]

PROJECT_ID="${1:-chattjce}"
REGION="${2:-southamerica-east1}"
SERVICE_NAME="${3:-mentor-virtual-tjce}"
RUNTIME_SA="${SERVICE_NAME}-run-sa"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
log_ok() { echo -e "${GREEN}✓ $1${NC}"; }
log_error() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# Validar gcloud
if ! command -v gcloud &>/dev/null; then
    log_error "gcloud CLI não encontrado. Instale: https://cloud.google.com/sdk/docs/install"
fi

# Validar .env
if [ ! -f .env ]; then
    log_error "Arquivo .env não encontrado no diretório atual"
fi

log_info "Configurando GCP para ${SERVICE_NAME} no projeto ${PROJECT_ID}"
log_info "Região: ${REGION}"

# Definir projeto
gcloud config set project "$PROJECT_ID" --quiet
log_ok "Projeto definido como ${PROJECT_ID}"

# Ler variáveis do .env
OPENAI_API_KEY=$(grep -oP '(?<=OPENAI_API_KEY=).*' .env | head -1 || true)
CLAUDE_API_KEY=$(grep -oP '(?<=CLAUDE_API_KEY=).*' .env | head -1 || true)
QDRANT_API_KEY=$(grep -oP '(?<=QDRANT_API_KEY=).*' .env | head -1 || true)

if [ -z "$OPENAI_API_KEY" ] || [ -z "$CLAUDE_API_KEY" ] || [ -z "$QDRANT_API_KEY" ]; then
    log_error "Variáveis de API não encontradas no .env"
fi

# Criar/atualizar secrets
log_info "Configurando secrets no Secret Manager"

for secret_name in openai-api-key claude-api-key qdrant-api-key; do
    secret_var="${secret_name//-/_}"
    secret_var="${secret_var^^}"
    secret_value="${!secret_var:-}"

    if [ -z "$secret_value" ]; then
        log_error "Variável $secret_var não encontrada"
    fi

    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=- --project="$PROJECT_ID" >/dev/null
        log_ok "Secret $secret_name atualizado"
    else
        echo -n "$secret_value" | gcloud secrets create "$secret_name" --data-file=- --project="$PROJECT_ID" --replication-policy=automatic >/dev/null
        log_ok "Secret $secret_name criado"
    fi
done

# Service accounts
CLOUD_BUILD_SA=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')@cloudbuild.gserviceaccount.com
RUNTIME_SA_EMAIL="${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

log_info "Configurando service accounts"

if ! gcloud iam service-accounts describe "$RUNTIME_SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    gcloud iam service-accounts create "$RUNTIME_SA" \
        --display-name="Service Account para Cloud Run - ${SERVICE_NAME}" \
        --project="$PROJECT_ID" >/dev/null
    log_ok "Service account $RUNTIME_SA_EMAIL criado"
else
    log_ok "Service account $RUNTIME_SA_EMAIL já existe"
fi

# Permissões IAM
log_info "Configurando permissões IAM"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/run.admin" \
    --quiet 2>/dev/null || true
log_ok "Cloud Build: roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/artifactregistry.writer" \
    --quiet 2>/dev/null || true
log_ok "Cloud Build: roles/artifactregistry.writer"

gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA_EMAIL" \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --project="$PROJECT_ID" \
    --quiet 2>/dev/null || true
log_ok "Cloud Build pode impersonar Runtime SA"

# Permissões para acessar secrets
log_info "Configurando acesso a secrets para Cloud Run"

for secret_name in openai-api-key claude-api-key qdrant-api-key; do
    gcloud secrets add-iam-policy-binding "$secret_name" \
        --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
        --role="roles/secretmanager.secretAccessor" \
        --project="$PROJECT_ID" \
        --quiet 2>/dev/null || true
done
log_ok "Cloud Run pode acessar todos os secrets"

# Resumo
echo ""
echo -e "${GREEN}✅ Configuração concluída!${NC}"
echo ""
echo "📋 Resumo da configuração:"
echo "  Projeto: $PROJECT_ID"
echo "  Região: $REGION"
echo "  Service: $SERVICE_NAME"
echo ""
echo "🔐 Secrets:"
echo "  - openai-api-key"
echo "  - claude-api-key"
echo "  - qdrant-api-key"
echo ""
echo "👤 Service Accounts:"
echo "  Runtime: $RUNTIME_SA_EMAIL"
echo "  Cloud Build: $CLOUD_BUILD_SA"
echo ""
echo "📝 Próximos passos:"
echo "  1. Cloud Build: gcloud builds submit --project=$PROJECT_ID --config=cloudbuild.yaml"
echo "  2. GitHub: Configurar secrets de Actions (veja .github/SETUP.md)"
