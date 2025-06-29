
-- Script para criar tabela de pessoas e migrar dados das revisões

-- Criar tabela de pessoas
CREATE TABLE IF NOT EXISTS pessoas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT
);

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome);
CREATE INDEX IF NOT EXISTS idx_pessoas_ativo ON pessoas(ativo);

-- Inserir pessoas padrão baseadas no sistema existente
INSERT INTO pessoas (nome) VALUES 
    ('Jean'),
    ('João Batista'),
    ('João Rafael'),
    ('Juliano'),
    ('Tati')
ON CONFLICT (nome) DO NOTHING;

-- Comentários sobre a tabela
COMMENT ON TABLE pessoas IS 'Tabela para armazenar as pessoas do sistema para rateio e pagamentos';
COMMENT ON COLUMN pessoas.nome IS 'Nome da pessoa (único)';
COMMENT ON COLUMN pessoas.ativo IS 'Indica se a pessoa está ativa no sistema';
COMMENT ON COLUMN pessoas.observacoes IS 'Observações adicionais sobre a pessoa';
