#!/bin/bash
set -e

# Configurações
# Defaults
PROJECT_ID="${1:-chattjce}"
REGION="${2:-southamerica-east1}"
SERVICE_NAME="mentor-virtual-tjce"
REPOSITORY="cloud-run-source-deploy"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}"
# Nota: o script usa 'chattjce' e 'southamerica-east1' por padrão

echo "   Iniciando deploy do mentor-virtual-tjce no Cloud Run"
echo "   Projeto: $PROJECT_ID"
echo "   Região: $REGION"
echo "   Serviço: $SERVICE_NAME"
echo "   Imagem: $IMAGE_NAME"

echo -e "\n Garantindo APIs necessárias..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT_ID"

echo -e "\n Verificando se o repositório Artifact Registry existe..."
if ! gcloud artifacts repositories describe "$REPOSITORY" \
    --project="$PROJECT_ID" \
    --location="$REGION" >/dev/null 2>&1; then
    echo "   Criando repositório $REPOSITORY em $REGION..."
    gcloud artifacts repositories create "$REPOSITORY" \
        --project="$PROJECT_ID" \
        --location="$REGION" \
        --repository-format=docker \
        --description="Imagens Docker do Cloud Run"
fi

echo -e "\n Construindo a imagem Docker..."
gcloud builds submit \
    --project="$PROJECT_ID" \
    --config=cloudbuild.yaml

echo -e "\n✅ Deploy concluído!"
echo -e "\n Configurações de custo:"
echo "   - Memory: 512Mi (mínimo recomendado)"
echo "   - CPU: 1 vCPU (padrão)"
echo "   - Max instances: 1 (teto de custo baixo)"
echo "   - Min instances: 0 (sem custo em idle)"
echo "   - Timeout: 5 minutos"
echo -e "\n Acessar: gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'"

# --- Exemplo: deploy manual sem usar cloudbuild (útil para testes locais)
echo -e "\n🔁 Para deploy manual (sem Cloud Build), execute:"
cat <<'CMD'
gcloud run deploy $SERVICE_NAME \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/mentor-virtual-tjce:latest \
    --region $REGION \
    --platform managed \
    --memory 512Mi --cpu 1 \
    --cpu-throttling \
    --timeout 300 \
    --min-instances 0 --max-instances 1 \
    --allow-unauthenticated \
    --set-env-vars QDRANT_URL=https://847e925b-b8a7-400e-92c4-c15fba8de03f.sa-east-1-0.aws.cloud.qdrant.io,QDRANT_COLLECTION=egchat_tjce,CLAUDE_MODEL=claude-haiku-4-5-20251001,PYTHONUNBUFFERED=1 \
    --set-secrets OPENAI_API_KEY=openai-api-key:latest,CLAUDE_API_KEY=claude-api-key:latest,QDRANT_API_KEY=qdrant-api-key:latest \
    --service-account mentor-virtual-tjce-run-sa@$PROJECT_ID.iam.gserviceaccount.com
CMD
