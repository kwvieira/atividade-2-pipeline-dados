import boto3
import pandas as pd
from io import BytesIO
from datetime import date

BUCKET = "atividade-2-pipeline-dados-2026-10782188"
DATA = date.today().isoformat()

s3 = boto3.client("s3")

# Ler a camada Silver
chave_silver = (
    f"processed/fato_vendas/"
    f"ingest_date={DATA}/fato_vendas.parquet"
)

resposta = s3.get_object(
    Bucket=BUCKET,
    Key=chave_silver
)

vendas = pd.read_parquet(
    BytesIO(resposta["Body"].read())
)

# Agregar por UF e categoria
gold = (
    vendas
    .groupby(["uf", "categoria"], as_index=False)
    .agg(
        quantidade_vendas=("pedido_id", "count"),
        quantidade_itens=("quantidade", "sum"),
        faturamento=("valor_total", "sum")
    )
)

# Criar arquivo Parquet com Snappy
buffer = BytesIO()

gold.to_parquet(
    buffer,
    index=False,
    engine="pyarrow",
    compression="snappy"
)

buffer.seek(0)

# Salvar na camada Gold
chave_gold = (
    f"gold/vendas_por_uf_categoria/"
    f"data={DATA}/vendas_por_uf_categoria.parquet"
)

s3.put_object(
    Bucket=BUCKET,
    Key=chave_gold,
    Body=buffer.getvalue(),
    ContentType="application/octet-stream"
)

print("==========================================")
print("CAMADA GOLD CONCLUÍDA")
print("==========================================")
print(f"Registros agregados: {len(gold)}")
print()
print(gold.to_string(index=False))
print()
print(f"Faturamento total: R$ {gold['faturamento'].sum():.2f}")
print()
print(f"Arquivo Gold:")
print(f"s3://{BUCKET}/{chave_gold}")
print()
print("Formato: Parquet")
print("Compressão: Snappy")
print("==========================================")
