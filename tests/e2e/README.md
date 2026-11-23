# tests/e2e/

Testes de ponta a ponta contra a API (e, depois, o Front). **Ignorados** enquanto `E2E_BASE_URL` não estiver definida.

```powershell
$env:E2E_BASE_URL = "http://localhost:8000/api/v1"
$env:E2E_RH_EMAIL = "..."; $env:E2E_RH_SENHA = "..."   # usuários de TESTE da seed fictícia; nunca no repositório
pytest tests/e2e
```

- Dados: só a seed fictícia (gerada por `tests/carga/gerador.py`). Nenhum dado real.
- Credenciais só por variável de ambiente/secrets; o código nunca as registra.
- Testes com `pytest.skip("completar: ...")` são contratos a preencher quando a API e a seed existirem.
- Cobertura planejada: autenticação, CPF mascarado, matriz de permissões (docs/05 §5.2), auditoria, painel < 2 s com 1.000 × 60, dossiê (formato e termos proibidos). Front: a definir quando existir (Playwright).
