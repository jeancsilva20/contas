
#!/usr/bin/env python3
"""
Script para testar conexão com Supabase
"""

from services.database import DatabaseService

def test_connection():
    print("Testando conexão com Supabase...")
    
    try:
        db = DatabaseService()
        conn = db.get_connection()
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 Versão PostgreSQL: {version[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    test_connection()
