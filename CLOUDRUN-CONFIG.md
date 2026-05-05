# mentor-virtual-tjce - Cloud Run Configuration
# Arquivo de referência para configuração manual no console GCP

## Configurações Recomendadas para Custo Mínimo:

### 1. Recursos Computacionais
- **Memory**: 512 MB (mínimo, suficiente para LLM API calls)
- **CPU**: 1 vCPU (alocação padrão)
- **Timeout**: 3600 segundos (1 hora, importante para processamento de contextos longos)

### 2. Auto-scaling
- **Min instances**: 0 (IMPORTANTE: sem custo quando não usado)
- **Max instances**: 5 (previne escalação incontrolável)
- **Concurrency**: 80 (requisições simultâneas por instância)

### 3. Triggers & Deployment
- Conectar ao GitHub para CI/CD automático
- Usar `cloudbuild.yaml` para builds otimizados
- Ativar cache de camadas Docker

### 4. Monitoramento & Logs
- Cloud Logging: ativado (sem custo para logs)
- Cloud Trace: opcional (pequeno custo)
- Alertas: configurar para uso acima do esperado

## Estimativa de Custo (USD/mês, aproximado):

### Cenário 1: Uso leve (até 1M requisições/mês)
- Compute: ~$5
- Invocações: ~$0.40
- **Total: ~$5-6/mês**

### Cenário 2: Uso moderado (10M requisições/mês)
- Compute: ~$50
- Invocações: ~$4
- **Total: ~$54/mês**

### Cenário 3: Com min-instances = 1 (Always On)
- Compute: ~$15/mês só para manter rodando
- Não recomendado para projeto pessoal

## Dicas de Economia:

1. ✅ Use min-instances = 0
2. ✅ Ajuste max-instances conforme necessidade
3. ✅ Use 512Mi de memória (não é muita diferença de preço)
4. ✅ Implemente cache em frontend (static assets)
5. ✅ Use CDN (Cloud CDN) para servir static files
6. ✅ Monitorar quotas e limites

## Links Úteis:

- Cloud Run Pricing: https://cloud.google.com/run/pricing
- Cloud Run Documentation: https://cloud.google.com/run/docs
- Autoscaling Best Practices: https://cloud.google.com/run/docs/about-runtime-contract
