# PHYLLOS Engineering Guided Capture Shadow v0.1.1

**Estado:** pronto para integração shadow e piloto sintético interno.  
**Não autorizado:** field test com as 70 candidatas, envio da Onda 1, benchmark empírico ou promoção de decisões.

## Estado material

```text
70 candidatas
0 amostras físicas
0 Evidence validada
0 conjunto ouro
```

As 70 candidatas possuem ponte persistida:

```text
OPS-TX-001
sample:ops-tx-001
textile-sample:ops-tx-001
```

Todas permanecem com `capture_allowed=false`.

## Correções v0.1.1

- ponte de IDs persistida;
- quality gates desmarcados por padrão;
- ator e timestamp da confirmação;
- validação real de JPEG, PNG e WebP;
- dimensões e decodificação obrigatórias;
- limite acumulado por sessão;
- sequência transacional;
- proteção contra órfãos e rotina de reconciliação;
- `would_change` limitado ao benchmark congelado;
- Evidence vinculada a cada captura;
- supersessão de sessão e Evidence;
- cinco registros sintéticos isolados.

## Instalação

```bash
python -m pip install -r requirements.txt
python src/cli.py init-db
```

## Interface local

```bash
python src/cli.py serve
```

Abrir `http://127.0.0.1:8765`.

A interface **PHYLLOS Textile Recognition Lab** conduz seleção, seis capturas,
revisão, processamento, resultado experimental, Evidence e diagnóstico JSON em
um único fluxo responsivo. Ela usa `OPS-SYN-001` por padrão. Uma candidata
`OPS-TX-*` é recusada enquanto não houver recebimento físico registrado.

O reconhecimento disponível neste MVP é uma reprodução controlada da baseline
congelada dos cinco fixtures sintéticos. Ele valida a integração ponta a ponta,
mas não representa uma nova inferência visual nem produz métrica empírica.

## Hospedagem de demonstração

O `render.yaml` na raiz do repositório cria um Web Service isolado chamado
`phyllos-textile-recognition-lab`, com health check em `/api/health` e deploy
automático desabilitado. O filesystem da instância gratuita é efêmero: sessões,
imagens e diagnósticos existem apenas para demonstração e podem ser descartados
quando o serviço reiniciar ou receber um novo deploy.

## Validação

```bash
python -m unittest discover -s tests -v
```

## Dry run sintético

```bash
python scripts/run_synthetic_pilot.py
```

## Reconciliação de artefatos

```bash
python src/cli.py reconcile-artifacts
python src/cli.py reconcile-artifacts --delete-orphans
```

## Exportar Evidence

```bash
python src/cli.py export-evidence \
  --output outputs/synthetic_evidence.jsonl
```

Nenhum endpoint de promoção ou envio de solicitação existe.

O gate global `field_test_enabled=false` também é aplicado pelo serviço às candidatas `OPS-TX-*`. Conteúdo dinâmico da lista web de tarefas é escapado antes da renderização.
