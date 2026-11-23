"""Configuração da API. Tudo vem de variáveis de ambiente (secrets); nada de valor real no código."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = ""
    app_env: str = "desenvolvimento"
    # Segredo que assina a sessão e deriva os ids opacos. Obrigatório fora de desenvolvimento.
    segredo_sessao: str = Field(default="", repr=False)
    sessao_horas: int = 8
    cookie_nome: str = "rp_sessao"

    @property
    def producao(self) -> bool:
        return self.app_env not in ("desenvolvimento", "ci", "teste")

    @property
    def segredo(self) -> bytes:
        if not self.segredo_sessao:
            if self.producao:
                raise RuntimeError("SEGREDO_SESSAO não definido")
            return b"somente-desenvolvimento-nao-usar-em-producao"
        return self.segredo_sessao.encode()


@lru_cache
def configuracao() -> Configuracao:
    return Configuracao()
