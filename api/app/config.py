"""Configuração da API. Tudo vem de variáveis de ambiente (secrets); nada de valor real no código.

Falha fechada: sem segredos fortes a API não sobe (exceto APP_ENV=teste ou ci, só para testes automatizados).
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

AMBIENTES_SEM_SEGREDO = ("teste", "ci")
MIN_SEGREDO = 32


class ConfiguracaoInvalida(RuntimeError):
    pass


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = ""
    app_env: str = "producao"  # padrão restritivo: ambiente não declarado exige segredos
    segredo_sessao: str = Field(default="", repr=False)  # assina o cookie de sessão
    segredo_id: str = Field(default="", repr=False)  # deriva o id opaco do colaborador (chave separada)
    sessao_horas: int = 8
    cookie_nome: str = "rp_sessao"

    def _segredo(self, valor: str, nome: str, rotulo: bytes) -> bytes:
        if self.app_env in AMBIENTES_SEM_SEGREDO:
            return (valor or f"somente-testes-{nome}").encode() + b"|" + rotulo
        if len(valor.encode()) < MIN_SEGREDO:
            raise ConfiguracaoInvalida(f"{nome.upper()} ausente ou com menos de {MIN_SEGREDO} bytes")
        return valor.encode()

    @property
    def segredo(self) -> bytes:
        return self._segredo(self.segredo_sessao, "segredo_sessao", b"sessao")

    @property
    def segredo_do_id(self) -> bytes:
        return self._segredo(self.segredo_id, "segredo_id", b"id")

    def validar(self) -> None:
        """Chamada na subida: erra antes de aceitar qualquer requisição."""
        if self.app_env not in AMBIENTES_SEM_SEGREDO:
            if self.segredo_sessao == self.segredo_id:
                raise ConfiguracaoInvalida("SEGREDO_SESSAO e SEGREDO_ID devem ser diferentes")
        _ = self.segredo, self.segredo_do_id


@lru_cache
def configuracao() -> Configuracao:
    return Configuracao()
