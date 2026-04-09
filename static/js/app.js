/**
 * app.js — UNIFIEO Lab Booking
 * Lógica do frontend: navegação SPA, chamadas à API, renderização.
 */

// =============================
// CONFIGURAÇÃO E ESTADO GLOBAL
// =============================

const API = "";  // Base URL da API (mesmo servidor)
let secaoAtual = "dashboard";

// =============================
// INICIALIZAÇÃO
// =============================

document.addEventListener("DOMContentLoaded", () => {
    atualizarDataHeader();
    carregarDashboard();
    preencherSelectComputadores();
    preencherSelectHorarios();
    definirDataMinima();
});

function atualizarDataHeader() {
    const agora = new Date();
    const opcoes = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
    document.getElementById("headerDate").textContent =
        agora.toLocaleDateString("pt-BR", opcoes);
}

function definirDataMinima() {
    const hoje = new Date().toISOString().split("T")[0];
    document.getElementById("data").setAttribute("min", hoje);
    document.getElementById("data").value = hoje;
}

// =============================
// NAVEGAÇÃO SPA
// =============================

function navegarPara(secao) {
    // Esconder todas as seções
    document.querySelectorAll(".section").forEach(s => s.classList.add("section--hidden"));

    // Remover classe ativa dos links
    document.querySelectorAll(".sidebar__link").forEach(l => l.classList.remove("sidebar__link--active"));

    // Mostrar seção selecionada
    const mapa = {
        dashboard: "secaoDashboard",
        agendar: "secaoAgendar",
        meus: "secaoMeus",
        mapa: "secaoMapa"
    };
    const titulos = {
        dashboard: "Dashboard",
        agendar: "Novo Agendamento",
        meus: "Meus Agendamentos",
        mapa: "Mapa da Sala"
    };

    const secaoEl = document.getElementById(mapa[secao]);
    if (secaoEl) {
        secaoEl.classList.remove("section--hidden");
    }

    // Ativar link correspondente
    const linkAtivo = document.querySelector(`[data-section="${secao}"]`);
    if (linkAtivo) linkAtivo.classList.add("sidebar__link--active");

    // Atualizar título do header
    document.getElementById("headerTitle").textContent = titulos[secao] || "Dashboard";

    secaoAtual = secao;

    // Carregar dados da seção
    if (secao === "dashboard") carregarDashboard();
    if (secao === "mapa") carregarMapa();
}

// =============================
// DASHBOARD
// =============================

async function carregarDashboard() {
    try {
        // Carregar status
        const resStatus = await fetch(`${API}/api/status`);
        const status = await resStatus.json();

        document.getElementById("statTotal").textContent = status.total_computadores;
        document.getElementById("statDisponiveis").textContent = status.computadores_disponiveis;
        document.getElementById("statHoje").textContent = status.agendamentos_hoje;
        document.getElementById("statAtivos").textContent = status.agendamentos_ativos;

        // Carregar agendamentos recentes
        const resAg = await fetch(`${API}/api/agendamentos`);
        const agendamentos = await resAg.json();

        renderizarTabelaRecentes(agendamentos.slice(-10).reverse());
    } catch (err) {
        console.error("Erro ao carregar dashboard:", err);
    }
}

function renderizarTabelaRecentes(agendamentos) {
    const tbody = document.getElementById("tabelaRecentes");

    if (agendamentos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="table__empty">Nenhum agendamento encontrado.</td></tr>`;
        return;
    }

    tbody.innerHTML = agendamentos.map(ag => `
        <tr>
            <td style="font-family:var(--mono); font-size:.75rem;">${ag.id}</td>
            <td>${ag.usuario_nome}</td>
            <td style="font-family:var(--mono);">${ag.usuario_ra}</td>
            <td>PC-${String(ag.computador_numero).padStart(2, '0')}</td>
            <td>${formatarData(ag.data)}</td>
            <td>${ag.horario_inicio} – ${ag.horario_fim}</td>
            <td><span class="badge badge--${ag.status}">${ag.status}</span></td>
        </tr>
    `).join("");
}

// =============================
// FORMULÁRIO DE AGENDAMENTO
// =============================

async function preencherSelectComputadores() {
    try {
        const res = await fetch(`${API}/api/computadores`);
        const computadores = await res.json();
        const select = document.getElementById("computador");

        computadores.forEach(pc => {
            if (pc.status === "disponivel") {
                const opt = document.createElement("option");
                opt.value = pc.id;
                opt.textContent = `PC-${String(pc.numero).padStart(2, '0')} — ${pc.descricao}`;
                select.appendChild(opt);
            }
        });
    } catch (err) {
        console.error("Erro ao carregar computadores:", err);
    }
}

function preencherSelectHorarios() {
    const selectInicio = document.getElementById("horarioInicio");
    const selectFim = document.getElementById("horarioFim");

    // Horários de funcionamento: 07:00 às 22:00
    for (let h = 7; h <= 21; h++) {
        for (let m = 0; m < 60; m += 30) {
            const horario = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
            selectInicio.innerHTML += `<option value="${horario}">${horario}</option>`;

            const horarioFim = `${String(m === 30 ? h + 1 : h).padStart(2, '0')}:${String(m === 30 ? 0 : 30).toString().padStart(2, '0')}`;
        }
    }

    for (let h = 7; h <= 22; h++) {
        for (let m = 0; m < 60; m += 30) {
            if (h === 22 && m > 0) break;
            const horario = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
            selectFim.innerHTML += `<option value="${horario}">${horario}</option>`;
        }
    }
}

async function criarAgendamento(event) {
    event.preventDefault();

    const dados = {
        usuario_nome: document.getElementById("nome").value.trim(),
        usuario_ra: document.getElementById("ra").value.trim(),
        computador_id: document.getElementById("computador").value,
        data: document.getElementById("data").value,
        horario_inicio: document.getElementById("horarioInicio").value,
        horario_fim: document.getElementById("horarioFim").value
    };

    // Validação no frontend
    if (dados.horario_fim <= dados.horario_inicio) {
        mostrarToast("Horário final deve ser depois do inicial!", "error");
        return false;
    }

    try {
        const res = await fetch(`${API}/api/agendamentos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        const resultado = await res.json();

        if (res.ok) {
            mostrarToast("Agendamento criado com sucesso!", "success");
            document.getElementById("formAgendamento").reset();
            definirDataMinima();
            setTimeout(() => navegarPara("dashboard"), 800);
        } else {
            mostrarToast(resultado.erro || "Erro ao criar agendamento", "error");
        }
    } catch (err) {
        mostrarToast("Erro de conexão com o servidor", "error");
        console.error(err);
    }

    return false;
}

// =============================
// MEUS AGENDAMENTOS
// =============================

async function buscarMeusAgendamentos() {
    const ra = document.getElementById("buscaRA").value.trim();
    if (!ra) {
        mostrarToast("Informe seu RA para buscar", "error");
        return;
    }

    try {
        const res = await fetch(`${API}/api/agendamentos?ra=${encodeURIComponent(ra)}`);
        const agendamentos = await res.json();
        renderizarTabelaMeus(agendamentos);
    } catch (err) {
        console.error("Erro ao buscar agendamentos:", err);
    }
}

function renderizarTabelaMeus(agendamentos) {
    const tbody = document.getElementById("tabelaMeus");

    if (agendamentos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="table__empty">Nenhum agendamento encontrado para este RA.</td></tr>`;
        return;
    }

    tbody.innerHTML = agendamentos.map(ag => `
        <tr>
            <td style="font-family:var(--mono); font-size:.75rem;">${ag.id}</td>
            <td>PC-${String(ag.computador_numero).padStart(2, '0')}</td>
            <td>${formatarData(ag.data)}</td>
            <td>${ag.horario_inicio} – ${ag.horario_fim}</td>
            <td><span class="badge badge--${ag.status}">${ag.status}</span></td>
            <td>
                ${ag.status === "ativo"
                    ? `<button class="btn btn--danger btn--sm" onclick="cancelarAgendamento('${ag.id}')">Cancelar</button>`
                    : "—"
                }
            </td>
        </tr>
    `).join("");
}

async function cancelarAgendamento(id) {
    if (!confirm("Tem certeza que deseja cancelar este agendamento?")) return;

    try {
        const res = await fetch(`${API}/api/agendamentos/${id}/cancelar`, { method: "PUT" });
        const resultado = await res.json();

        if (res.ok) {
            mostrarToast("Agendamento cancelado!", "success");
            buscarMeusAgendamentos();  // Recarregar a lista
        } else {
            mostrarToast(resultado.erro || "Erro ao cancelar", "error");
        }
    } catch (err) {
        mostrarToast("Erro de conexão", "error");
    }
}

// =============================
// MAPA DA SALA
// =============================

async function carregarMapa() {
    try {
        const [resPC, resAg] = await Promise.all([
            fetch(`${API}/api/computadores`),
            fetch(`${API}/api/agendamentos?data=${new Date().toISOString().split("T")[0]}`)
        ]);

        const computadores = await resPC.json();
        const agendamentosHoje = await resAg.json();

        // IDs dos computadores ocupados hoje
        const ocupados = new Set(agendamentosHoje.map(a => a.computador_id));

        const container = document.getElementById("mapaSala");
        container.innerHTML = computadores.map(pc => {
            let classe = "sala-pc--livre";
            let statusTexto = "Livre";

            if (pc.status === "manutencao") {
                classe = "sala-pc--manutencao";
                statusTexto = "Manutenção";
            } else if (ocupados.has(pc.id)) {
                classe = "sala-pc--ocupado";
                statusTexto = "Ocupado";
            }

            return `
                <div class="sala-pc ${classe}" 
                     onclick="${classe !== 'sala-pc--manutencao' ? `selecionarPC('${pc.id}')` : ''}"
                     title="PC-${String(pc.numero).padStart(2, '0')} — ${statusTexto}">
                    <span class="sala-pc__icon">🖥</span>
                    <span class="sala-pc__label">PC-${String(pc.numero).padStart(2, '0')}</span>
                    <span class="sala-pc__status">${statusTexto}</span>
                </div>
            `;
        }).join("");
    } catch (err) {
        console.error("Erro ao carregar mapa:", err);
    }
}

function selecionarPC(pcId) {
    document.getElementById("computador").value = pcId;
    navegarPara("agendar");
    mostrarToast("Computador selecionado! Preencha os demais dados.", "success");
}

// =============================
// UTILIDADES
// =============================

function formatarData(dataStr) {
    const [ano, mes, dia] = dataStr.split("-");
    return `${dia}/${mes}/${ano}`;
}

function mostrarToast(mensagem, tipo = "success") {
    const toast = document.getElementById("toast");
    toast.textContent = mensagem;
    toast.className = `toast toast--show toast--${tipo}`;

    setTimeout(() => {
        toast.classList.remove("toast--show");
    }, 3000);
}
