"""Repositório em memória e usuários fictícios (sem dado real)."""

from api.app.repositorio import UsuarioRegistro
from api.app.seguranca import hash_senha

SENHA = "senha-ficticia-123"
_H = hash_senha(SENHA)


class RepoMem:
    def __init__(self):
        self.usuarios = {
            u.id: u
            for u in [
                UsuarioRegistro(1, "rh@ficticio.example.com", "Rita RH", "rh", _H),
                UsuarioRegistro(2, "dp@ficticio.example.com", "Davi DP", "dp", _H),
                UsuarioRegistro(3, "comp@ficticio.example.com", "Carla Compliance", "compliance", _H),
                UsuarioRegistro(4, "pp@ficticio.example.com", "Paulo PP", "pp", _H),
                UsuarioRegistro(5, "dir@ficticio.example.com", "Diana Diretoria", "diretoria", _H),
                UsuarioRegistro(6, "ger@ficticio.example.com", "Gil Gerente", "gerencia_regional", _H, regional="Sul"),
                UsuarioRegistro(7, "sup@ficticio.example.com", "Sara Supervisora", "supervisor", _H,
                                supervisor_cpf="00000000191", supervisor_nome="SARA SUPERVISORA"),
                UsuarioRegistro(8, "merch@ficticio.example.com", "Mario Merch", "merch", _H),
                UsuarioRegistro(9, "adm@ficticio.example.com", "Ana Admin", "admin", _H),
                UsuarioRegistro(10, "off@ficticio.example.com", "Otto Desligado", "rh", _H, ativo=False),
            ]
        }
        self.auditoria: list[dict] = []

    def usuario_por_email(self, email):
        return next((u for u in self.usuarios.values() if u.email.lower() == email.lower()), None)

    def usuario_por_id(self, usuario_id):
        return self.usuarios.get(usuario_id)

    def gravar_auditoria(self, usuario_id, acao, recurso, recurso_id, ip, detalhe):
        self.auditoria.append(
            dict(usuario_id=usuario_id, acao=acao, recurso=recurso, recurso_id=recurso_id, ip=ip, detalhe=detalhe)
        )
