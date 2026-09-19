/**
 * Sistema de Controle Financeiro Pessoal - Front-end
 * Consome a API Flask (/api/...) para registrar e listar
 * lançamentos, e exibir o saldo e o resumo por categoria.
 */

const API_BASE = "/api";

let categoriasCache = [];

// ------------------------------------------------------------
// Utilitários
// ------------------------------------------------------------
function formatarMoeda(valor) {
    return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatarData(dataISO) {
    const [ano, mes, dia] = dataISO.split("-");
    return `${dia}/${mes}/${ano}`;
}

function hoje() {
    const d = new Date();
    const mes = String(d.getMonth() + 1).padStart(2, "0");
    const dia = String(d.getDate()).padStart(2, "0");
    return `${d.getFullYear()}-${mes}-${dia}`;
}

// ------------------------------------------------------------
// Categorias
// ------------------------------------------------------------
async function carregarCategorias() {
    const resposta = await fetch(`${API_BASE}/categorias`);
    categoriasCache = await resposta.json();
}

function atualizarSelectCategorias(tipoSelecionado) {
    const select = document.getElementById("categoria");
    select.innerHTML = "";

    const filtradas = categoriasCache.filter((c) => c.tipo === tipoSelecionado);

    if (filtradas.length === 0) {
        select.innerHTML = '<option value="">Selecione o tipo primeiro...</option>';
        return;
    }

    select.innerHTML = '<option value="">Selecione...</option>';
    filtradas.forEach((categoria) => {
        const opcao = document.createElement("option");
        opcao.value = categoria.id;
        opcao.textContent = categoria.nome;
        select.appendChild(opcao);
    });
}

// ------------------------------------------------------------
// Resumo (saldo + por categoria)
// ------------------------------------------------------------
async function carregarResumo() {
    const resposta = await fetch(`${API_BASE}/resumo`);
    const dados = await resposta.json();

    document.getElementById("totalReceitas").textContent = formatarMoeda(dados.total_receitas);
    document.getElementById("totalDespesas").textContent = formatarMoeda(dados.total_despesas);

    const saldoEl = document.getElementById("saldoAtual");
    saldoEl.textContent = formatarMoeda(dados.saldo);
    saldoEl.style.color = dados.saldo >= 0 ? "var(--cor-receita)" : "var(--cor-despesa)";

    renderizarCategorias(dados.por_categoria);
}

function renderizarCategorias(porCategoria) {
    const container = document.getElementById("listaCategorias");
    const comLancamentos = porCategoria.filter((c) => c.total > 0);

    if (comLancamentos.length === 0) {
        container.innerHTML = '<p class="vazio">Nenhum lançamento cadastrado ainda.</p>';
        return;
    }

    container.innerHTML = comLancamentos
        .map(
            (c) => `
            <div class="item-categoria ${c.tipo}">
                <span class="nome">${c.categoria}</span>
                <span class="valor">${formatarMoeda(c.total)}</span>
            </div>`
        )
        .join("");
}

// ------------------------------------------------------------
// Lançamentos
// ------------------------------------------------------------
async function carregarLancamentos() {
    const tipo = document.getElementById("filtroTipo").value;
    const url = tipo ? `${API_BASE}/lancamentos?tipo=${tipo}` : `${API_BASE}/lancamentos`;

    const resposta = await fetch(url);
    const lancamentos = await resposta.json();

    const corpo = document.getElementById("corpoTabela");

    if (lancamentos.length === 0) {
        corpo.innerHTML = '<tr><td colspan="6" class="vazio">Nenhum lançamento cadastrado ainda.</td></tr>';
        return;
    }

    corpo.innerHTML = lancamentos
        .map(
            (l) => `
            <tr>
                <td>${formatarData(l.data_lancamento)}</td>
                <td>${l.descricao}</td>
                <td>${l.categoria}</td>
                <td><span class="badge ${l.tipo}">${l.tipo === "receita" ? "Receita" : "Despesa"}</span></td>
                <td class="valor-${l.tipo}">${formatarMoeda(l.valor)}</td>
                <td><button class="btn-excluir" title="Excluir" onclick="excluirLancamento(${l.id})">🗑️</button></td>
            </tr>`
        )
        .join("");
}

async function excluirLancamento(id) {
    if (!confirm("Deseja realmente excluir este lançamento?")) return;

    const resposta = await fetch(`${API_BASE}/lancamentos/${id}`, { method: "DELETE" });

    if (resposta.ok) {
        await atualizarTudo();
    } else {
        alert("Não foi possível excluir o lançamento.");
    }
}

async function enviarFormulario(evento) {
    evento.preventDefault();

    const form = document.getElementById("formLancamento");
    const mensagemEl = document.getElementById("mensagemForm");

    const dados = {
        descricao: form.descricao.value,
        valor: form.valor.value,
        tipo: form.tipo.value,
        categoria_id: form.categoria_id.value,
        data_lancamento: form.data_lancamento.value,
        observacoes: form.observacoes.value,
    };

    const resposta = await fetch(`${API_BASE}/lancamentos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    });

    const resultado = await resposta.json();

    if (!resposta.ok) {
        mensagemEl.textContent = (resultado.erros || ["Erro ao salvar."]).join(" ");
        mensagemEl.className = "mensagem erro";
        return;
    }

    mensagemEl.textContent = "Lançamento adicionado com sucesso!";
    mensagemEl.className = "mensagem sucesso";
    form.reset();
    document.getElementById("data").value = hoje();
    atualizarSelectCategorias("");

    await atualizarTudo();

    setTimeout(() => {
        mensagemEl.textContent = "";
    }, 3000);
}

// ------------------------------------------------------------
// Inicialização
// ------------------------------------------------------------
async function atualizarTudo() {
    await Promise.all([carregarResumo(), carregarLancamentos()]);
}

document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById("data").value = hoje();

    await carregarCategorias();
    await atualizarTudo();

    document.getElementById("tipo").addEventListener("change", (e) => {
        atualizarSelectCategorias(e.target.value);
    });

    document.getElementById("filtroTipo").addEventListener("change", carregarLancamentos);

    document.getElementById("formLancamento").addEventListener("submit", enviarFormulario);
});
