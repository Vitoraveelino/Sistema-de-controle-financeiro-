-- ============================================================
-- Sistema de Controle Financeiro Pessoal
-- Script de criação do banco de dados (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS controle_financeiro
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE controle_financeiro;

-- ------------------------------------------------------------
-- Tabela: categorias
-- Armazena as categorias usadas para classificar os lançamentos
-- (ex.: Alimentação, Transporte, Salário, Lazer...)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    tipo ENUM('receita', 'despesa') NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabela: lancamentos
-- Armazena cada movimentação financeira (receita ou despesa)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lancamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    valor DECIMAL(12, 2) NOT NULL,
    tipo ENUM('receita', 'despesa') NOT NULL,
    categoria_id INT NOT NULL,
    data_lancamento DATE NOT NULL,
    observacoes VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Índices para acelerar as consultas mais comuns
CREATE INDEX idx_lancamentos_data ON lancamentos (data_lancamento);
CREATE INDEX idx_lancamentos_categoria ON lancamentos (categoria_id);
CREATE INDEX idx_lancamentos_tipo ON lancamentos (tipo);

-- ------------------------------------------------------------
-- Categorias iniciais (podem ser ajustadas livremente)
-- ------------------------------------------------------------
INSERT INTO categorias (nome, tipo) VALUES
    ('Salário', 'receita'),
    ('Freelance', 'receita'),
    ('Investimentos', 'receita'),
    ('Outras Receitas', 'receita'),
    ('Alimentação', 'despesa'),
    ('Transporte', 'despesa'),
    ('Moradia', 'despesa'),
    ('Saúde', 'despesa'),
    ('Educação', 'despesa'),
    ('Lazer', 'despesa'),
    ('Assinaturas', 'despesa'),
    ('Outras Despesas', 'despesa')
ON DUPLICATE KEY UPDATE nome = nome;
