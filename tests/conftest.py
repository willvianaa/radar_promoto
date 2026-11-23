import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Testes automatizados: único ambiente que dispensa os segredos fortes (ver api/app/config.py).
os.environ.setdefault("APP_ENV", "teste")
