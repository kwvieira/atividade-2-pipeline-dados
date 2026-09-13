import csv
import random
from datetime import date
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

DATA_INGESTAO = date.today().isoformat()

PASTA_DATA = Path("data") / f"ingest_date={DATA_INGESTAO}"
PASTA_DATA.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. GERAÇÃO DOS CLIENTES
# ============================================================

clientes = [
    {"cliente_id": 1, "nome": "Ana Silva", "uf": "MG"},
    {"cliente_id": 2, "nome": "Bruno Santos", "uf": "SP"},
    {"cliente_id": 3, "nome": "Carla Oliveira", "uf": "RJ"},
    {"cliente_id": 4, "nome": "Daniel Souza", "uf": "BA"},
    {"cliente_id": 5, "nome": "Fernanda Lima", "uf": "MG"},
    {"cliente_id": 6, "nome": "Gabriel Costa", "uf": "SP"},
    {"cliente_id": 7, "nome": "Juliana Alves", "uf": "PR"},
    {"cliente_id": 8, "nome": "Lucas Pereira", "uf": "RJ"},
]


# ============================================================
# 2. GERAÇÃO DOS PRODUTOS
# ============================================================

produtos = [
    {
        "product_id": 101,
        "produto": "Notebook",
        "categoria": "Eletronicos",
        "preco": 3500.00
    },
    {
        "product_id": 102,
        "produto": "Celular",
        "categoria": "Eletronicos",
        "preco": 2200.00
    },
    {
        "product_id": 103,
        "produto": "Camisa",
        "categoria": "Vestuario",
        "preco": 100.00
    },
    {
        "product_id": 104,
        "produto": "Tenis",
        "categoria": "Calcados",
        "preco": 250.00
    },
    {
        "product_id": 105,
        "produto": "Mochila",
        "categoria": "Acessorios",
        "preco": 180.00
    },
]


# ============================================================
# 3. GERAÇÃO DOS PEDIDOS
# ============================================================

pedidos = []

for pedido_id in range(1, 31):

    cliente = random.choice(clientes)
    produto = random.choice(produtos)
    quantidade = random.randint(1, 5)

    pedido = {
        "pedido_id": pedido_id,
        "cliente_id": cliente["cliente_id"],
        "product_id": produto["product_id"],
        "quantidade": quantidade
    }

    pedidos.append(pedido)


# ============================================================
# 4. INSERÇÃO INTENCIONAL DE ANOMALIAS
# ============================================================

# Pedido com quantidade negativa
pedidos[4]["quantidade"] = -2

# Pedido com cliente inexistente
pedidos[9]["cliente_id"] = 999

# Pedido com produto inexistente
pedidos[14]["product_id"] = 999

# Outro pedido com quantidade zero
pedidos[19]["quantidade"] = 0


# ============================================================
# 5. FUNÇÃO PARA SALVAR CSV
# ============================================================

def salvar_csv(nome_arquivo, dados, colunas):

    caminho = PASTA_DATA / nome_arquivo

    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas
        )

        escritor.writeheader()
        escritor.writerows(dados)

    print(f"Arquivo criado: {caminho}")


# ============================================================
# 6. SALVANDO OS ARQUIVOS
# ============================================================

salvar_csv(
    "clientes.csv",
    clientes,
    ["cliente_id", "nome", "uf"]
)

salvar_csv(
    "produtos.csv",
    produtos,
    ["product_id", "produto", "categoria", "preco"]
)

salvar_csv(
    "pedidos.csv",
    pedidos,
    ["pedido_id", "cliente_id", "product_id", "quantidade"]
)


# ============================================================
# 7. MENSAGEM FINAL
# ============================================================

print()
print("==========================================")
print("GERAÇÃO DOS DADOS CONCLUÍDA!")
print("==========================================")
print(f"Data de ingestão: {DATA_INGESTAO}")
print(f"Quantidade de clientes: {len(clientes)}")
print(f"Quantidade de produtos: {len(produtos)}")
print(f"Quantidade de pedidos: {len(pedidos)}")
print("Anomalias inseridas: 4")
print("==========================================")