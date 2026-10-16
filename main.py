"""Atalho:  py main <comando>   (igual a: python -m k_study <comando>; sem comando = serve).

Funciona sem instalar o pacote: coloca src/ no caminho de importação.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from k_study.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
