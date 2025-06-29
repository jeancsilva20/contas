
#!/usr/bin/env python3
"""
Script para inicializar as tabelas do banco de dados
"""

from services.database import FonteService, PendenteService, TransacaoService, RevisaoService, PessoaService

def main():
    print("🚀 Inicializando estrutura do banco de dados...")
    print("=" * 60)
    
    try:
        # Inicializar todas as tabelas
        print("📂 Criando tabela de fontes...")
        fonte_service = FonteService()
        fonte_service.criar_tabela_fontes()
        print("✅ Tabela de fontes criada!")
        
        print("⏳ Criando tabela de pendentes...")
        pendente_service = PendenteService()
        pendente_service.criar_tabela_pendentes()
        print("✅ Tabela de pendentes criada!")
        
        print("💰 Criando tabela de transações...")
        transacao_service = TransacaoService()
        transacao_service.criar_tabela_transacoes()
        print("✅ Tabela de transações criada!")
        
        print("📝 Criando tabela de revisões...")
        revisao_service = RevisaoService()
        revisao_service.criar_tabela_revisoes()
        print("✅ Tabela de revisões criada!")
        
        print("👥 Criando tabela de pessoas...")
        pessoa_service = PessoaService()
        pessoa_service.criar_tabela_pessoas()
        print("✅ Tabela de pessoas criada!")
        
        # Adicionar fontes padrão se não existirem
        print("\n📋 Adicionando fontes padrão...")
        fontes_padrao = ["Cartão C6", "Conta C6", "Cartão XP", "Conta XP", "Cartão C6 Tati"]
        for fonte in fontes_padrao:
            if not fonte_service.fonte_existe(fonte):
                fonte_service.adicionar_fonte(fonte)
                print(f"   + {fonte}")
        
        print("\n" + "=" * 60)
        print("🎉 BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("=" * 60)
        print("\n💡 O sistema está pronto para uso com PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        return False

if __name__ == "__main__":
    main()
