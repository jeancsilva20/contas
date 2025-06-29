
-- Script para criar tabela de pendentes e migrar dados do JSON

-- Criar tabela de pendentes
CREATE TABLE IF NOT EXISTS pendentes (
    id SERIAL PRIMARY KEY,
    transacao_id VARCHAR(100) NOT NULL,
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

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_pendentes_hash ON pendentes(hash);
CREATE INDEX IF NOT EXISTS idx_pendentes_data ON pendentes(data);
CREATE INDEX IF NOT EXISTS idx_pendentes_fonte ON pendentes(fonte);
CREATE INDEX IF NOT EXISTS idx_pendentes_ativo ON pendentes(ativo);
CREATE INDEX IF NOT EXISTS idx_pendentes_tipo_movimento ON pendentes(tipo_movimento);
