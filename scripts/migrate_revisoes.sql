
-- Script para criar tabela de revisões e migrar dados do JSON

-- Criar tabela de revisões
CREATE TABLE IF NOT EXISTS revisoes (
    id SERIAL PRIMARY KEY,
    hash VARCHAR(128) NOT NULL UNIQUE,
    id_original VARCHAR(100) NOT NULL,
    nova_descricao TEXT NOT NULL,
    donos JSONB NOT NULL,
    comentarios TEXT,
    pago_por VARCHAR(100),
    quitado BOOLEAN DEFAULT FALSE,
    quitacao_individual JSONB,
    data_revisao TIMESTAMP NOT NULL,
    revisado_por VARCHAR(100),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_revisoes_hash ON revisoes(hash);
CREATE INDEX IF NOT EXISTS idx_revisoes_data_revisao ON revisoes(data_revisao);
CREATE INDEX IF NOT EXISTS idx_revisoes_pago_por ON revisoes(pago_por);
CREATE INDEX IF NOT EXISTS idx_revisoes_quitado ON revisoes(quitado);
CREATE INDEX IF NOT EXISTS idx_revisoes_ativo ON revisoes(ativo);

-- Criar tabela de transações
CREATE TABLE IF NOT EXISTS transacoes (
    id SERIAL PRIMARY KEY,
    transacao_id VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    data DATE NOT NULL,
    descricao TEXT NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    tipo_movimento VARCHAR(20) NOT NULL CHECK (tipo_movimento IN ('entrada', 'saida')),
    fonte VARCHAR(100) NOT NULL,
    hash VARCHAR(128) NOT NULL UNIQUE,
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Criar índices para transações
CREATE INDEX IF NOT EXISTS idx_transacoes_hash ON transacoes(hash);
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);
CREATE INDEX IF NOT EXISTS idx_transacoes_fonte ON transacoes(fonte);
CREATE INDEX IF NOT EXISTS idx_transacoes_ativo ON transacoes(ativo);
CREATE INDEX IF NOT EXISTS idx_transacoes_tipo_movimento ON transacoes(tipo_movimento);
