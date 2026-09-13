import boto3
import csv
import json
from io import StringIO
from datetime import date

BUCKET = "atividade-2-pipeline-dados-2026-10782188"
DATA = date.today().isoformat()

s3 = boto3.client("s3")

def ler_csv(caminho):
    resposta = s3.get_object(Bucket=BUCKET, Key=caminho)
    conteudo = resposta["Body"].read().decode("utf-8")
    return list(csv.DictReader(StringIO(conteudo)))

clientes = ler_csv(
    f"raw/clientes/ingest_date={DATA}/clientes.csv"
)

produtos = ler_csv(
    f"raw/produtos/ingest_date={DATA}/produtos.csv"
)

pedidos = ler_csv(
    f"raw/pedidos/ingest_date={DATA}/pedidos.csv"
)

clientes_validos = {int(c["cliente_id"]) for c in clientes}
produtos_validos = {int(p["product_id"]) for p in produtos}

pedidos_validos = []
pedidos_rejeitados = []

for pedido in pedidos:
    motivos = []

    quantidade = int(pedido["quantidade"])
    cliente_id = int(pedido["cliente_id"])
    product_id = int(pedido["product_id"])

    if quantidade <= 0:
        motivos.append("quantidade <= 0")

    if cliente_id not in clientes_validos:
        motivos.append("cliente_id inexistente")

    if product_id not in produtos_validos:
        motivos.append("product_id inexistente")

    if motivos:
        pedidos_rejeitados.append({
            **pedido,
            "motivo_rejeicao": motivos
        })
    else:
        pedidos_validos.append(pedido)

# Salva os pedidos rejeitados em JSON na camada Quarantine
chave_quarantine = (
    f"quarantine/pedidos_rejeitados/"
    f"data={DATA}/rejeitados.json"
)

s3.put_object(
    Bucket=BUCKET,
    Key=chave_quarantine,
    Body=json.dumps(
        pedidos_rejeitados,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8"),
    ContentType="application/json"
)

# Salva os pedidos válidos em CSV temporário para a próxima etapa
csv_buffer = StringIO()

campos = [
    "pedido_id",
    "cliente_id",
    "product_id",
    "quantidade"
]

escritor = csv.DictWriter(
    csv_buffer,
    fieldnames=campos
)

escritor.writeheader()
escritor.writerows(pedidos_validos)

chave_validos = (
    f"processed/pedidos_validos/"
    f"ingest_date={DATA}/pedidos_validos.csv"
)

s3.put_object(
    Bucket=BUCKET,
    Key=chave_validos,
    Body=csv_buffer.getvalue().encode("utf-8"),
    ContentType="text/csv"
)

print("==========================================")
print("DATA QUALITY CONCLUÍDO")
print("==========================================")
print(f"Pedidos recebidos: {len(pedidos)}")
print(f"Pedidos válidos: {len(pedidos_validos)}")
print(f"Pedidos rejeitados: {len(pedidos_rejeitados)}")
print()
print("Arquivo de quarentena:")
print(f"s3://{BUCKET}/{chave_quarantine}")
print()
print("Arquivo com pedidos válidos:")
print(f"s3://{BUCKET}/{chave_validos}")
print("==========================================")
