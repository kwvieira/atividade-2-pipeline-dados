import boto3
import pandas as pd
from io import BytesIO
from datetime import date

BUCKET = "atividade-2-pipeline-dados-2026-10782188"
DATA = date.today().isoformat()

s3 = boto3.client("s3")


def ler_csv(caminho):
    resposta = s3.get_object(Bucket=BUCKET, Key=caminho)
    return pd.read_csv(BytesIO(resposta["Body"].read()))


# 1. Ler os dados
clientes = ler_csv(
    f"raw/clientes/ingest_date={DATA}/clientes.csv"
)

produtos = ler_csv(
    f"raw/produtos/ingest_date={DATA}/produtos.csv"
)

pedidos = ler_csv(
    f"processed/pedidos_validos/ingest_date={DATA}/pedidos_validos.csv"
)


# 2. Juntar pedidos com clientes
vendas = pedidos.merge(
    clientes,
    on="cliente_id",
    how="inner"
)


# 3. Juntar com produtos
vendas = vendas.merge(
    produtos,
    on="product_id",
    how="inner"
)


# 4. Calcular valor total da venda
vendas["valor_total"] = (
    vendas["quantidade"] * vendas["preco"]
)


# 5. Organizar as colunas da camada Silver
vendas = vendas[
    [
        "pedido_id",
        "cliente_id",
        "nome",
        "uf",
        "product_id",
        "produto",
        "categoria",
        "quantidade",
        "preco",
        "valor_total"
    ]
]


# 6. Criar arquivo Parquet com compressão Snappy
buffer = BytesIO()

vendas.to_parquet(
    buffer,
    index=False,
    engine="pyarrow",
    compression="snappy"
)

buffer.seek(0)


# 7. Enviar para o S3
chave_silver = (
    f"processed/fato_vendas/"
    f"ingest_date={DATA}/fato_vendas.parquet"
)

s3.put_object(
    Bucket=BUCKET,
    Key=chave_silver,
    Body=buffer.getvalue(),
    ContentType="application/octet-stream"
)


# 8. Mostrar resultado
print("==========================================")
print("CAMADA SILVER CONCLUÍDA")
print("==========================================")
print(f"Pedidos processados: {len(vendas)}")
print(f"Arquivo Parquet: s3://{BUCKET}/{chave_silver}")
print()
print("Colunas:")
print(", ".join(vendas.columns))
print()
print("Primeiras vendas:")
print(vendas.head().to_string(index=False))
print()
print(f"Valor total das vendas: R$ {vendas['valor_total'].sum():.2f}")
print("Compressão: Snappy")
print("Formato: Parquet")
print("==========================================")
