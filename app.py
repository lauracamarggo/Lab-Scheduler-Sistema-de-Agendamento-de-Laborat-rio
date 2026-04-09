"""
app.py - Aplicação principal Flask.
Sistema de Agendamento de Computadores - UNIFIEO
Inspirado na plataforma DeskBee.
"""

from flask import Flask, render_template, request, jsonify
from models import (
    Computador, Agendamento,
    RepositorioComputadores, RepositorioAgendamentos
)
from datetime import datetime
import uuid
import os

# Configuração da aplicação
app = Flask(__name__)

# Caminhos dos arquivos CSV (banco de dados)
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(PASTA_DADOS, exist_ok=True)

CSV_COMPUTADORES = os.path.join(PASTA_DADOS, "computadores.csv")
CSV_AGENDAMENTOS = os.path.join(PASTA_DADOS, "agendamentos.csv")

# Inicialização dos repositórios (injeção de dependência)
repo_computadores = RepositorioComputadores(CSV_COMPUTADORES)
repo_agendamentos = RepositorioAgendamentos(CSV_AGENDAMENTOS)


# =====================
# ROTAS DE PÁGINAS HTML
# =====================

@app.route("/")
def pagina_inicial():
    """Rota principal — renderiza o dashboard."""
    return render_template("index.html")


# ==============
# ROTAS DA API
# ==============

@app.route("/api/computadores", methods=["GET"])
def api_listar_computadores():
    """Retorna lista de todos os computadores."""
    computadores = repo_computadores.listar_todos()
    return jsonify(computadores)


@app.route("/api/computadores/<pc_id>", methods=["GET"])
def api_buscar_computador(pc_id):
    """Retorna dados de um computador específico."""
    pc = repo_computadores.buscar_por_id(pc_id)
    if pc:
        return jsonify(pc)
    return jsonify({"erro": "Computador não encontrado"}), 404


@app.route("/api/agendamentos", methods=["GET"])
def api_listar_agendamentos():
    """Lista agendamentos, com filtro opcional por data ou RA."""
    data = request.args.get("data")
    ra = request.args.get("ra")

    if data:
        agendamentos = repo_agendamentos.listar_por_data(data)
    elif ra:
        agendamentos = repo_agendamentos.listar_por_ra(ra)
    else:
        agendamentos = repo_agendamentos.listar_todos()

    return jsonify(agendamentos)


@app.route("/api/agendamentos", methods=["POST"])
def api_criar_agendamento():
    """Cria um novo agendamento."""
    dados = request.get_json()

    # Validação básica dos campos obrigatórios
    campos_obrigatorios = ["usuario_nome", "usuario_ra", "computador_id", "data",
                           "horario_inicio", "horario_fim"]
    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo]:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400

    # Buscar dados do computador
    pc = repo_computadores.buscar_por_id(dados["computador_id"])
    if not pc:
        return jsonify({"erro": "Computador não encontrado"}), 404

    if pc["status"] != "disponivel":
        return jsonify({"erro": "Computador em manutenção"}), 400

    # Validar horários
    try:
        h_inicio = datetime.strptime(dados["horario_inicio"], "%H:%M")
        h_fim = datetime.strptime(dados["horario_fim"], "%H:%M")
        if h_fim <= h_inicio:
            return jsonify({"erro": "Horário final deve ser após o horário inicial"}), 400
    except ValueError:
        return jsonify({"erro": "Formato de horário inválido. Use HH:MM"}), 400

    # Criar objeto Agendamento
    agendamento = Agendamento(
        id=str(uuid.uuid4())[:8],
        usuario_nome=dados["usuario_nome"],
        usuario_ra=dados["usuario_ra"],
        computador_id=dados["computador_id"],
        computador_numero=pc["numero"],
        data=dados["data"],
        horario_inicio=dados["horario_inicio"],
        horario_fim=dados["horario_fim"],
        status="ativo"
    )

    resultado = repo_agendamentos.criar(agendamento)

    if "erro" in resultado:
        return jsonify(resultado), 409  # Conflict

    return jsonify(resultado), 201


@app.route("/api/agendamentos/<agendamento_id>/cancelar", methods=["PUT"])
def api_cancelar_agendamento(agendamento_id):
    """Cancela um agendamento existente."""
    sucesso = repo_agendamentos.cancelar(agendamento_id)
    if sucesso:
        return jsonify({"sucesso": True, "mensagem": "Agendamento cancelado com sucesso"})
    return jsonify({"erro": "Agendamento não encontrado"}), 404


# ===========================
# ROTA DE STATUS DO SISTEMA
# ===========================

@app.route("/api/status", methods=["GET"])
def api_status():
    """Retorna estatísticas gerais do sistema."""
    computadores = repo_computadores.listar_todos()
    agendamentos = repo_agendamentos.listar_todos()
    hoje = datetime.now().strftime("%Y-%m-%d")
    agendamentos_hoje = [a for a in agendamentos if a["data"] == hoje and a["status"] == "ativo"]

    return jsonify({
        "total_computadores": len(computadores),
        "computadores_disponiveis": len([c for c in computadores if c["status"] == "disponivel"]),
        "total_agendamentos": len(agendamentos),
        "agendamentos_hoje": len(agendamentos_hoje),
        "agendamentos_ativos": len([a for a in agendamentos if a["status"] == "ativo"])
    })


# =====================
# INICIALIZAÇÃO
# =====================

if __name__ == "__main__":
    print("=" * 50)
    print("  UNIFIEO - Sistema de Agendamento de PCs")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
