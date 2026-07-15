# Protocolo PHYLLOS de Observação e Verificação Têxtil

**Status:** discovery interno
**Início:** 2026-07-15
**Decision ID:** `PHYLLOS-DEC-PTIP-DISCOVERY-S1-2026-07-15`

## Decisão vigente

O protocolo será investigado como uma capacidade interna do DPP Studio para caracterizar amostras, explicitar incerteza e gerar tarefas de verificação. Não é um produto autônomo nem um identificador conclusivo de composição por fotografia.

Toda sugestão visual permanece privada e recebe a proveniência auxiliar `inferido_por_modelo`. Essa proveniência não substitui nem eleva os estados canônicos `ausente`, `declarado`, `calculado`, `documentado` e `verificado`.

## Pacote da Semana 01

- [Execution Brief](execution-brief-semana-01.md)
- [Taxonomia têxtil v0.3 pós-revisão — versão vigente](taxonomia-textil-v0.3.md)
- [Taxonomia têxtil v0.1 — histórico](taxonomia-textil-v0.1.md)
- [Matriz de evidência e protocolo seguro v0.1](matriz-evidencia-protocolo-v0.1.md)
- [Contrato de dados v0.1](contrato-dados-v0.1.md)
- [Decisão de adoção da v0.3](decisao-adocao-taxonomia-v0.3.md)
- [Modelagem em grafo v0.4 — corrigida](modelagem-grafo-v0.4.md)
- [Schema de asserção v0.4](schema/assertion-v0.4.schema.json)
- [Fixtures de validação](fixtures/README.md)
- [Pacote executável v0.4.1](executavel-v0.4.1/README.md)

## Implementação executável vigente

O diretório `executavel-v0.4.1/` é a implementação validável da taxonomia v0.3 sobre a modelagem em grafo v0.4.1. Ele contém o dicionário canônico, JSON Schema, validador semântico, 20 fixtures válidas, 20 inválidas, relatórios e manifesto de integridade.

```bash
python -m pip install -r produto/textile-protocol/executavel-v0.4.1/requirements.txt
python produto/textile-protocol/executavel-v0.4.1/validate.py --all
```

Os arquivos mínimos em `schema/` e `fixtures/` permanecem como histórico da primeira iteração e não substituem o pacote executável v0.4.1.

## Gate central

Nenhuma composição inferida por imagem pode preencher automaticamente um campo público do DPP. Confiança do modelo e nível de evidência são dimensões independentes.
