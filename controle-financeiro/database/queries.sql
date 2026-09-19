-- ============================================================
-- Consultas úteis para o Sistema de Controle Financeiro Pessoal
-- Estas consultas também são usadas internamente pelo backend
-- (app.py), mas ficam aqui documentadas para consulta manual
-- direto no MySQL.
-- ============================================================

USE controle_financeiro;

-- 1) Saldo geral (total de receitas - total de despesas)
SELECT
    COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) AS total_receitas,
    COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) AS total_despesas,
    COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END), 0) AS saldo
FROM lancamentos;

-- 2) Total de gastos (despesas) agrupado por categoria
SELECT
    c.nome AS categoria,
    COUNT(l.id) AS quantidade_lancamentos,
    SUM(l.valor) AS total
FROM lancamentos l
JOIN categorias c ON c.id = l.categoria_id
WHERE l.tipo = 'despesa'
GROUP BY c.nome
ORDER BY total DESC;

-- 3) Total de receitas agrupado por categoria
SELECT
    c.nome AS categoria,
    COUNT(l.id) AS quantidade_lancamentos,
    SUM(l.valor) AS total
FROM lancamentos l
JOIN categorias c ON c.id = l.categoria_id
WHERE l.tipo = 'receita'
GROUP BY c.nome
ORDER BY total DESC;

-- 4) Saldo por categoria (receitas - despesas de cada categoria)
SELECT
    c.nome AS categoria,
    c.tipo,
    COALESCE(SUM(l.valor), 0) AS total
FROM categorias c
LEFT JOIN lancamentos l ON l.categoria_id = c.id
GROUP BY c.id, c.nome, c.tipo
ORDER BY c.tipo, total DESC;

-- 5) Resumo mensal (receitas, despesas e saldo por mês)
SELECT
    DATE_FORMAT(data_lancamento, '%Y-%m') AS mes,
    SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) AS receitas,
    SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) AS despesas,
    SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END) AS saldo
FROM lancamentos
GROUP BY mes
ORDER BY mes DESC;

-- 6) Últimos 10 lançamentos registrados
SELECT
    l.id,
    l.descricao,
    l.valor,
    l.tipo,
    c.nome AS categoria,
    l.data_lancamento
FROM lancamentos l
JOIN categorias c ON c.id = l.categoria_id
ORDER BY l.data_lancamento DESC, l.id DESC
LIMIT 10;
