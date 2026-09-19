"""
Sistema de Controle Financeiro Pessoal
---------------------------------------
Aplicação Flask que expõe uma API para registrar e consultar
receitas e despesas, organizadas por categoria, com os dados
armazenados em um banco de dados MySQL.

Como executar:
    1. Configure o banco (veja database/schema.sql)
    2. Copie .env.example para .env e preencha suas credenciais
    3. pip install -r requirements.txt
    4. python app.py
    5. Acesse http://localhost:5000
"""

import os
from datetime import date

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/static")


# ------------------------------------------------------------------
# Rotas de páginas (front-end)
# ------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ------------------------------------------------------------------
# Rotas de API - Categorias
# ------------------------------------------------------------------
@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    conexao = get_connection()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, tipo FROM categorias ORDER BY tipo, nome")
    categorias = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(categorias)


# ------------------------------------------------------------------
# Rotas de API - Lançamentos (receitas e despesas)
# ------------------------------------------------------------------
@app.route("/api/lancamentos", methods=["GET"])
def listar_lancamentos():
    """Lista lançamentos, com filtros opcionais via query string:
    ?tipo=receita|despesa&categoria_id=<id>&mes=YYYY-MM
    """
    tipo = request.args.get("tipo")
    categoria_id = request.args.get("categoria_id")
    mes = request.args.get("mes")

    sql = """
        SELECT l.id, l.descricao, l.valor, l.tipo, l.categoria_id,
               c.nome AS categoria, l.data_lancamento, l.observacoes
        FROM lancamentos l
        JOIN categorias c ON c.id = l.categoria_id
        WHERE 1 = 1
    """
    parametros = []

    if tipo in ("receita", "despesa"):
        sql += " AND l.tipo = %s"
        parametros.append(tipo)

    if categoria_id:
        sql += " AND l.categoria_id = %s"
        parametros.append(categoria_id)

    if mes:
        sql += " AND DATE_FORMAT(l.data_lancamento, '%%Y-%%m') = %s"
        parametros.append(mes)

    sql += " ORDER BY l.data_lancamento DESC, l.id DESC"

    conexao = get_connection()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(sql, parametros)
    lancamentos = cursor.fetchall()
    cursor.close()
    conexao.close()

    # Converte Decimal e date para tipos serializáveis em JSON
    for item in lancamentos:
        item["valor"] = float(item["valor"])
        item["data_lancamento"] = item["data_lancamento"].isoformat()

    return jsonify(lancamentos)


@app.route("/api/lancamentos", methods=["POST"])
def criar_lancamento():
    dados = request.get_json(silent=True) or {}

    descricao = (dados.get("descricao") or "").strip()
    valor = dados.get("valor")
    tipo = dados.get("tipo")
    categoria_id = dados.get("categoria_id")
    data_lancamento = dados.get("data_lancamento") or date.today().isoformat()
    observacoes = (dados.get("observacoes") or "").strip() or None

    # Validações básicas
    erros = []
    if not descricao:
        erros.append("A descrição é obrigatória.")
    if tipo not in ("receita", "despesa"):
        erros.append("O tipo deve ser 'receita' ou 'despesa'.")
    if not categoria_id:
        erros.append("A categoria é obrigatória.")
    try:
        valor = float(valor)
        if valor <= 0:
            erros.append("O valor deve ser maior que zero.")
    except (TypeError, ValueError):
        erros.append("O valor informado é inválido.")

    if erros:
        return jsonify({"erros": erros}), 400

    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO lancamentos
            (descricao, valor, tipo, categoria_id, data_lancamento, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (descricao, valor, tipo, categoria_id, data_lancamento, observacoes),
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Lançamento registrado com sucesso.", "id": novo_id}), 201


@app.route("/api/lancamentos/<int:lancamento_id>", methods=["DELETE"])
def excluir_lancamento(lancamento_id):
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM lancamentos WHERE id = %s", (lancamento_id,))
    conexao.commit()
    afetados = cursor.rowcount
    cursor.close()
    conexao.close()

    if afetados == 0:
        return jsonify({"erro": "Lançamento não encontrado."}), 404

    return jsonify({"mensagem": "Lançamento excluído com sucesso."})


# ------------------------------------------------------------------
# Rotas de API - Resumo / Saldo
# ------------------------------------------------------------------
@app.route("/api/resumo", methods=["GET"])
def resumo_financeiro():
    """Retorna o saldo geral e o total por categoria."""
    conexao = get_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) AS total_receitas,
            COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) AS total_despesas
        FROM lancamentos
        """
    )
    totais = cursor.fetchone()
    total_receitas = float(totais["total_receitas"])
    total_despesas = float(totais["total_despesas"])

    cursor.execute(
        """
        SELECT c.nome AS categoria, c.tipo, COALESCE(SUM(l.valor), 0) AS total
        FROM categorias c
        LEFT JOIN lancamentos l ON l.categoria_id = c.id
        GROUP BY c.id, c.nome, c.tipo
        ORDER BY c.tipo, total DESC
        """
    )
    por_categoria = cursor.fetchall()
    for item in por_categoria:
        item["total"] = float(item["total"])

    cursor.close()
    conexao.close()

    return jsonify(
        {
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo": total_receitas - total_despesas,
            "por_categoria": por_categoria,
        }
    )


if __name__ == "__main__":
    porta = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=porta, debug=debug)
