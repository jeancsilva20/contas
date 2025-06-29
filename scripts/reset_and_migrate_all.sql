
-- Script para limpar todas as tabelas e migrar dados dos arquivos JSON
-- Considerando relacionamentos entre tabelas

-- 1. LIMPAR TODAS AS TABELAS (na ordem correta devido aos relacionamentos)
TRUNCATE TABLE revisoes CASCADE;
TRUNCATE TABLE pendentes CASCADE;
TRUNCATE TABLE transacoes CASCADE;
TRUNCATE TABLE fontes CASCADE;
-- Não limpamos a tabela pessoas conforme solicitado

-- 2. RESETAR SEQUENCES
ALTER SEQUENCE fontes_id_seq RESTART WITH 1;
ALTER SEQUENCE transacoes_id_seq RESTART WITH 1;
ALTER SEQUENCE pendentes_id_seq RESTART WITH 1;
ALTER SEQUENCE revisoes_id_seq RESTART WITH 1;

-- 3. INSERIR FONTES (primeira, pois outras tabelas podem referenciar)
INSERT INTO fontes (nome, ativo, data_criacao) VALUES
('Cartão C6', TRUE, CURRENT_TIMESTAMP),
('Conta C6', TRUE, CURRENT_TIMESTAMP),
('Cartão XP', TRUE, CURRENT_TIMESTAMP),
('Conta XP', TRUE, CURRENT_TIMESTAMP),
('Cartão C6 Tati', TRUE, CURRENT_TIMESTAMP),
('Manual', TRUE, CURRENT_TIMESTAMP);

-- 4. INSERIR TRANSAÇÕES
INSERT INTO transacoes (transacao_id, tipo, data, descricao, valor, tipo_movimento, fonte, hash, observacoes, ativo) VALUES
('cartao_1751160449_0', 'cartao', '2025-04-07', 'AZUL WE*EF3ZQYSILVA', -1131.8, 'entrada', 'Cartão C6', '1318029dfa7545fc8dfce2c546416bdace3f8e7124a672256db5d0ace4cd4009', 'Parcela: 02/fev | Categoria: T&E Companhia aérea | Cartão: JEAN C SILVA | Final: 4447.0', TRUE),
('cartao_1751160449_1', 'cartao', '2025-04-14', 'MULTIUTILSTORE', 139.73, 'saida', 'Cartão C6', 'e1a469fd2170ed5cd27bc29e92a6cad989f804d345de0c219bca24a9a8ca7480', 'Parcela: 02/fev | Categoria: Departamento / Desconto | Cartão: JEAN C SILVA | Final: 6071.0', TRUE),
('cartao_1751160449_2', 'cartao', '2025-05-03', 'LATAM AIR', -967.9, 'entrada', 'Cartão C6', '1b95ecedf3d567c8be7a5cf9a83b454e342a3d776c44cfd5fc136e49b86bd372', 'Parcela: Única | Categoria: T&E Companhia aérea | Cartão: JEAN C SILVA | Final: 6071.0', TRUE),
('cartao_1751160449_3', 'cartao', '2025-05-06', 'MICROSOFT*STORE', -60.0, 'entrada', 'Cartão C6', 'ac0c43ecf51c208e49d44deccf6c32903c806a7cebeb7ae41701fb764c9c68ed', 'Parcela: Única | Categoria: Entretenimento | Cartão: JEAN C SILVA | Final: 6071.0', TRUE),
('cartao_1751160449_4', 'cartao', '2025-05-29', 'OPENAI                 +1', -29.96, 'entrada', 'Cartão C6', 'f617609c6f17ce1f30e40d870c1070b73ec6f09fc0118baa15e88004e97cc7d1', 'Parcela: Única | Categoria: Elétrico | Cartão: JEAN C SILVA | Final: 6071.0', TRUE),
('cartao_1751160449_5', 'cartao', '2025-05-29', 'OPENAI                 +1', -1.05, 'entrada', 'Cartão C6', '9054dbaaaeb63cb54180f2418092d6a4c926f576f3595fb727b7dec5a13ab71b', 'Parcela: Única | Categoria: Elétrico | Cartão: JEAN C SILVA | Final: 6071.0', TRUE),
('cartao_1751160507_41', 'cartao', '2025-06-10', 'Pix para Jean Silva', -9991.59, 'entrada', 'Cartão C6', 'dfbafcce98654e2de3f86597447c1a6f826f26d8fca32ed146e90950633e416b', 'Categoria: Pix recebido de JEAN CARLOS DA SILVA', TRUE),
('manual_1751160775', 'manual', '2025-06-29', 'Teste de nova despesa', 0.07, 'saida', 'Manual', '70cffbd2a03de60c68969f682b1880d81f8eb4b2393b6242fb4dc05e01c20629', 'Categoria: Categoria | teste', TRUE);

-- 5. INSERIR PENDENTES (baseado nas transações)
INSERT INTO pendentes (transacao_id, tipo, data, descricao, valor, tipo_movimento, fonte, hash, observacoes, ativo) VALUES
('cartao_1751160449_0', 'cartao', '2025-04-07', 'AZUL WE*EF3ZQYSILVA', -1131.8, 'entrada', 'Cartão C6', '1318029dfa7545fc8dfce2c546416bdace3f8e7124a672256db5d0ace4cd4009', 'Parcela: 02/fev | Categoria: T&E Companhia aérea | Cartão: JEAN C SILVA | Final: 4447.0', TRUE),
('cartao_1751160449_1', 'cartao', '2025-04-14', 'MULTIUTILSTORE', 139.73, 'saida', 'Cartão C6', 'e1a469fd2170ed5cd27bc29e92a6cad989f804d345de0c219bca24a9a8ca7480', 'Parcela: 02/fev | Categoria: Departamento / Desconto | Cartão: JEAN C SILVA | Final: 6071.0', TRUE),
('cartao_1751160449_2', 'cartao', '2025-05-03', 'LATAM AIR', -967.9, 'entrada', 'Cartão C6', '1b95ecedf3d567c8be7a5cf9a83b454e342a3d776c44cfd5fc136e49b86bd372', 'Parcela: Única | Categoria: T&E Companhia aérea | Cartão: JEAN C SILVA | Final: 6071.0', TRUE);

-- 6. INSERIR REVISÕES (por último, pois referenciam transações através do hash)
INSERT INTO revisoes (hash, id_original, nova_descricao, donos, comentarios, pago_por, quitado, quitacao_individual, data_revisao, revisado_por, ativo) VALUES
('dfbafcce98654e2de3f86597447c1a6f826f26d8fca32ed146e90950633e416b', 'cartao_1751160507_41', 'Pix para Jean Silva', '{"Jean": 20, "João Rafael": 20, "Juliano": 20, "Tati": 20, "João Batista": 20}', '', 'Jean', FALSE, '{"Jean": false, "João Rafael": false, "Juliano": false, "Tati": false, "João Batista": false}', '2025-06-29T01:29:17.220163', 'Usuario', TRUE),
('70cffbd2a03de60c68969f682b1880d81f8eb4b2393b6242fb4dc05e01c20629', 'manual_1751160775', 'Teste de nova despesa', '{"Jean": 34, "João Rafael": 33, "Tati": 33}', 'testes', 'Tati', FALSE, '{"Jean": false, "João Rafael": false, "Tati": false}', '2025-06-29T01:32:55.629674', 'Manual', TRUE);

-- 7. VERIFICAR INSERÇÕES
SELECT 'FONTES' as tabela, COUNT(*) as total FROM fontes
UNION ALL
SELECT 'TRANSAÇÕES' as tabela, COUNT(*) as total FROM transacoes
UNION ALL
SELECT 'PENDENTES' as tabela, COUNT(*) as total FROM pendentes
UNION ALL
SELECT 'REVISÕES' as tabela, COUNT(*) as total FROM revisoes;
