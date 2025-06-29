
#!/usr/bin/env python3
"""
Script para inicializar as tabelas do banco de dados PostgreSQL no Render
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def criar_estrutura_banco():
    """Cria todas as tabelas necessárias no banco PostgreSQL do Render"""
    
    # URL de conexão interna do PostgreSQL no Render
    database_url = "postgresql://contas:b62OYudl5h3htXjydOW4s3owWcxOYj7v@dpg-d1gccgffte5s738fk4n0-a/contas_xltx"
    
    try:
        print("🚀 Conectando ao banco PostgreSQL do Render...")
        
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )
        cur = conn.cursor()
        
        print("✅ Conexão estabelecida com sucesso!")
        print("=" * 60)
        
        # Criar tabela de fontes
        print("📂 Criando tabela de fontes...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fontes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT TRUE
            )
        """)
        print("✅ Tabela fontes criada!")
        
        # Criar tabela de pessoas
        print("👥 Criando tabela de pessoas...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome);
            CREATE INDEX IF NOT EXISTS idx_pessoas_ativo ON pessoas(ativo);
        """)
        print("✅ Tabela pessoas criada!")
        
        # Criar tabela de transações
        print("💰 Criando tabela de transações...")
        cur.execute("""
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

            CREATE INDEX IF NOT EXISTS idx_transacoes_hash ON transacoes(hash);
            CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);
            CREATE INDEX IF NOT EXISTS idx_transacoes_fonte ON transacoes(fonte);
            CREATE INDEX IF NOT EXISTS idx_transacoes_ativo ON transacoes(ativo);
            CREATE INDEX IF NOT EXISTS idx_transacoes_tipo_movimento ON transacoes(tipo_movimento);
        """)
        print("✅ Tabela transações criada!")
        
        # Criar tabela de pendentes
        print("⏳ Criando tabela de pendentes...")
        cur.execute("""
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

            CREATE INDEX IF NOT EXISTS idx_pendentes_hash ON pendentes(hash);
            CREATE INDEX IF NOT EXISTS idx_pendentes_data ON pendentes(data);
            CREATE INDEX IF NOT EXISTS idx_pendentes_fonte ON pendentes(fonte);
            CREATE INDEX IF NOT EXISTS idx_pendentes_ativo ON pendentes(ativo);
            CREATE INDEX IF NOT EXISTS idx_pendentes_tipo_movimento ON pendentes(tipo_movimento);
        """)
        print("✅ Tabela pendentes criada!")
        
        # Criar tabela de revisões
        print("📝 Criando tabela de revisões...")
        cur.execute("""
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

            CREATE INDEX IF NOT EXISTS idx_revisoes_hash ON revisoes(hash);
            CREATE INDEX IF NOT EXISTS idx_revisoes_data_revisao ON revisoes(data_revisao);
            CREATE INDEX IF NOT EXISTS idx_revisoes_pago_por ON revisoes(pago_por);
            CREATE INDEX IF NOT EXISTS idx_revisoes_quitado ON revisoes(quitado);
            CREATE INDEX IF NOT EXISTS idx_revisoes_ativo ON revisoes(ativo);
        """)
        print("✅ Tabela revisões criada!")
        
        # Inserir dados padrão
        print("\n📋 Inserindo dados padrão...")
        
        # Fontes padrão
        fontes_padrao = ["Cartão C6", "Conta C6", "Cartão XP", "Conta XP", "Cartão C6 Tati", "Manual"]
        for fonte in fontes_padrao:
            cur.execute(
                "INSERT INTO fontes (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING",
                (fonte,)
            )
            print(f"   + Fonte: {fonte}")
        
        # Pessoas padrão
        pessoas_padrao = ["Jean", "João Batista", "João Rafael", "Juliano", "Tati"]
        for pessoa in pessoas_padrao:
            cur.execute(
                "INSERT INTO pessoas (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING",
                (pessoa,)
            )
            print(f"   + Pessoa: {pessoa}")
        
        # Confirma todas as alterações
        conn.commit()
        
        print("\n" + "=" * 60)
        print("🎉 BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("=" * 60)
        print("\n💡 O sistema está pronto para uso no Render!")
        
        # Mostra estatísticas finais
        cur.execute("SELECT COUNT(*) as total FROM fontes WHERE ativo = TRUE")
        total_fontes = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM pessoas WHERE ativo = TRUE")
        total_pessoas = cur.fetchone()['total']
        
        print(f"\n📊 Estatísticas:")
        print(f"   - Fontes ativas: {total_fontes}")
        print(f"   - Pessoas ativas: {total_pessoas}")
        print(f"   - Tabelas criadas: 5")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    criar_estrutura_banco()
