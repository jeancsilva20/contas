
#!/usr/bin/env python3
"""
Script para migrar dados de fontes do arquivo JSON para PostgreSQL
"""

from services.database import FonteService

def main():
    print("Iniciando migração de fontes...")
    
    try:
        fonte_service = FonteService()
        
        # Executa a migração
        if fonte_service.migrar_fontes_json():
            print("✅ Migração concluída com sucesso!")
            
            # Lista as fontes migradas
            fontes = fonte_service.listar_fontes()
            print(f"\n📋 Fontes migradas ({len(fontes)}):")
            for fonte in fontes:
                print(f"  - {fonte}")
        else:
            print("❌ Erro na migração!")
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")

if __name__ == "__main__":
    main()
