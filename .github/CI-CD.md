# CI/CD & Deploy — Síntese

Este README reúne tudo o que você precisa saber sobre o CI/CD e o deploy do projeto, compilado a partir dos arquivos em `.github/` e dos scripts de automação.

**Resumo rápido**
- Pipeline principal: 5 steps (criação/verificação do Artifact Registry → build da imagem → push com SHA → push `latest` → deploy no Cloud Run).
- Métodos de deploy suportados: Cloud Build (recomendado) e GitHub Actions (via Workload Identity Federation).
- Secrets: `openai-api-key`, `claude-api-key`, `qdrant-api-key` (Secret Manager). O script `scripts/gcp-setup.sh` cria/atualiza esses secrets e configura as service accounts.
- URL de produção conhecida: https://mentor-virtual-tjce-931025652334.southamerica-east1.run.app

**Quick start (recomendado)**

1. Pré-requisitos: `gcloud`, `docker`, `gh` (opcional), e um arquivo `.env` com as chaves `OPENAI_API_KEY`, `CLAUDE_API_KEY`, `QDRANT_API_KEY`.
2. Rodar o setup que cria secrets e SAs:

```bash
./scripts/gcp-setup.sh
```

3. Deploy via Cloud Build:

```bash
gcloud builds submit --project=chattjce --config=cloudbuild.yaml
```

4. (Opcional) Usar GitHub Actions: siga `.github/SETUP.md` para configurar Workload Identity Federation (WIF). Push para `main` dispara o workflow `.github/workflows/deploy.yml`.

**Pipeline (resumo dos passos)**

1. ensure-artifact-registry — garante que o repositório no Artifact Registry existe.
2. build-image — constrói a imagem Docker (tags: commit SHA + latest).
3. push-build-id — push da imagem com tag SHA.
4. push-latest — push da tag `latest`.
5. deploy-cloud-run — deploy no Cloud Run (executado pelo Cloud Build ou pelo workflow do GitHub Actions) e injeção automática de secrets.

Tempo típico de execução: ~3 minutos (Build Docker é o passo mais demorado: ~50s).

**Secrets & IAM (essenciais)**

- Secrets gerenciados: `openai-api-key`, `claude-api-key`, `qdrant-api-key` (Secret Manager).
- Runtime Service Account: `${SERVICE_NAME}-run-sa` (por padrão `mentor-virtual-tjce-run-sa`). Deve ter `roles/secretmanager.secretAccessor`.
- Cloud Build Service Account: `PROJECT_NUMBER@cloudbuild.gserviceaccount.com` precisa de `roles/run.admin`, `roles/artifactregistry.writer` e permissão para impersonar o Runtime SA.

Comando útil para dar acesso ao secret ao Runtime SA:

```bash
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:mentor-virtual-tjce-run-sa@chattjce.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=chattjce
```

**Como o deploy injeta secrets**

- `cloudbuild.yaml` usa `--set-secrets` no comando `gcloud run deploy` para vincular cada secret a uma variável de ambiente (por exemplo `OPENAI_API_KEY=openai-api-key:latest`).
- Em runtime, a aplicação lê essas variáveis via `os.environ` (ver `scripts/config.py`).

**Comandos úteis de debugging / validação**

- Listar builds: `gcloud builds list --project=chattjce`
- Ver logs do build: `gcloud builds log BUILD_ID --project=chattjce`
- Descrever serviço Cloud Run: `gcloud run services describe mentor-virtual-tjce --region=southamerica-east1 --platform=managed --project=chattjce`
- Ler logs Cloud Run: `gcloud run services logs read mentor-virtual-tjce --region=southamerica-east1`
- Health check (exemplo): `curl https://mentor-virtual-tjce-931025652334.southamerica-east1.run.app/`

**Endpoints principais**

- `GET /` → interface HTML
- `GET /healthz` (ou `GET /`) → health check
- `POST /api/chat` → API de chat (usa RAG + LLM)

**GitHub Actions (resumo)**

- Workflow: `.github/workflows/deploy.yml` (dispara em push para `main` ou manualmente).
- Autenticação: Workload Identity Federation (WIF) via `secrets.WIF_PROVIDER` e `secrets.WIF_SERVICE_ACCOUNT`. Alternativa menos segura: chave de Service Account (`GCP_SA_KEY`).

**Como funciona o build ao dar commit (GitHub Actions)**

Quando você dá `git push` em `main` (ou dispara manualmente pelo UI), o workflow `.github/workflows/deploy.yml` executa o job `build-and-deploy` com os seguintes passos principais:

1. Checkout: baixa o código (`actions/checkout@v4`).
2. Autenticação: `google-github-actions/auth@v2` usa WIF (OIDC) com os secrets do repositório (`WIF_PROVIDER` e `WIF_SERVICE_ACCOUNT`) para obter credenciais temporárias do GCP.
3. Setup do Cloud SDK: `google-github-actions/setup-gcloud@v2` instala e configura `gcloud`.
4. Configurar Docker para o Artifact Registry: `gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev`.
5. Garantir Artifact Registry: cria o repositório se não existir.
6. Build da imagem Docker: `docker build` cria as tags `:${{ github.sha }}` e `:latest`.
7. Push das imagens: `docker push` empurra ambas as tags para o Artifact Registry.
8. Deploy para Cloud Run: `gcloud run deploy` usa a imagem com a tag `${{ github.sha }}`, injeta `--set-env-vars` e `--set-secrets` (ex.: `OPENAI_API_KEY=openai-api-key:latest`) e define `--service-account=${{ env.SERVICE_NAME }}-run-sa@${{ env.PROJECT_ID }}.iam.gserviceaccount.com`.
9. Resultado: o workflow imprime a URL do serviço e o container passa a servir tráfego.

Pontos importantes para o sucesso do workflow:
- O repositório deve ter os secrets `WIF_PROVIDER` e `WIF_SERVICE_ACCOUNT` apontando para o provedor WIF e o Service Account configurado (ver `.github/SETUP.md`).
- O Service Account usado pelo workflow precisa de permissões: `roles/run.admin`, `roles/artifactregistry.writer`/`admin` e capacidade de `iam.serviceAccountUser` para a runtime SA.
- A Runtime SA (`mentor-virtual-tjce-run-sa`) deve ter `roles/secretmanager.secretAccessor` para que o Cloud Run consiga ler os secrets.

Diagnóstico e logs:
- Ver runs do workflow: `gh run list --workflow=deploy.yml` e `gh run view <RUN_ID> --log`.
- Ver logs do build (Cloud Build): `gcloud builds list --project=$PROJECT_ID` e `gcloud builds log BUILD_ID --project=$PROJECT_ID`.
- Ver logs do Cloud Run: `gcloud run services logs read ${SERVICE_NAME} --region=${REGION}`.

Ganho de tempo típico: ~3 minutos desde o push até o serviço atualizado (varia conforme o build).

**Arquivos importantes**

- Cloud Build config: [cloudbuild.yaml](../cloudbuild.yaml)
- (deploy helper removido) Para deploy manual: use `gcloud run deploy` conforme exemplos no README e no script `deploy-cloudrun.sh` (arquivo removido). Prefira `gcloud builds submit --config=cloudbuild.yaml` ou o workflow.
- Dockerfile: [Dockerfile](../Dockerfile)
- Setup GCP (script): [scripts/gcp-setup.sh](../scripts/gcp-setup.sh)
- GitHub Actions workflow: [workflows/deploy.yml](workflows/deploy.yml)
- Documentação detalhada: [SETUP.md](SETUP.md), [CI-CD.md](CI-CD.md), [CI-CD-STATUS.md](CI-CD-STATUS.md), [BUILD-ANALYSIS.md](BUILD-ANALYSIS.md)

**Erros comuns & soluções rápidas**

- Permission denied on secret: verifique se o Runtime SA tem `roles/secretmanager.secretAccessor` (comando acima).
- Build falha: olhar logs com `gcloud builds log BUILD_ID` e aumentar timeout em `cloudbuild.yaml` se necessário.
- Cloud Run não inicia: `gcloud run services describe ... --format=json | jq '.status'` para detalhes da revision.

**Checklist antes de deploy**

- [ ] `gcloud` instalado e autenticado
- [ ] Arquivo `.env` com as chaves de API
- [ ] Executar `./scripts/gcp-setup.sh`
- [ ] Verificar que os secrets foram criados no Secret Manager
- [ ] Verificar permissões das service accounts
- [ ] Executar `gcloud builds submit --config=cloudbuild.yaml` ou dar push para `main`

---

Se quiser, eu posso:
- rodar o `./scripts/gcp-setup.sh` localmente (precisa do `.env` e `gcloud` autenticado),
- ou gerar uma versão curta deste README para incluir no README raiz do repositório.
