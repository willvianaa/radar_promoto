# Política de retenção e descarte — proposta (Q-09)

> **Proposta para decisão do DPO, DP e Compliance (Q-09).** Até a decisão, o sistema não entra em emissão formal. Os prazos abaixo partem do princípio da necessidade (art. 6º, III) e dos prazos trabalhistas usuais (prescrição de 5 anos durante o vínculo e 2 anos após o desligamento, art. 7º, XXIX da Constituição); o Jurídico confirma.

## 1. Prazos propostos

| Tipo de dado | Prazo | Ao vencer |
|--------------|-------|-----------|
| `raw` (arquivo e linhas como recebidos) | 90 dias após a carga | Apagar (o `core` já tem o necessário) |
| Cadastro do colaborador | Vínculo + 5 anos | Anonimizar (CPF → id aleatório; nome removido) |
| Visitas, jornada, faltas (tipo) | 5 anos | Apagar ou anonimizar para estatística |
| Motivo de falta / atestado | 5 anos | Apagar |
| Atividades, pesquisas, aderência, PDOH | 2 anos | Agregar por regional/semana e apagar o individual |
| Posição GPS (lat/lon) | 12 meses | Manter só a distância calculada e o indício |
| Fotos (arquivo) | 12 meses | Apagar o arquivo; manter hash e indício. Foto citada em dossiê emitido segue o prazo do dossiê |
| Humor (exceto "Doente") | 12 meses | Apagar o individual; agregados ≥ 5 pessoas podem ficar |
| Humor "Doente" | 6 meses | Apagar |
| Indicadores, alertas, nível, risco | 2 anos | Apagar (são recalculáveis) |
| Dossiê emitido (conteúdo, PDF, XLSX) | 5 anos após emissão, ou fim do processo relacionado se for maior | Apagar; manter número e hash na auditoria |
| Usuário interno | Ativo + 1 ano | Anonimizar; hash de senha apagado ao desligar |
| Auditoria | 5 anos | Apagar em lote por ano (único DELETE permitido, por rotina dedicada e registrada) |
| Backups | 35 dias rotativos | Sobrescrita |

## 2. Regras

1. **Descarte automático**: rotina diária identifica o que venceu, apaga ou anonimiza e grava na auditoria (tipo, quantidade, período; nunca o conteúdo).
2. **Retenção legal (hold)**: Jurídico pode suspender o descarte de um titular ou período com processo em curso, com registro e justificativa.
3. **Direitos do titular**: pedido de eliminação (art. 18, VI) é avaliado pelo DPO frente às bases legais; dado necessário a obrigação legal ou defesa em processo pode ser mantido, com resposta fundamentada.
4. **Ambientes de teste**: só dados fictícios ou pseudonimizados; nada de cópia de produção.
5. **Revisão**: anual ou quando mudar finalidade, origem ou base legal.

## 3. Decisões pendentes

- Confirmação dos prazos trabalhistas pelo Jurídico e DP.
- Se o "Doente" for mantido (Q-10), prazo e base.
- Tratamento de dados de colaboradores PJ (Q-11).
