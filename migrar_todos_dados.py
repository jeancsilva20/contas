
#!/usr/bin/env python3
"""
Script para migrar todos os dados dos arquivos JSON para PostgreSQL
"""

from services.database import FonteService, PendenteService, TransacaoService, RevisaoService

def main():
    print("🚀 Iniciando migração completa dos dados para PostgreSQL...")
    print("=" * 60)
    
    # 1. Migrar fontes
    print("\n1️⃣ Migrando fontes...")
    try:
        fonte_service = FonteService()
        if fonte_service.migrar_fontes_json():
            fontes = fonte_service.listar_fontes()
            print(f"✅ {len(fontes)} fontes migradas com sucesso!")
        else:
            print("❌ Erro na migração das fontes")
    except Exception as e:
        print(f"❌ Erro na migração das fontes: {e}")
    
    # 2. Migrar transações
    print("\n2️⃣ Migrando transações...")
    try:
        transacao_service = TransacaoService()
        if transacao_service.migrar_transacoes_json():
            transacoes = transacao_service.listar_transacoes()
            print(f"✅ {len(transacoes)} transações migradas com sucesso!")
        else:
            print("❌ Erro na migração das transações")
    except Exception as e:
        print(f"❌ Erro na migração das transações: {e}")
    
    # 3. Migrar pendentes
    print("\n3️⃣ Migrando pendentes...")
    try:
        pendente_service = PendenteService()
        if pendente_service.migrar_pendentes_json():
            pendentes = pendente_service.listar_pendentes()
            print(f"✅ {len(pendentes)} pendentes migrados com sucesso!")
        else:
            print("❌ Erro na migração dos pendentes")
    except Exception as e:
        print(f"❌ Erro na migração dos pendentes: {e}")
    
    # 4. Migrar revisões
    print("\n4️⃣ Migrando revisões...")
    try:
        revisao_service = RevisaoService()
        if revisao_service.migrar_revisoes_json():
            revisoes = revisao_service.listar_revisoes()
            print(f"✅ {len(revisoes)} revisões migradas com sucesso!")
        else:
            print("❌ Erro na migração das revisões")
    except Exception as e:
        print(f"❌ Erro na migração das revisões: {e}")
    
    # 5. Migrar pessoas
    print("\n5️⃣ Migrando pessoas...")
    try:
        from services.database import PessoaService
        pessoa_service = PessoaService()
        if pessoa_service.migrar_pessoas_json():
            pessoas = pessoa_service.listar_pessoas()
            print(f"✅ {len(pessoas)} pessoas migradas com sucesso!")
        else:
            print("❌ Erro na migração das pessoas")
    except Exception as e:
        print(f"❌ Erro na migração das pessoas: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Migração completa finalizada!")
    print("\n💡 Agora o sistema está usando o banco PostgreSQL do Supabase.")
    print("   Os arquivos JSON ainda estão preservados como backup.")

if __name__ == "__main__":
    main()

def main():
    print("Iniciando migração completa dos dados...")
    
    # Ordem da migração é importante devido às dependências
    
    # 1. Migra fontes
    print("\n1. Migrando fontes...")
    fonte_service = FonteService()
    try:
        if fonte_service.migrar_fontes_json():
            print("✅ Fontes migradas com sucesso!")
        else:
            print("❌ Erro na migração das fontes")
    except Exception as e:
        print(f"❌ Erro na migração das fontes: {e}")
    
    # 2. Migra transações
    print("\n2. Migrando transações...")
    transacao_service = TransacaoService()
    try:
        if transacao_service.migrar_transacoes_json():
            print("✅ Transações migradas com sucesso!")
        else:
            print("❌ Erro na migração das transações")
    except Exception as e:
        print(f"❌ Erro na migração das transações: {e}")
    
    # 3. Migra revisões
    print("\n3. Migrando revisões...")
    revisao_service = RevisaoService()
    try:
        if revisao_service.migrar_revisoes_json():
            print("✅ Revisões migradas com sucesso!")
        else:
            print("❌ Erro na migração das revisões")
    except Exception as e:
        print(f"❌ Erro na migração das revisões: {e}")
    
    # 4. Migra pendentes
    print("\n4. Migrando pendentes...")
    pendente_service = PendenteService()
    try:
        if pendente_service.migrar_pendentes_json():
            print("✅ Pendentes migrados com sucesso!")
        else:
            print("❌ Erro na migração dos pendentes")
    except Exception as e:
        print(f"❌ Erro na migração dos pendentes: {e}")
    
    print("\n🎉 Migração completa finalizada!")

if __name__ == "__main__":
    main()

def main():
    print("🚀 Iniciando migração completa dos dados para PostgreSQL...")
    print("=" * 60)
    
    try:
        # Migrar fontes
        print("\n📂 Migrando fontes...")
        fonte_service = FonteService()
        if fonte_service.migrar_fontes_json():
            fontes = fonte_service.listar_fontes()
            print(f"✅ Fontes migradas com sucesso! ({len(fontes)} registros)")
        else:
            print("❌ Erro na migração de fontes!")
            return
        
        # Migrar pendentes
        print("\n⏳ Migrando pendentes...")
        pendente_service = PendenteService()
        if pendente_service.migrar_pendentes_json():
            pendentes = pendente_service.listar_pendentes()
            print(f"✅ Pendentes migrados com sucesso! ({len(pendentes)} registros)")
        else:
            print("❌ Erro na migração de pendentes!")
            return
        
        print("\n" + "=" * 60)
        print("🎉 MIGRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📊 Resumo:")
        print(f"   - Fontes: {len(fontes)} registros")
        print(f"   - Pendentes: {len(pendentes)} registros")
        print("\n💡 Próximos passos:")
        print("   1. Teste a aplicação para verificar se tudo está funcionando")
        print("   2. Faça backup dos arquivos JSON originais")
        print("   3. Configure backups regulares do banco de dados")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")

if __name__ == "__main__":
    main()
