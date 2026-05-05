#!/bin/bash
set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ID="chattjce"
REGION="southamerica-east1"
SERVICE_NAME="mentor-virtual-tjce"

echo -e "${YELLOW}🔧 Configurando secrets e permissões no Google Cloud...${NC}"

# 1. Verificar se gcloud está disponível
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI não encontrado. Instale em: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# 2. Definir projeto
echo -e "${YELLOW}📝 Definindo projeto como: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# 3. Ler variáveis do .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    exit 1
fi

OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2- | tr -d '\r')
CLAUDE_API_KEY=$(grep CLAUDE_API_KEY .env | cut -d= -f2- | tr -d '\r')
QDRANT_API_KEY=$(grep QDRANT_API_KEY .env | cut -d= -f2- | tr -d '\r')

if [ -z "$OPENAI_API_KEY" ] || [ -z "$CLAUDE_API_KEY" ] || [ -z "$QDRANT_API_KEY" ]; then
    echo -e "${RED}❌ Variáveis de API não encontradas no .env${NC}"
    exit 1
fi

# 4. Criar secrets no Secret Manager
echo -e "${YELLOW}🔐 Criando secrets no Secret Manager...${NC}"

create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2

    if gcloud secrets describe $secret_name --project=$PROJECT_ID &>/dev/null; then
        echo "  ✓ Atualizando $secret_name"
        echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=- --project=$PROJECT_ID > /dev/null
    else
        echo "  ✓ Criando $secret_name"
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=- --project=$PROJECT_ID --replication-policy="automatic" > /dev/null
    fi
}

create_or_update_secret "openai-api-key" "$OPENAI_API_KEY"
create_or_update_secret "claude-api-key" "$CLAUDE_API_KEY"
create_or_update_secret "qdrant-api-key" "$QDRANT_API_KEY"

# 5. Obter o service account do Cloud Build
CLOUD_BUILD_SA=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com

# 6. Obter ou criar o service account do Cloud Run
RUNTIME_SA="mentor-virtual-tjce-run-sa"
RUNTIME_SA_EMAIL="${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${YELLOW}👤 Verificando service account do Cloud Run...${NC}"

if ! gcloud iam service-accounts describe $RUNTIME_SA_EMAIL --project=$PROJECT_ID &>/dev/null; then
    echo "  ✓ Criando $RUNTIME_SA_EMAIL"
    gcloud iam service-accounts create $RUNTIME_SA \
        --display-name="Service Account para Cloud Run - Mentor Virtual" \
        --project=$PROJECT_ID
else
    echo "  ✓ $RUNTIME_SA_EMAIL já existe"
fi

# 7. Configurar permissões para Cloud Build
echo -e "${YELLOW}🔑 Configurando permissões para Cloud Build...${NC}"

# Permissão para criar Cloud Run services
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/run.admin" \
    --condition=None \
    2>/dev/null || true
echo "  ✓ Cloud Build com permissão run.admin"

# Permissão para push em Artifact Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/artifactregistry.writer" \
    --condition=None \
    2>/dev/null || true
echo "  ✓ Cloud Build com permissão artifactregistry.writer"

# Permissão para usar o service account do Cloud Run
gcloud iam service-accounts add-iam-policy-binding $RUNTIME_SA_EMAIL \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/iam.serviceAccountUser" \
    --project=$PROJECT_ID \
    --condition=None \
    2>/dev/null || true
echo "  ✓ Cloud Build pode impersonar Cloud Run service account"

# 8. Configurar permissões para Cloud Run acessar secrets
echo -e "${YELLOW}🔐 Configurando permissões para Cloud Run acessar secrets...${NC}"

for secret in "openai-api-key" "claude-api-key" "qdrant-api-key"; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID \
        --condition=None \
        2>/dev/null || true
done
echo "  ✓ Cloud Run pode acessar todos os secrets"

# 9. Resumo
echo -e "${GREEN}✅ Configuração concluída!${NC}"
echo ""
echo "Resumo:"
echo "  📁 Projeto: $PROJECT_ID"
echo "  🔐 Secrets criados/atualizados:"
echo "     - openai-api-key"
echo "     - claude-api-key"
echo "     - qdrant-api-key"
echo "  👤 Service Account (Cloud Run): $RUNTIME_SA_EMAIL"
echo "  🔧 Service Account (Cloud Build): $CLOUD_BUILD_SA"
echo ""
echo -e "${YELLOW}Próximo passo:${NC}"
echo "  gcloud builds submit --project=$PROJECT_ID --config=cloudbuild.yaml"
