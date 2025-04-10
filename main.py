import os
import requests
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Conexão com o MySQL
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
)
cursor = conn.cursor(dictionary=True)

# Busca usuários com CEP preenchido
cursor.execute(
    "SELECT id_usuario, cep_usuario FROM usuarios WHERE cep_usuario IS NOT NULL AND cep_usuario != ''"
)
usuarios = cursor.fetchall()

for usuario in usuarios:
    cep = "".join(filter(str.isdigit, usuario["cep_usuario"]))  # Somente números

    if len(cep) != 8:
        print(
            f"CEP inválido ({usuario['cep_usuario']}) para ID {usuario['id_usuario']}"
        )
        continue

    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        data = response.json()

        if "bairro" in data and data["bairro"]:
            bairro = data["bairro"]
            print(f"Atualizando ID {usuario['id_usuario']} com bairro: {bairro}")
            update_sql = "UPDATE usuarios SET bairro_usuario = %s WHERE id_usuario = %s"
            cursor.execute(update_sql, (bairro, usuario["id_usuario"]))
            conn.commit()
        else:
            print(
                f"Bairro não encontrado para o CEP {cep} (ID {usuario['id_usuario']})"
            )

    except Exception as e:
        print(f"Erro ao consultar o CEP {cep}: {str(e)}")

# Fecha conexão
cursor.close()
conn.close()
