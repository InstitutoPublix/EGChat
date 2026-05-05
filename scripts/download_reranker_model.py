#!/usr/bin/env python

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from config import PROJECT_ROOT
from huggingface_hub import snapshot_download
from reranker import (
    MODEL_CACHE_PATH,
    MODEL_REPO_ID,
    _ensure_model_dir,
    _get_reranker,
    ensure_local_reranker_model,
)


def download_model():
    print("Baixando modelo mMiniLM (multilingual) para reranking...")
    print(f"Diretorio: {MODEL_CACHE_PATH}")

    _ensure_model_dir()

    snapshot_download(
        repo_id=MODEL_REPO_ID,
        local_dir=MODEL_CACHE_PATH,
        ignore_patterns=[
            "onnx/*",
            "openvino/*",
            "pytorch_model.bin",
        ],
    )

    ensure_local_reranker_model()

    print("Validando carregamento local do modelo...")
    _get_reranker()

    print("Modelo baixado e validado com sucesso.")
    print(f"Modelo pronto em: {PROJECT_ROOT / 'models'}")
    print("Inclua a pasta models/ no contexto do Cloud Build.")


if __name__ == "__main__":
    try:
        download_model()
    except Exception as e:
        print(f"Erro ao baixar modelo: {e}")
        sys.exit(1)
