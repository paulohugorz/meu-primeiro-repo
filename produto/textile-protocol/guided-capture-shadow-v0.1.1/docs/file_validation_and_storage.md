# Validação de arquivo e armazenamento

Antes da persistência, cada imagem passa por:

1. limite individual;
2. leitura da assinatura real;
3. detecção do formato;
4. confronto entre MIME declarado e MIME detectado;
5. `Image.verify()`;
6. decodificação integral;
7. dimensões mínimas e máximas;
8. limite de pixels;
9. limite acumulado da sessão.

A sequência é alocada dentro de uma transação `BEGIN IMMEDIATE`.  
O arquivo é escrito inicialmente como temporário, sincronizado e movido atomicamente.  
Se a transação falhar, o arquivo final é removido.

A restrição única `(session_id, sequence_no)` oferece proteção adicional.

`reconcile-artifacts` identifica:

- registro sem arquivo;
- arquivo sem registro;
- temporário abandonado.

A opção `--delete-orphans` remove apenas arquivos não referenciados.
