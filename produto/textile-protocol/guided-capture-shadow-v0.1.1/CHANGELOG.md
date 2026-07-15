# Changelog

## v0.1.1 — 15/07/2026

- adiciona o PHYLLOS Textile Recognition Lab com fluxo responsivo em cinco etapas;
- separa Evidence de resultado experimental e oferece diagnóstico JSON local;
- adiciona execução de reconhecimento shadow como replay explícito da baseline sintética congelada;
- persiste `recognition_runs` sem mutação oficial ou decisão de publicação;
- cobre resultado, abstinência, remoção pré-confirmação e bloqueio de sessão incompleta em 31 testes;
- adiciona ponte persistida `OPS-TX → sample → TextileSample`;
- bloqueia captura das 70 candidatas enquanto não houver recebimento físico;
- adiciona cinco fixtures sintéticas isoladas;
- controles de qualidade começam desmarcados;
- registra ator e horário da confirmação de qualidade;
- valida assinatura, MIME real, decodificação, dimensões e pixels;
- adiciona limite acumulado por sessão;
- aloca sequência dentro de transação `BEGIN IMMEDIATE`;
- adiciona restrição única `(session_id, sequence_no)`;
- coordena arquivo temporário, rename atômico, banco e limpeza em falha;
- adiciona reconciliação e limpeza de arquivos órfãos;
- limita `would_change` às dimensões congeladas do benchmark;
- valida classes e relações de aplicabilidade;
- cria `Evidence` para cada captura sem elevar autenticidade ou relevância;
- registra supersessão de sessões e Evidence;
- mantém Onda 1 em `prepared_not_sent`;
- mantém field test e promoção desabilitados.
- aplica `field_test_enabled` como gate executável para candidatas reais;
- escapa campos dinâmicos da lista web de tarefas;
- mantém banco e artefatos gerados fora do versionamento.
