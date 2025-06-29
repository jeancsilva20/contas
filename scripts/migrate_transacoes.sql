
-- Script para criar tabela de transações e migrar dados do JSON

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

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_transacoes_hash ON transacoes(hash);
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);
CREATE INDEX IF NOT EXISTS idx_transacoes_fonte ON transacoes(fonte);
CREATE INDEX IF NOT EXISTS idx_transacoes_ativo ON transacoes(ativo);
CREATE INDEX IF NOT EXISTS idx_transacoes_tipo_movimento ON transacoes(tipo_movimento);
CREATE INDEX IF NOT EXISTS idx_transacoes_transacao_id ON transacoes(transacao_id);

-- Comentários das colunas
COMMENT ON TABLE transacoes IS 'Tabela de transações financeiras processadas';
COMMENT ON COLUMN transacoes.transacao_id IS 'ID único da transação (original do arquivo)';
COMMENT ON COLUMN transacoes.tipo IS 'Tipo da transação (cartao, transferencia, etc)';
COMMENT ON COLUMN transacoes.data IS 'Data da transação';
COMMENT ON COLUMN transacoes.descricao IS 'Descrição da transação';
COMMENT ON COLUMN transacoes.valor IS 'Valor da transação (negativo para entradas)';
COMMENT ON COLUMN transacoes.tipo_movimento IS 'Tipo de movimento: entrada ou saida';
COMMENT ON COLUMN transacoes.fonte IS 'Fonte da transação (ex: Cartão C6)';
COMMENT ON COLUMN transacoes.hash IS 'Hash único para identificar duplicatas';
COMMENT ON COLUMN transacoes.observacoes IS 'Observações adicionais da transação';
COMMENT ON COLUMN transacoes.ativo IS 'Se a transação está ativa (soft delete)';
