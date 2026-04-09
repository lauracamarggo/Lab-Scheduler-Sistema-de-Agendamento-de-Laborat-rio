"""
models.py - Módulo de modelos do sistema de agendamento.
Utiliza conceitos de POO: encapsulamento, herança e polimorfismo.
Banco de dados baseado em arquivos CSV.
"""

import csv
import os
from datetime import datetime, date
from abc import ABC, abstractmethod


class BancoDadosCSV:
    """Classe base para persistência em CSV (encapsulamento do acesso a dados)."""

    def __init__(self, arquivo: str, campos: list):
        self._arquivo = arquivo
        self._campos = campos
        self._garantir_arquivo()

    def _garantir_arquivo(self):
        """Cria o arquivo CSV com cabeçalho se não existir."""
        if not os.path.exists(self._arquivo):
            with open(self._arquivo, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self._campos)
                writer.writeheader()

    def ler_todos(self) -> list:
        """Lê todos os registros do CSV."""
        registros = []
        with open(self._arquivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for linha in reader:
                registros.append(linha)
        return registros

    def inserir(self, registro: dict):
        """Insere um novo registro no CSV."""
        with open(self._arquivo, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._campos)
            writer.writerow(registro)

    def salvar_todos(self, registros: list):
        """Reescreve todo o CSV com a lista de registros fornecida."""
        with open(self._arquivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._campos)
            writer.writeheader()
            writer.writerows(registros)


class Entidade(ABC):
    """Classe abstrata base para entidades do sistema (abstração)."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Usuario(Entidade):
    """Representa um usuário do sistema (aluno ou professor)."""

    def __init__(self, id: str, nome: str, ra: str, email: str, tipo: str = "aluno"):
        self._id = id
        self._nome = nome
        self._ra = ra
        self._email = email
        self._tipo = tipo  # "aluno" ou "professor"

    # --- Propriedades (encapsulamento via getters) ---
    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome

    @property
    def ra(self):
        return self._ra

    @property
    def email(self):
        return self._email

    @property
    def tipo(self):
        return self._tipo

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "nome": self._nome,
            "ra": self._ra,
            "email": self._email,
            "tipo": self._tipo
        }

    def __str__(self) -> str:
        return f"Usuario({self._nome}, RA: {self._ra}, Tipo: {self._tipo})"


class Computador(Entidade):
    """Representa um computador da sala."""

    def __init__(self, id: str, numero: int, descricao: str, status: str = "disponivel"):
        self._id = id
        self._numero = numero
        self._descricao = descricao
        self._status = status  # "disponivel", "manutencao"

    @property
    def id(self):
        return self._id

    @property
    def numero(self):
        return self._numero

    @property
    def descricao(self):
        return self._descricao

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, novo_status: str):
        if novo_status in ("disponivel", "manutencao"):
            self._status = novo_status
        else:
            raise ValueError("Status inválido. Use 'disponivel' ou 'manutencao'.")

    def esta_disponivel(self) -> bool:
        """Verifica se o computador está disponível para agendamento."""
        return self._status == "disponivel"

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "numero": str(self._numero),
            "descricao": self._descricao,
            "status": self._status
        }

    def __str__(self) -> str:
        return f"PC-{self._numero:02d} ({self._status})"


class Agendamento(Entidade):
    """Representa um agendamento de computador."""

    def __init__(self, id: str, usuario_nome: str, usuario_ra: str,
                 computador_id: str, computador_numero: str,
                 data: str, horario_inicio: str, horario_fim: str,
                 status: str = "ativo"):
        self._id = id
        self._usuario_nome = usuario_nome
        self._usuario_ra = usuario_ra
        self._computador_id = computador_id
        self._computador_numero = computador_numero
        self._data = data
        self._horario_inicio = horario_inicio
        self._horario_fim = horario_fim
        self._status = status  # "ativo", "cancelado", "concluido"

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, novo_status: str):
        if novo_status in ("ativo", "cancelado", "concluido"):
            self._status = novo_status

    def tem_conflito(self, data: str, horario_inicio: str, horario_fim: str, computador_id: str) -> bool:
        """Verifica se há conflito de horário com outro agendamento (polimorfismo de lógica)."""
        if self._status != "ativo":
            return False
        if self._data != data or self._computador_id != computador_id:
            return False
        # Verifica sobreposição de horários
        return not (horario_fim <= self._horario_inicio or horario_inicio >= self._horario_fim)

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "usuario_nome": self._usuario_nome,
            "usuario_ra": self._usuario_ra,
            "computador_id": self._computador_id,
            "computador_numero": self._computador_numero,
            "data": self._data,
            "horario_inicio": self._horario_inicio,
            "horario_fim": self._horario_fim,
            "status": self._status
        }

    def __str__(self) -> str:
        return (f"Agendamento(PC-{self._computador_numero}, "
                f"{self._data} {self._horario_inicio}-{self._horario_fim}, "
                f"Status: {self._status})")


# =============================================
# REPOSITÓRIOS — camada de acesso a dados (DAO)
# =============================================

class RepositorioComputadores:
    """Gerencia a persistência de computadores."""

    CAMPOS = ["id", "numero", "descricao", "status"]

    def __init__(self, caminho_csv: str):
        self._db = BancoDadosCSV(caminho_csv, self.CAMPOS)
        self._inicializar_computadores()

    def _inicializar_computadores(self):
        """Cria computadores padrão se o CSV estiver vazio."""
        registros = self._db.ler_todos()
        if len(registros) == 0:
            for i in range(1, 21):  # 20 computadores
                pc = Computador(
                    id=f"pc-{i:02d}",
                    numero=i,
                    descricao=f"Desktop Dell OptiPlex - Sala 101",
                    status="disponivel"
                )
                self._db.inserir(pc.to_dict())

    def listar_todos(self) -> list:
        return self._db.ler_todos()

    def buscar_por_id(self, pc_id: str) -> dict:
        for reg in self._db.ler_todos():
            if reg["id"] == pc_id:
                return reg
        return None


class RepositorioAgendamentos:
    """Gerencia a persistência de agendamentos."""

    CAMPOS = ["id", "usuario_nome", "usuario_ra", "computador_id",
              "computador_numero", "data", "horario_inicio", "horario_fim", "status"]

    def __init__(self, caminho_csv: str):
        self._db = BancoDadosCSV(caminho_csv, self.CAMPOS)

    def listar_todos(self) -> list:
        return self._db.ler_todos()

    def listar_por_data(self, data: str) -> list:
        return [r for r in self._db.ler_todos() if r["data"] == data and r["status"] == "ativo"]

    def listar_por_ra(self, ra: str) -> list:
        return [r for r in self._db.ler_todos() if r["usuario_ra"] == ra]

    def criar(self, agendamento: Agendamento) -> dict:
        """Cria um novo agendamento após verificar conflitos."""
        registros = self._db.ler_todos()

        # Verificar conflitos
        for reg in registros:
            ag_existente = Agendamento(**reg)
            if ag_existente.tem_conflito(
                agendamento.to_dict()["data"],
                agendamento.to_dict()["horario_inicio"],
                agendamento.to_dict()["horario_fim"],
                agendamento.to_dict()["computador_id"]
            ):
                return {"erro": "Conflito de horário! Este computador já está reservado neste período."}

        self._db.inserir(agendamento.to_dict())
        return {"sucesso": True, "agendamento": agendamento.to_dict()}

    def cancelar(self, agendamento_id: str) -> bool:
        """Cancela um agendamento pelo ID."""
        registros = self._db.ler_todos()
        for reg in registros:
            if reg["id"] == agendamento_id:
                reg["status"] = "cancelado"
                self._db.salvar_todos(registros)
                return True
        return False
