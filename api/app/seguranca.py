"""Hash de senha (argon2), sessão assinada e id opaco do colaborador."""

import base64
import hashlib
import hmac
import time

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from itsdangerous import BadSignature, URLSafeTimedSerializer

_ph = PasswordHasher()
# Hash de uma senha descartada: iguala o tempo de resposta entre e-mail inexistente e senha errada.
_HASH_FALSO = _ph.hash("senha-descartada-sem-uso")


def hash_senha(senha: str) -> str:
    return _ph.hash(senha)


def verifica_senha(senha: str, hash_: str | None) -> bool:
    try:
        ok = _ph.verify(hash_ or _HASH_FALSO, senha)
    except (VerificationError, InvalidHashError):
        return False
    return ok and hash_ is not None


def _serializador(segredo: bytes) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(segredo, salt="rp-sessao")


def emite_sessao(segredo: bytes, usuario_id: int) -> str:
    return _serializador(segredo).dumps({"u": usuario_id, "t": int(time.time())})


def le_sessao(segredo: bytes, token: str, max_idade_s: int) -> int | None:
    try:
        return int(_serializador(segredo).loads(token, max_age=max_idade_s)["u"])
    except (BadSignature, KeyError, ValueError, TypeError):
        return None


def id_opaco(segredo: bytes, cpf: str) -> str:
    """Id estável e não reversível do colaborador (HMAC do CPF). O CPF nunca vai à URL."""
    mac = hmac.new(segredo, b"colab:" + cpf.encode(), hashlib.sha256).digest()[:15]
    return "c_" + base64.b32encode(mac).decode().lower().rstrip("=")
