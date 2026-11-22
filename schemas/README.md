# schemas/ — formato esperado de cada export

Cada arquivo `*.schema.json` descreve **uma linha** do export como chega da origem (JSON Schema 2020-12),
mais metadados `x-` que o ingestor usa para ler e validar o arquivo.

| Schema | Origem | Formato | Status |
|---|---|---|---|
| `colaboradores` | Plataforma de monitoramento — cadastro de colaboradores | CSV `;` UTF-8 | Confirmado |
| `operacao` | Plataforma de monitoramento — relatório de check-in (painel de visitas) | XLSX | Confirmado |
| `atividades` | Plataforma de monitoramento — relatório de pesquisas | CSV `;` UTF-8 | Confirmado |
| `humor` | Plataforma de monitoramento — relatório de humor | XLSX (cabeçalho não está na 1ª linha) | Confirmado |
| `fotos` | Plataforma de monitoramento — fotos das pesquisas (ZIP) + manifesto | ZIP + CSV | Provisório |
| `faltas` | DP — faltas, atestados e afastamentos | XLSX/CSV | Provisório (layout a confirmar com DP) |
| `aderencia` | 2PRT — Tabela Analítica (Exportar XLSX) | XLSX | Confirmado |
| `pdoh` | 2PRT — PDOH, rankings (Exportar XLSX) | XLSX (4 arquivos) | Confirmado (extra) |
| `estoque` | Cliente/backoffice — estoque e ruptura | XLSX/CSV | Provisório (Q-13) |

## Regras de validação (valem para todos)

1. **Cabeçalho:** o ingestor procura nas 15 primeiras linhas a que contém todas as colunas `x-colunas-obrigatorias`,
   comparando nomes normalizados (maiúsculas, sem acento, espaços simples). Colunas extras são aceitas e ignoradas.
2. **Mudança de formato:** faltou coluna obrigatória, mudou o tipo de mais de 2% das linhas ou o arquivo veio vazio
   quando não deveria → o ingestor **para a carga daquela origem**, não grava nada e abre alerta para P&P/TI (`ingestao_alerta`).
3. **Duplicidade:** linhas repetidas são descartadas pela `x-chave-unica`.
4. **Limite:** cada export tem no máximo 10 mil linhas; o ingestor fatia por período (`x-fatiamento`).
5. **Raw imutável:** o arquivo original é guardado como recebido (hash SHA-256) antes de qualquer tratamento.
6. Status "Provisório": o schema pode mudar quando a área dona confirmar o layout; a mudança entra por PR na mãe.
