# Atividade 2 — Pipeline de Dados com AWS S3 e Athena

## 1. Objetivo

Construir um pipeline de dados utilizando Amazon S3 e Amazon Athena, contemplando ingestão de dados, validação de qualidade, tratamento de anomalias, arquitetura Medallion (Raw, Silver e Gold) e auditoria de metadados e consistência.

O projeto utiliza dados simulados de clientes, produtos e pedidos, contendo propositalmente registros inválidos para demonstrar o processo de Data Quality e quarentena.

---

## 2. Arquitetura do Pipeline

O fluxo implementado foi:

Dados simulados → Raw → Data Quality → Quarantine → Silver → Gold → Athena

### Camadas

- **Raw:** dados originais em formato CSV, organizados por data de ingestão.
- **Quarantine:** registros rejeitados durante as validações de qualidade.
- **Silver:** dados válidos enriquecidos por meio do relacionamento entre pedidos, clientes e produtos.
- **Gold:** dados agregados para análise.
- **Athena:** consultas SQL para análise, auditoria e reconciliação dos dados.

---

## 3. Estrutura no Amazon S3

Bucket utilizado:

`atividade-2-pipeline-dados-2026-10782188`

Estrutura:

```text
s3://atividade-2-pipeline-dados-2026-10782188/

├── raw/
│   ├── clientes/
│   │   └── ingest_date=2026-09-13/
│   │       └── clientes.csv
│   │
│   ├── produtos/
│   │   └── ingest_date=2026-09-13/
│   │       └── produtos.csv
│   │
│   └── pedidos/
│       └── ingest_date=2026-09-13/
│           └── pedidos.csv
│
├── quarantine/
│   └── pedidos_rejeitados/
│       └── data=2026-09-13/
│           └── rejeitados.json
│
├── processed/
│   ├── pedidos_validos/
│   │   └── ingest_date=2026-09-13/
│   │       └── pedidos_validos.csv
│   │
│   └── fato_vendas/
│       └── ingest_date=2026-09-13/
│           └── fato_vendas.parquet
│
├── gold/
│   └── vendas_por_uf_categoria/
│       └── data=2026-09-13/
│           └── vendas_por_uf_categoria.parquet
│
└── athena-results/

## 4. Geração dos dados

Os dados foram gerados pelo script:

src/gerar_dados.py

Foram criados:

8 clientes;
5 produtos;
30 pedidos.

O script também insere propositalmente 4 anomalias nos pedidos para testar as regras de qualidade.

Anomalias inseridas
Pedido	Problema
5	quantidade = -2
10	cliente_id = 999, inexistente
15	product_id = 999, inexistente
20	quantidade = 0

## 5. Data Quality

A validação é realizada pelo script:

src/validar_dados.py

Foram utilizadas as seguintes regras:

A quantidade do pedido deve ser maior que zero.
O cliente_id deve existir na dimensão de clientes.
O product_id deve existir na dimensão de produtos.

Registros que não atendem às regras são rejeitados.

Resultado
Pedidos recebidos: 30
Pedidos válidos: 26
Pedidos rejeitados: 4

Os registros rejeitados são armazenados em formato JSON na camada de quarentena.

## 6. Quarantine

Os registros inválidos são armazenados em:

s3://atividade-2-pipeline-dados-2026-10782188/quarantine/pedidos_rejeitados/data=2026-09-13/rejeitados.json

Cada registro contém o pedido rejeitado e o motivo da rejeição.

Exemplos de motivos:

quantidade <= 0
cliente_id inexistente
product_id inexistente

## 7. Camada Silver

A camada Silver é criada pelo script:

src/criar_silver.py

Nessa etapa são utilizados apenas os pedidos considerados válidos.

Os pedidos são relacionados às tabelas de clientes e produtos por meio dos identificadores:

cliente_id
product_id

Também é calculado o campo:

valor_total = quantidade * preco

O resultado é armazenado em formato Parquet com compressão Snappy.

Local:

processed/fato_vendas/ingest_date=2026-09-13/fato_vendas.parquet
Resultado
Registros processados: 26
Faturamento total: R$ 66.910,00

## 8. Camada Gold

A camada Gold é criada pelo script:

src/criar_gold.py

Os dados da Silver são agregados por:

UF;
Categoria.

São calculados:

quantidade de vendas;
quantidade de itens;
faturamento.

O resultado também é armazenado em formato Parquet com compressão Snappy.

Local:

gold/vendas_por_uf_categoria/data=2026-09-13/vendas_por_uf_categoria.parquet
Resultado
Registros agregados: 17
Faturamento total: R$ 66.910,00

O faturamento da camada Gold é igual ao faturamento da camada Silver, demonstrando a consistência da transformação.

## 9. Amazon Athena

Foi criado o banco de dados:

atividade2_db

Foram criadas tabelas externas para consulta dos dados armazenados no Amazon S3.

Entre as consultas realizadas estão:

Total de pedidos

Consulta para verificar a quantidade total de registros na camada Raw.

Resultado:

30 pedidos

Registros inválidos

Consulta para identificar os pedidos que apresentam anomalias.

Resultado:

4 pedidos rejeitados

Metadados

Foi utilizada a consulta abaixo para verificar informações de localização e tamanho dos arquivos:

SELECT
    pedido_id,
    cliente_id,
    product_id,
    quantidade,
    "$path" AS caminho_arquivo,
    "$file_size" AS tamanho_arquivo
FROM pedidos
LIMIT 10;

Os campos $path e $file_size permitem realizar uma auditoria sobre os arquivos consultados pelo Athena.

Reconciliação

Foi realizada uma consulta para verificar a consistência entre Raw, Silver e Quarantine:

SELECT
    (SELECT COUNT(*) FROM pedidos) AS total_raw,
    26 AS total_silver,
    4 AS total_quarantine,
    (SELECT COUNT(*) FROM pedidos) = 26 + 4 AS reconciliacao_ok;

Resultado:

total_raw = 30
total_silver = 26
total_quarantine = 4
reconciliacao_ok = true

A reconciliação demonstra que:

30 registros Raw = 26 registros válidos + 4 registros rejeitados

## 10. Scripts

Os principais scripts do projeto são:

src/
├── gerar_dados.py
├── validar_dados.py
├── criar_silver.py
└── criar_gold.py
gerar_dados.py

Gera os dados simulados e insere as anomalias.

validar_dados.py

Executa as regras de Data Quality e separa os registros válidos dos rejeitados.

criar_silver.py

Realiza os joins entre pedidos, clientes e produtos e calcula o valor_total.

criar_gold.py

Realiza as agregações por UF e categoria.

## 11. Execução

Os scripts podem ser executados em sequência:

python src/gerar_dados.py
python src/validar_dados.py
python src/criar_silver.py
python src/criar_gold.py

Na execução em ambiente AWS, os arquivos são disponibilizados no Amazon S3 e processados utilizando os scripts do projeto.

## 12. Evidências

As evidências das consultas realizadas no Amazon Athena estão disponíveis na pasta:

screenshots/

Arquivos:

Total de Pedidos.png
Pedidos Invalidos.png
Anomalias.png
Consulta Metadados.png
Reconciliação.png

As imagens demonstram as consultas de contagem, identificação de anomalias, metadados dos arquivos e reconciliação dos registros.

## 13. Tecnologias utilizadas

Python
Amazon S3
Amazon Athena
Pandas
PyArrow
CSV
JSON
Parquet
Snappy
SQL
Git e GitHub

## 14. Estrutura do projeto

atividade-2-pipeline-dados/
│
├── data/
│   └── ingest_date=2026-09-13/
│       ├── clientes.csv
│       ├── pedidos.csv
│       └── produtos.csv
│
├── screenshots/
│   ├── Anomalias.png
│   ├── Consulta Metadados.png
│   ├── Pedidos Invalidos.png
│   ├── Reconciliação.png
│   └── Total de Pedidos.png
│
├── sql/
│   └── consultas.sql
│
├── src/
│   ├── criar_gold.py
│   ├── criar_silver.py
│   ├── gerar_dados.py
│   └── validar_dados.py
│
└── README.md

## 15. Conclusão

O pipeline implementado contempla as principais etapas solicitadas: ingestão e particionamento dos dados, validação de qualidade, identificação e quarentena de anomalias, transformação para a camada Silver, agregação para a camada Gold e auditoria utilizando o Amazon Athena.

Os resultados obtidos demonstram a consistência do fluxo:

30 pedidos recebidos → 26 pedidos válidos + 4 pedidos rejeitados

O faturamento total de R$ 66.910,00 foi preservado entre as camadas Silver e Gold.