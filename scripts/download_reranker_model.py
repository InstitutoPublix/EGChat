#!/usr/bin/env python
"""Script para pré-baixar o modelo BGE Small de reranking.

Use este script para:
1. Pré-baixar o modelo localmente (antes do deploy)
2. Incluir o modelo no Docker image
3. Evitar downloads durante inicialização em produção

Uso:
    python scripts/download_reranker_model.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from config import PROJECT_ROOT
from reranker import _ensure_model_dir, _get_reranker


def download_model():
    print("📥 Baixando modelo BGE Small para reranking...")
    print(f"📁 Diretório: {PROJECT_ROOT / 'models'}")

    _ensure_model_dir()

    print("⏳ Carregando modelo (pode levar alguns minutos na primeira vez)...")
    reranker = _get_reranker()

    print("✅ Modelo baixado com sucesso!")
    print(f"📦 Modelo pronto em: {PROJECT_ROOT / 'models'}")
    print("\n💡 Dicas:")
    print("  - O modelo será cacheado localmente")
    print("  - Próximas execuções serão mais rápidas (~50ms de latência)")
    print("  - Para produção, inclua a pasta 'models/' no Dockerfile")


if __name__ == "__main__":
    try:
        download_model()
    except Exception as e:
        print(f"❌ Erro ao baixar modelo: {e}")
        sys.exit(1)
