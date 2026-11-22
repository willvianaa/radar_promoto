# Briefing — Documentos (Haiku · `feat/documentos` · onda 3)

## A ideia
O dossiê é o produto final que sai do sistema e circula entre DP e Compliance. Ele precisa ser **formal, numerado e verificável**: gerado no servidor (não no navegador), com número único RP-AAAA-NNNNNN e hash, para ninguém alterar o arquivo depois sem ser percebido.

## Por que Haiku
Montagem de layout a partir de conteúdo já pronto; o texto e as regras vêm de Dados/API.

## Entrega
- PDF: logo RT Intelligence, "DOSSIÊ DE ANÁLISE OPERACIONAL", CONFIDENCIAL em todas as páginas, seções numeradas (`CLAUDE.md` §5), tabelas e gráficos dos blocos, rodapé de indícios.
- Excel: dados completos por aba (identificação, blocos, jornada, pesquisas, aderência, parâmetros usados).
- Numeração sequencial anual com lock (`app.dossie_sequencia`), nome "Dossiê - NOME.pdf/.xlsx", SHA-256 gravado.
- Revisão final de termos proibidos antes de gerar.

## Não faz
Não escreve nem decide o texto; recebe o conteúdo do dossiê já editado.

## Encaixe
Chamado pela API na emissão; o Front só baixa o arquivo.

## Pronto quando
Dossiê de fixture idêntico ao modelo aprovado (`docs/04-modelo-documentos.md` ajustado ao padrão do `CLAUDE.md`); numeração sem buraco nem repetição em teste concorrente.
