"""
Módulo de conexão com o banco de dados MySQL.
Centraliza a criação da conexão para ser reutilizada pelo app.py.
"""

import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Abre e retorna uma nova conexão com o banco MySQL.

    As credenciais são lidas de variáveis de ambiente (veja o
    arquivo .env.example). Isso evita deixar usuário/senha
    fixos no código.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "controle_financeiro"),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            use_unicode=True,
        )
        return connection
    except Error as erro:
        print(f"Erro ao conectar no banco de dados: {erro}")
        raise
