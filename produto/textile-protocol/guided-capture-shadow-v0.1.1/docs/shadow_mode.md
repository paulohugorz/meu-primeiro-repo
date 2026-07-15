# Contrato de shadow mode

## O que acontece

- decisões do baseline são copiadas como snapshots imutáveis;
- gatilhos geram tarefas internas;
- especialistas podem resolver tarefas;
- propostas são comparadas com o snapshot;
- o sistema mede quantas propostas mudariam a decisão;
- custos, tempo, tipos de erro e taxa de conclusão podem ser analisados.

## O que não acontece

- nenhuma decisão oficial é atualizada;
- nenhuma publicação é alterada;
- nenhum usuário recebe notificação;
- nenhuma tarefa certifica uma propriedade;
- nenhuma proposta é promovida;
- nenhum resultado shadow entra no benchmark oficial.

## Motivo

O shadow mode permite testar se o fluxo de verificação melhora qualidade e em que custo, sem criar risco operacional ou contaminar a baseline.
