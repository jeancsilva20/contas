
#!/usr/bin/env python3
"""
Script para migrar pessoas das revisões para a tabela pessoas no PostgreSQL
"""

from services.database import PessoaService

def main():
    print("🚀 Iniciando migração das pessoas para PostgreSQL...")
    print("=" * 60)
    
    try:
        pessoa_service = PessoaService()
        
        # Migrar pessoas
        print("\n👥 Migrando pessoas...")
        if pessoa_service.migrar_pessoas_json():
            pessoas = pessoa_service.listar_pessoas()
            print(f"✅ Pessoas migradas com sucesso! ({len(pessoas)} registros)")
            print(f"📋 Pessoas encontradas: {', '.join(pessoas)}")
        else:
            print("❌ Erro na migração de pessoas!")
            return
        
        print("\n" + "=" * 60)
        print("🎉 MIGRAÇÃO DE PESSOAS CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📊 Resumo:")
        print(f"   - Pessoas: {len(pessoas)} registros")
        print("\n💡 Agora o sistema pode usar a tabela pessoas para:")
        print("   - Lista de pessoas para rateio")
        print("   - Campo 'Pago Por'")
        print("   - Gerenciamento centralizado de pessoas")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")

if __name__ == "__main__":
    main()
