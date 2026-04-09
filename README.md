# 🖥️ UNIFIEO — Sistema de Agendamento de Computadores

Sistema web de agendamento de computadores para o laboratório da faculdade UNIFIEO,
inspirado na plataforma **DeskBee**. Desenvolvido em **Python (Flask)** com boas
práticas de **Programação Orientada a Objetos (POO)** e banco de dados em **CSV**.

---

## 📁 Estrutura do Projeto

```
agendamento/
├── app.py                  # Aplicação principal Flask (rotas e API REST)
├── models.py               # Modelos POO (entidades, repositórios, DAO)
├── data/                   # Banco de dados CSV (gerado automaticamente)
│   ├── computadores.csv
│   └── agendamentos.csv
├── templates/
│   └── index.html          # Página HTML principal (SPA)
├── static/
│   ├── css/
│   │   └── style.css       # Estilos do sistema
│   └── js/
│       └── app.js          # Lógica JavaScript do frontend
└── README.md               # Este arquivo
```

---

## 🧩 Conceitos de POO Aplicados

| Conceito           | Onde é aplicado                                                |
|--------------------|----------------------------------------------------------------|
| **Encapsulamento** | Atributos privados (`_nome`, `_ra`) com `@property` getters   |
| **Abstração**      | Classe abstrata `Entidade` com `ABC` e `@abstractmethod`      |
| **Herança**        | `Usuario`, `Computador` e `Agendamento` herdam de `Entidade`  |
| **Polimorfismo**   | Método `to_dict()` implementado de forma diferente por classe  |
| **Composição**     | Repositórios usam `BancoDadosCSV` internamente                |
| **DAO Pattern**    | `RepositorioComputadores` e `RepositorioAgendamentos`         |

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone ou copie a pasta do projeto** para seu computador.

2. **Instale a dependência Flask:**
   ```bash
   pip install flask
   ```

3. **Execute a aplicação:**
   ```bash
   cd agendamento
   python app.py
   ```

4. **Acesse no navegador:**
   ```
   http://localhost:5000
   ```

> Os arquivos CSV do banco de dados são criados automaticamente na primeira
> execução dentro da pasta `data/`.

---

## 🔌 Rotas da API REST

| Método | Rota                                  | Descrição                         |
|--------|---------------------------------------|-----------------------------------|
| GET    | `/api/computadores`                   | Lista todos os computadores       |
| GET    | `/api/computadores/<id>`              | Busca computador por ID           |
| GET    | `/api/agendamentos`                   | Lista agendamentos (filtros: `?data=` ou `?ra=`) |
| POST   | `/api/agendamentos`                   | Cria novo agendamento             |
| PUT    | `/api/agendamentos/<id>/cancelar`     | Cancela um agendamento            |
| GET    | `/api/status`                         | Estatísticas do sistema           |

### Exemplo de POST (criar agendamento)

```json
{
    "usuario_nome": "João Silva",
    "usuario_ra": "12345",
    "computador_id": "pc-01",
    "data": "2026-03-25",
    "horario_inicio": "08:00",
    "horario_fim": "10:00"
}
```

---

## 🎨 Funcionalidades do Frontend

- **Dashboard** — Visão geral com cards de status e tabela de agendamentos recentes
- **Novo Agendamento** — Formulário completo com validação e seleção de horários
- **Meus Agendamentos** — Busca por RA com opção de cancelamento
- **Mapa da Sala** — Grid visual dos 20 PCs com status em tempo real (livre/ocupado/manutenção)
- **Toasts** — Notificações visuais de sucesso e erro
- **Navegação SPA** — Sem reload de página entre seções

---

## 📊 Banco de Dados (CSV)

### computadores.csv
```csv
id,numero,descricao,status
pc-01,1,Desktop Dell OptiPlex - Sala 101,disponivel
pc-02,2,Desktop Dell OptiPlex - Sala 101,disponivel
...
```

### agendamentos.csv
```csv
id,usuario_nome,usuario_ra,computador_id,computador_numero,data,horario_inicio,horario_fim,status
a1b2c3d4,João Silva,12345,pc-01,1,2026-03-25,08:00,10:00,ativo
```

---

## 👨‍🎓 Informações Acadêmicas

- **Instituição:** Centro Universitário FIEO (UNIFIEO)
- **Disciplina:** Programação Orientada a Objetos
- **Tecnologias:** Python, Flask, HTML5, CSS3, JavaScript, CSV
- **Padrões:** POO, MVC, DAO, API REST, SPA
