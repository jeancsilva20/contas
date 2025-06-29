
#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados PostgreSQL do Render
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def testar_conexao():
    # URLs de conexão PostgreSQL no Render
    database_url_internal = "postgresql://contas:b62OYudl5h3htXjydOW4s3owWcxOYj7v@dpg-d1gccgffte5s738fk4n0-a/contas_xltx"
    database_url_external = "postgresql://contas:b62OYudl5h3htXjydOW4s3owWcxOYj7v@dpg-d1gccgffte5s738fk4n0-a.oregon-postgres.render.com/contas_xltx"
    
    print("🔌 Testando conexões com o banco de dados PostgreSQL...")
    print(f"Database: contas_xltx")
    print(f"Username: contas")
    print("-" * 50)
    
    # Testa URLs em ordem de preferência
    urls_to_test = [
        ("INTERNA", database_url_internal),
        ("EXTERNA", database_url_external)
    ]
    
    for tipo, database_url in urls_to_test:
        try:
            print(f"\n🔍 Testando conexão {tipo}...")
            
            # Tenta conectar
            conn = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
        
        print(f"✅ Conexão {tipo} estabelecida com sucesso!")
            
            # Testa uma query simples
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"📊 Versão do PostgreSQL: {version['version']}")
            
            # Lista tabelas existentes
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tabelas = cur.fetchall()
            
            if tabelas:
                print(f"📋 Tabelas encontradas ({len(tabelas)}):")
                for tabela in tabelas:
                    print(f"   - {tabela['table_name']}")
            else:
                print("📋 Nenhuma tabela encontrada (banco vazio)")
            
            cur.close()
            conn.close()
            
            print("-" * 50)
            print(f"🎉 Teste de conexão {tipo} concluído com sucesso!")
            print(f"🔗 URL utilizada: {database_url}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão {tipo}: {e}")
            continue
    
    # Se chegou aqui, nenhuma conexão funcionou
    print("-" * 50)
    print("❌ Todas as tentativas de conexão falharam!")
    print("💡 Verifique:")
    print("   - Se as credenciais estão corretas")
    print("   - Se o banco de dados está ativo")
    print("   - Se há conectividade de rede")
    return False

if __name__ == "__main__":
    testar_conexao()
