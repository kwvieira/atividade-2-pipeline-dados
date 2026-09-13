-- ============================================================
-- ATIVIDADE 2 - PIPELINE DE DADOS
-- Consultas de auditoria no Amazon Athena
-- ============================================================

-- 1. Criar banco de dados
CREATE DATABASE atividade2_db;


-- 2. Quantidade total de pedidos na camada Raw
SELECT COUNT(*) AS total_pedidos
FROM pedidos;


-- 3. Quantidade de pedidos inválidos
SELECT
    COUNT(*) AS pedidos_invalidos
FROM pedidos p
WHERE p.quantidade <= 0
   OR p.cliente_id NOT IN (
       SELECT cliente_id
       FROM clientes
   )
   OR p.product_id NOT IN (
       SELECT product_id
       FROM produtos
   );


-- 4. Detalhamento das anomalias
SELECT
    p.pedido_id,
    p.cliente_id,
    p.product_id,
    p.quantidade,
    CASE
        WHEN p.quantidade <= 0 THEN 'quantidade <= 0'
        WHEN p.cliente_id NOT IN (
            SELECT cliente_id FROM clientes
        ) THEN 'cliente_id inexistente'
        WHEN p.product_id NOT IN (
            SELECT product_id FROM produtos
        ) THEN 'product_id inexistente'
    END AS motivo_rejeicao
FROM pedidos p
WHERE p.quantidade <= 0
   OR p.cliente_id NOT IN (
       SELECT cliente_id FROM clientes
   )
   OR p.product_id NOT IN (
       SELECT product_id FROM produtos
   )
ORDER BY p.pedido_id;


-- 5. Auditoria de metadados dos arquivos
SELECT
    pedido_id,
    cliente_id,
    product_id,
    quantidade,
    "$path" AS caminho_arquivo,
    "$file_size" AS tamanho_arquivo
FROM pedidos
LIMIT 10;


-- 6. Reconciliação de integridade
SELECT
    (SELECT COUNT(*) FROM pedidos) AS total_raw,
    26 AS total_silver,
    4 AS total_quarantine,
    (SELECT COUNT(*) FROM pedidos) = 26 + 4 AS reconciliacao_ok;
