# Migração para o Claude da empresa

Como levar o Radar Promotor da conta pessoal para a conta empresarial do Claude da RT, sem perder nada e sem expor dados.

**Ideia central:** conversas não passam de uma conta para outra. O que migra é o **projeto**: código, contratos e documentação neste repositório. Uma sessão nova do Claude Code, na conta da empresa, entende o projeto lendo `CLAUDE.md`, `.claude/agents/` (harness de cada sessão) e `docs/briefings/`.

## O que está onde

| Item | Onde fica hoje | Migra como |
|---|---|---|
| Código do sistema web (API, regras, ingestor, testes) | Este repositório | Transferência do repositório |
| Protótipo (`radar_v3/`: `build.py`, `parts/`, `index.html`) | Este repositório (só código) | Transferência do repositório |
| Regras, contratos, LGPD, briefings, harness | Este repositório | Transferência do repositório |
| Link do protótipo e da apresentação | Conta pessoal do claude.ai | Republicar pela conta da empresa (links novos) |
| Dados reais carregados no protótipo | Banco do artefato na conta pessoal | Recarregar na conta da empresa e apagar na pessoal |
| Exports reais (Involves, 2PRT, fotos) | Pasta local `dados/` e `radar_v3/fotos/` | Nunca vão para o GitHub; copiar por meio aprovado pela TI |
| Esta conversa | Conta pessoal | Não migra; exportar só como registro, se quiser |

## Passo a passo

### 1. Tornar o repositório privado
GitHub → repositório `radar_promoto` → **Settings** → **General** → **Danger Zone** → **Change repository visibility** → **Private**.

### 2. Levar o repositório para a RT
- Se a RT tem organização no GitHub: **Settings** → **Danger Zone** → **Transfer ownership** → escolher a organização.
- Se não tem: **Settings** → **Collaborators** → adicionar quem vai trabalhar no projeto.

### 3. Preparar o computador com a conta da empresa
1. Instalar o Claude (app desktop) e entrar com a **conta empresarial**.
2. Pedir ao administrador do Claude da RT que libere o **Claude Code** e as **páginas publicadas (artefatos)** para a conta.
3. Clonar o repositório:
   ```powershell
   git clone https://github.com/<organizacao>/radar_promoto.git
   ```
4. Abrir a pasta `radar_promoto` no Claude Code. Primeira mensagem sugerida:
   > "Leia CLAUDE.md, docs/08-plano-de-ondas.md e docs/briefings/README.md e me diga em que pé está o projeto."

### 4. Republicar o protótipo e a apresentação
1. Copiar as fotos com indício para `radar_v3/fotos/` (fora do Git).
2. No Claude Code: "Rode `python radar_v3/build.py` e publique `radar_v3/index.html` como página, junto com `radar_v3/fotos/`."
3. A apresentação: pedir para recriá-la a partir do deck atual (ou exportar o deck atual em PDF/PPTX antes e reimportar).

### 5. Recarregar os dados
- No protótipo novo, botão **Atualizar dados** com os CSVs de `dados/radar/` e `dados/2prt/`, ou pedir à sessão para rodar a carga.
- Depois de conferir que tudo apareceu, **apagar os dados da conta pessoal** (pendência R2 de `docs/lgpd/00-diagnostico.md`).

### 6. Guardar o histórico desta conversa (opcional)
Conta pessoal no claude.ai → **Configurações** → **Privacidade** → **Exportar dados**. É só um registro; não dá para importar na conta da empresa.

## Cuidados
- Dados reais (CPF, humor, fotos, planilhas) **nunca** vão para o GitHub. O `.gitignore` já bloqueia `dados/`, `radar_v3/tmp/`, `radar_v3/fotos/` e `radar_v3/dump.html`, e o CI varre CPF e segredos em todo PR.
- Credenciais (Involves, 2PRT, Google) ficam só nos *secrets* do ambiente da empresa.
- Na conta da empresa os dados passam a ficar sob o contrato corporativo, que é o caminho certo pela LGPD (`CLAUDE.md` §2.1).
