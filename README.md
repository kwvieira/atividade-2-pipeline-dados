# Atividade 2 - Pipeline de Dados

## Objetivo

Construção de um pipeline completo de dados utilizando Amazon S3 e Amazon Athena, seguindo a arquitetura Medallion (Raw, Silver e Gold).

O pipeline realiza geração de dados, ingestão, validação de qualidade, tratamento de anomalias em quarentena, transformação e agregação analítica.

## Arquitetura

O fluxo implementado é:

Dados simulados → Raw → Data Quality → Quarantine → Silver → Gold → Athena

## Camada Raw

Os dados de clientes, produtos e pedidos são gerados em formato CSV e armazenados no Amazon S3 utilizando particionamento Hive por data de ingestão.

Estrutura:

```text
raw/
├── clientes/
│   └── ingest_date=YYYY-MM-DD/
├── produtos/
│   └── ingest_date=YYYY-MM-DD/
└── pedidos/
    └── ingest_date=YYYY-MM-DD/

   
   
   
    Data Quality

Foram implementadas regras para identificar registros inválidos:

quantidade menor ou igual a zero;
cliente inexistente;
produto inexistente.

Foram gerados 30 pedidos, sendo 26 válidos e 4 rejeitados.

Quarentena

Os registros inválidos são armazenados em formato JSON juntamente com o motivo da rejeição.

Estrutura:

quarantine/
└── pedidos_rejeitados/
    └── data=YYYY-MM-DD/
        └── rejeitados.json
Camada Silver

Os pedidos válidos são enriquecidos através do relacionamento com as tabelas de clientes e produtos.

Foi calculado o campo:

valor_total = quantidade * preco

Os dados são armazenados em formato Parquet com compressão Snappy.

Local:

processed/fato_vendas/
Camada Gold

A camada Gold realiza uma agregação das vendas por UF e categoria.

As métricas utilizadas são:

quantidade de vendas;
quantidade de itens;
faturamento.

Os dados são armazenados em formato Parquet com compressão Snappy.

Local:

gold/vendas_por_uf_categoria/
Dados utilizados

Foram gerados:

8 clientes;
5 produtos;
30 pedidos.

Foram inseridas propositalmente 4 anomalias:

Pedido	Anomalia
5	quantidade igual a -2
10	cliente_id inexistente
15	product_id inexistente
20	quantidade igual a 0

Resultado da validação:

Pedidos recebidos: 30
Pedidos válidos: 26
Pedidos rejeitados: 4
Tecnologias
Python
Pandas
PyArrow
Amazon S3
Amazon Athena
Parquet
Snappy
SQL
Scripts
gerar_dados.py

Gera os dados simulados de clientes, produtos e pedidos, incluindo anomalias propositalmente.

validar_dados.py

Aplica as regras de Data Quality, separando registros válidos e inválidos e enviando os registros rejeitados para a quarentena.

criar_silver.py

Realiza o enriquecimento dos pedidos válidos com clientes e produtos e calcula o valor total das vendas.

criar_gold.py

Realiza a agregação das vendas por UF e categoria.

Execução

Os scripts podem ser executados na seguinte ordem:

python src/gerar_dados.py
python src/validar_dados.py
python src/criar_silver.py
python src/criar_gold.py
Amazon S3

Bucket utilizado:

atividade-2-pipeline-dados-2026-10782188

Estrutura principal:

raw/
quarantine/
processed/
gold/
athena-results/

Os dados da camada Raw estão particionados pela data:

ingest_date=2026-09-13
Amazon Athena

Foi criado o banco de dados:

atividade2_db

Foram criadas tabelas externas para consulta dos dados armazenados no Amazon S3.

Foram realizadas consultas para:

verificar a quantidade total de pedidos;
identificar pedidos inválidos;
consultar as anomalias e seus motivos;
verificar os metadados utilizando $path e $file_size;
realizar a reconciliação dos dados.

A reconciliação realizada foi:

30 pedidos = 26 válidos + 4 rejeitados
Resultado do processamento

A camada Silver processou 26 pedidos válidos.

O faturamento total calculado foi:

R$ 66.910,00

A camada Gold apresenta o faturamento agregado por UF e categoria.

Evidências

As evidências das consultas realizadas no Amazon Athena estão armazenadas na pasta:

screenshots/

Arquivos:

Total de Pedidos.png
Pedidos Invalidos.png
Anomalias.png
Consulta Metadados.png
Reconciliação.png
Estrutura do projeto
atividade-2-pipeline-dados/
├── README.md
├── data/
├── screenshots/
│   ├── Total de Pedidos.png
│   ├── Pedidos Invalidos.png
│   ├── Anomalias.png
│   ├── Consulta Metadados.png
│   └── Reconciliação.png
├── sql/
│   └── consultas.sql
└── src/
    ├── gerar_dados.py
    ├── validar_dados.py
    ├── criar_silver.py
    └── criar_gold.py

### 4. Salve

Pressione:

**Ctrl + S**

Depois, no terminal, rode novamente:

```powershell
Get-Content .\README.md | Measure-Object -Character