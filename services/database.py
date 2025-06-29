import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

class DatabaseService:
    def __init__(self):
        # Usa o Transaction Pooler do Supabase (melhor para aplicações web)
        self.database_url = "postgresql://postgres.xwtgelviiogtdonckkve:JzEKV#x5wXeXy4g@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

    def get_connection(self):
        """Retorna conexão com o banco de dados"""
        try:
            conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")
            raise

    def execute_query(self, query, params=None, fetch=False):
        """Executa query no banco de dados"""
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            cur.execute(query, params)

            if fetch:
                result = cur.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao executar query: {e}")
            raise
        finally:
            if conn:
                cur.close()
                conn.close()

class FonteService:
    def __init__(self):
        self.db = DatabaseService()

    def migrar_fontes_json(self):
        """Migra dados do arquivo fontes.json para o banco de dados"""
        try:
            # Carrega dados do JSON
            with open('data/fontes.json', 'r', encoding='utf-8') as f:
                fontes_json = json.load(f)

            # Verifica se a tabela existe, se não, cria
            self.criar_tabela_fontes()

            # Limpa tabela existente
            self.db.execute_query("DELETE FROM fontes")

            # Insere fontes do JSON
            for fonte in fontes_json:
                self.adicionar_fonte(fonte)

            print(f"Migração concluída! {len(fontes_json)} fontes migradas.")
            return True

        except Exception as e:
            print(f"Erro na migração: {e}")
            return False

    def criar_tabela_fontes(self):
        """Cria a tabela de fontes se ela não existir"""
        query = """
        CREATE TABLE IF NOT EXISTS fontes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT TRUE
        )
        """
        self.db.execute_query(query)

    def listar_fontes(self):
        """Lista todas as fontes ativas"""
        query = "SELECT nome FROM fontes WHERE ativo = TRUE ORDER BY nome"
        result = self.db.execute_query(query, fetch=True)
        return [row['nome'] for row in result]

    def adicionar_fonte(self, nome):
        """Adiciona uma nova fonte"""
        query = "INSERT INTO fontes (nome) VALUES (%s)"
        return self.db.execute_query(query, (nome,))

    def editar_fonte(self, nome_antigo, nome_novo):
        """Edita o nome de uma fonte"""
        query = "UPDATE fontes SET nome = %s WHERE nome = %s AND ativo = TRUE"
        return self.db.execute_query(query, (nome_novo, nome_antigo))

    def excluir_fonte(self, nome):
        """Marca uma fonte como inativa (soft delete)"""
        query = "UPDATE fontes SET ativo = FALSE WHERE nome = %s"
        return self.db.execute_query(query, (nome,))

    def fonte_existe(self, nome):
        """Verifica se uma fonte existe"""
        query = "SELECT COUNT(*) as count FROM fontes WHERE nome = %s AND ativo = TRUE"
        result = self.db.execute_query(query, (nome,), fetch=True)
        return result[0]['count'] > 0


class PendenteService:
    def __init__(self):
        self.db = DatabaseService()

    def migrar_pendentes_json(self):
        """Migra dados do arquivo pendentes.json para o banco de dados"""
        try:
            # Carrega dados do JSON
            with open('data/pendentes.json', 'r', encoding='utf-8') as f:
                pendentes_json = json.load(f)

            # Verifica se a tabela existe, se não, cria
            self.criar_tabela_pendentes()

            # Limpa tabela existente
            self.db.execute_query("DELETE FROM pendentes")

            # Insere pendentes do JSON
            for pendente in pendentes_json:
                self.adicionar_pendente(
                    transacao_id=pendente.get('id'),
                    tipo=pendente.get('tipo'),
                    data=pendente.get('data'),
                    descricao=pendente.get('descricao'),
                    valor=pendente.get('valor'),
                    tipo_movimento=pendente.get('tipo_movimento'),
                    fonte=pendente.get('fonte'),
                    hash_transacao=pendente.get('hash'),
                    observacoes=pendente.get('observacoes', '')
                )

            print(f"Migração concluída! {len(pendentes_json)} pendentes migradas.")
            return True

        except Exception as e:
            print(f"Erro na migração: {e}")
            return False

    def criar_tabela_pendentes(self):
        """Cria a tabela de pendentes se ela não existir"""
        query = """
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
        """
        self.db.execute_query(query)

    def listar_pendentes(self):
        """Lista todas as transações pendentes ativas"""
        query = """
        SELECT transacao_id, tipo, data, descricao, valor, tipo_movimento, 
               fonte, hash, observacoes, data_criacao, ativo
        FROM pendentes 
        WHERE ativo = TRUE
        ORDER BY data DESC
        """
        result = self.db.execute_query(query, fetch=True)
        return [dict(row) for row in result]

    def adicionar_pendente(self, transacao_id, tipo, data, descricao, valor, 
                          tipo_movimento, fonte, hash_transacao, observacoes=''):
        """Adiciona uma nova transação pendente"""
        query = """
        INSERT INTO pendentes (transacao_id, tipo, data, descricao, valor, 
                              tipo_movimento, fonte, hash, observacoes) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (
            transacao_id, tipo, data, descricao, valor, 
            tipo_movimento, fonte, hash_transacao, observacoes
        ))

    def excluir_pendente(self, hash_transacao):
        """Remove uma transação da lista de pendentes (soft delete)"""
        query = "UPDATE pendentes SET ativo = FALSE WHERE hash = %s"
        return self.db.execute_query(query, (hash_transacao,))

    def pendente_existe(self, hash_transacao):
        """Verifica se uma transação pendente existe"""
        query = "SELECT COUNT(*) as count FROM pendentes WHERE hash = %s AND ativo = TRUE"
        result = self.db.execute_query(query, (hash_transacao,), fetch=True)
        return result[0]['count'] > 0

    def listar_hashes_pendentes(self):
        """Lista apenas os hashes dos pendentes ativos (para cache)"""
        query = "SELECT hash FROM pendentes WHERE ativo = TRUE"
        result = self.db.execute_query(query, fetch=True)
        return {row['hash'] for row in result}

    def buscar_pendente_por_hash(self, hash_transacao):
        """Busca uma transação pendente pelo hash"""
        query = """
        SELECT transacao_id, tipo, data, descricao, valor, 
               tipo_movimento, fonte, hash, observacoes, data_criacao
        FROM pendentes 
        WHERE hash = %s AND ativo = TRUE
        """
        result = self.db.execute_query(query, (hash_transacao,), fetch=True)
        return dict(result[0]) if result else None

    def adicionar_transacoes_lote(self, transacoes_list):
        """Adiciona múltiplas transações pendentes em lote"""
        if not transacoes_list:
            print("⚠️ Lista de pendentes vazia")
            return True

        query = """
        INSERT INTO pendentes (transacao_id, tipo, data, descricao, valor, 
                              tipo_movimento, fonte, hash, observacoes) 
        VALUES %s
        ON CONFLICT (hash) DO NOTHING
        """

        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()

            dados = []
            print(f"🔍 Preparando {len(transacoes_list)} pendentes para inserção...")
            
            for i, transacao in enumerate(transacoes_list):
                try:
                    if not isinstance(transacao, dict):
                        print(f"❌ Pendente {i} não é um dicionário válido")
                        continue
                    
                    dados.append((
                        str(transacao.get('id', '')),
                        str(transacao.get('tipo', '')),
                        str(transacao.get('data', '')),
                        str(transacao.get('descricao', '')),
                        float(transacao.get('valor', 0)),
                        str(transacao.get('tipo_movimento', '')),
                        str(transacao.get('fonte', '')),
                        str(transacao.get('hash', '')),
                        str(transacao.get('observacoes', ''))
                    ))
                    
                except Exception as e:
                    print(f"❌ Erro ao processar pendente {i}: {e}")
                    continue

            if not dados:
                print("⚠️ Nenhum pendente válido para inserir")
                return True

            print(f"🔄 Inserindo {len(dados)} pendentes em lote...")
            
            from psycopg2.extras import execute_values
            execute_values(cur, query, dados, template=None, page_size=10)

            affected_rows = cur.rowcount
            conn.commit()
            
            print(f"✅ {affected_rows} pendentes inseridos com sucesso")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Erro ao inserir lote de pendentes: {e}")
            raise
        finally:
            if conn:
                cur.close()
                conn.close()


class TransacaoService:
    def __init__(self):
        self.db = DatabaseService()

    def migrar_transacoes_json(self):
        """Migra dados do arquivo transacoes.json para o banco de dados"""
        try:
            # Carrega dados do JSON
            with open('data/transacoes.json', 'r', encoding='utf-8') as f:
                transacoes_json = json.load(f)

            # Verifica se a tabela existe, se não, cria
            self.criar_tabela_transacoes()

            # Limpa tabela existente
            self.db.execute_query("DELETE FROM transacoes")

            # Insere transações do JSON
            for transacao in transacoes_json:
                self.adicionar_transacao(
                    transacao_id=transacao.get('id'),
                    tipo=transacao.get('tipo'),
                    data=transacao.get('data'),
                    descricao=transacao.get('descricao'),
                    valor=transacao.get('valor'),
                    tipo_movimento=transacao.get('tipo_movimento'),
                    fonte=transacao.get('fonte'),
                    hash_transacao=transacao.get('hash'),
                    observacoes=transacao.get('observacoes', '')
                )

            print(f"Migração concluída! {len(transacoes_json)} transações migradas.")
            return True

        except Exception as e:
            print(f"Erro na migração: {e}")
            return False

    def criar_tabela_transacoes(self):
        """Cria a tabela de transações se ela não existir"""
        query = """
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
        """
        self.db.execute_query(query)

    def listar_transacoes(self):
        """Lista todas as transações ativas"""
        query = """
        SELECT transacao_id, tipo, data, descricao, valor, tipo_movimento, 
               fonte, hash, observacoes, data_criacao, ativo
        FROM transacoes 
        WHERE ativo = TRUE
        ORDER BY data DESC
        """
        result = self.db.execute_query(query, fetch=True)
        return [dict(row) for row in result]

    def listar_hashes_transacoes(self):
        """Lista apenas os hashes das transações ativas (para cache)"""
        query = "SELECT hash FROM transacoes WHERE ativo = TRUE"
        result = self.db.execute_query(query, fetch=True)
        return {row['hash'] for row in result}

    def adicionar_transacao(self, transacao_id, tipo, data, descricao, valor, 
                           tipo_movimento, fonte, hash_transacao, observacoes=''):
        """Adiciona uma nova transação"""
        query = """
        INSERT INTO transacoes (transacao_id, tipo, data, descricao, valor, 
                               tipo_movimento, fonte, hash, observacoes) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (hash) DO NOTHING
        """
        return self.db.execute_query(query, (
            transacao_id, tipo, data, descricao, valor, 
            tipo_movimento, fonte, hash_transacao, observacoes
        ))

    def adicionar_transacoes_lote(self, transacoes_list):
        """Adiciona múltiplas transações em lote para melhor performance"""
        if not transacoes_list:
            print("⚠️ Lista de transações vazia")
            return True

        query = """
        INSERT INTO transacoes (transacao_id, tipo, data, descricao, valor, 
                               tipo_movimento, fonte, hash, observacoes) 
        VALUES %s
        ON CONFLICT (hash) DO NOTHING
        """

        conn = None
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()

            # Prepara dados para inserção em lote com validação robusta
            dados = []
            campos_obrigatorios = ['id', 'tipo', 'data', 'descricao', 'valor', 'tipo_movimento', 'fonte', 'hash']
            
            print(f"🔍 Processando {len(transacoes_list)} transações para inserção...")
            
            for i, transacao in enumerate(transacoes_list):
                try:
                    # Verifica se é um dicionário válido
                    if not isinstance(transacao, dict):
                        print(f"❌ Transação {i} não é um dicionário válido: {type(transacao)}")
                        continue
                    
                    # Debug: mostra chaves da transação
                    print(f"🔍 Transação {i} - Chaves: {list(transacao.keys())}")
                    
                    # Valida campos obrigatórios
                    campos_faltantes = []
                    for campo in campos_obrigatorios:
                        if campo not in transacao or transacao[campo] is None:
                            campos_faltantes.append(campo)
                    
                    if campos_faltantes:
                        print(f"❌ Transação {i} - Campos faltantes: {campos_faltantes}")
                        continue
                    
                    # Valida tipos de dados
                    if not isinstance(transacao['valor'], (int, float)):
                        print(f"❌ Transação {i} - Valor inválido: {transacao['valor']}")
                        continue
                    
                    # Adiciona à lista de dados para inserção
                    dados.append((
                        str(transacao['id']),
                        str(transacao['tipo']),
                        str(transacao['data']),
                        str(transacao['descricao']),
                        float(transacao['valor']),
                        str(transacao['tipo_movimento']),
                        str(transacao['fonte']),
                        str(transacao['hash']),
                        str(transacao.get('observacoes', ''))
                    ))
                    
                    print(f"✅ Transação {i} validada e preparada")
                    
                except Exception as e:
                    print(f"❌ Erro ao processar transação {i}: {e}")
                    continue

            if not dados:
                print("⚠️ Nenhuma transação válida para inserir")
                return True

            print(f"🔄 Tentando inserir {len(dados)} transações válidas em lote...")
            
            # Usa execute_values para inserção em lote
            from psycopg2.extras import execute_values
            execute_values(cur, query, dados, template=None, page_size=10)

            # Verifica quantas foram realmente inseridas
            affected_rows = cur.rowcount
            conn.commit()
            
            print(f"✅ Lote executado com sucesso. {affected_rows} transações inseridas")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Erro ao executar lote de transações: {e}")
            print(f"Detalhes do erro: {type(e).__name__}")
            
            # Debug adicional do erro
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            raise
        finally:
            if conn:
                cur.close()
                conn.close()

    def buscar_transacao_por_hash(self, hash_transacao):
        """Busca uma transação pelo hash"""
        query = """
        SELECT transacao_id, tipo, data, descricao, valor, 
               tipo_movimento, fonte, hash, observacoes, data_criacao
        FROM transacoes 
        WHERE hash = %s AND ativo = TRUE
        """
        result = self.db.execute_query(query, (hash_transacao,), fetch=True)
        return dict(result[0]) if result else None

    def transacao_existe(self, hash_transacao):
        """Verifica se uma transação existe"""
        query = "SELECT COUNT(*) as count FROM transacoes WHERE hash = %s AND ativo = TRUE"
        result = self.db.execute_query(query, (hash_transacao,), fetch=True)
        return result[0]['count'] > 0


class PessoaService:
    def __init__(self):
        self.db = DatabaseService()

    def migrar_pessoas_json(self):
        """Migra pessoas das revisões existentes para a tabela pessoas"""
        try:
            # Carrega dados das revisões para extrair pessoas
            with open('data/revisoes.json', 'r', encoding='utf-8') as f:
                revisoes_json = json.load(f)

            # Verifica se a tabela existe, se não, cria
            self.criar_tabela_pessoas()

            # Extrai pessoas únicas das revisões
            pessoas_encontradas = set()
            for revisao in revisoes_json:
                donos = revisao.get('donos', {})
                pessoas_encontradas.update(donos.keys())

                pago_por = revisao.get('pago_por', '')
                if pago_por:
                    pessoas_encontradas.add(pago_por)

            # Remove strings vazias
            pessoas_encontradas.discard('')

            # Adiciona pessoas encontradas
            for pessoa in pessoas_encontradas:
                self.adicionar_pessoa(pessoa)

            print(f"Migração concluída! {len(pessoas_encontradas)} pessoas migradas.")
            return True

        except Exception as e:
            print(f"Erro na migração: {e}")
            return False

    def criar_tabela_pessoas(self):
        """Cria a tabela de pessoas se ela não existir"""
        query = """
        CREATE TABLE IF NOT EXISTS pessoas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            ativo BOOLEAN DEFAULT TRUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observacoes TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome);
        CREATE INDEX IF NOT EXISTS idx_pessoas_ativo ON pessoas(ativo);
        """
        self.db.execute_query(query)

    def listar_pessoas(self):
        """Lista todas as pessoas ativas"""
        query = "SELECT nome FROM pessoas WHERE ativo = TRUE ORDER BY nome"
        result = self.db.execute_query(query, fetch=True)
        return [row['nome'] for row in result]

    def adicionar_pessoa(self, nome):
        """Adiciona uma nova pessoa"""
        query = "INSERT INTO pessoas (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING"
        return self.db.execute_query(query, (nome,))

    def editar_pessoa(self, nome_antigo, nome_novo):
        """Edita o nome de uma pessoa"""
        query = "UPDATE pessoas SET nome = %s WHERE nome = %s AND ativo = TRUE"
        return self.db.execute_query(query, (nome_novo, nome_antigo))

    def excluir_pessoa(self, nome):
        """Marca uma pessoa como inativa (soft delete)"""
        query = "UPDATE pessoas SET ativo = FALSE WHERE nome = %s"
        return self.db.execute_query(query, (nome,))

    def pessoa_existe(self, nome):
        """Verifica se uma pessoa existe"""
        query = "SELECT COUNT(*) as count FROM pessoas WHERE nome = %s AND ativo = TRUE"
        result = self.db.execute_query(query, (nome,), fetch=True)
        return result[0]['count'] > 0

    def buscar_pessoa_por_id(self, pessoa_id):
        """Busca uma pessoa pelo ID"""
        query = "SELECT * FROM pessoas WHERE id = %s AND ativo = TRUE"
        result = self.db.execute_query(query, (pessoa_id,), fetch=True)
        return dict(result[0]) if result else None


class RevisaoService:
    def __init__(self):
        self.db = DatabaseService()

    def migrar_revisoes_json(self):
        """Migra dados do arquivo revisoes.json para o banco de dados"""
        try:
            # Carrega dados do JSON
            with open('data/revisoes.json', 'r', encoding='utf-8') as f:
                revisoes_json = json.load(f)

            # Verifica se a tabela existe, se não, cria
            self.criar_tabela_revisoes()

            # Limpa tabela existente
            self.db.execute_query("DELETE FROM revisoes")

            # Insere revisões do JSON
            for revisao in revisoes_json:
                from datetime import datetime
                data_revisao = datetime.fromisoformat(revisao.get('data_revisao').replace('Z', '+00:00'))

                self.adicionar_revisao(
                    hash_transacao=revisao.get('hash'),
                    id_original=revisao.get('id_original'),
                    nova_descricao=revisao.get('nova_descricao'),
                    donos=revisao.get('donos'),
                    comentarios=revisao.get('comentarios', ''),
                    pago_por=revisao.get('pago_por', ''),
                    quitado=revisao.get('quitado', False),
                    quitacao_individual=revisao.get('quitacao_individual', {}),
                    data_revisao=data_revisao,
                    revisado_por=revisao.get('revisado_por', '')
                )

            print(f"Migração concluída! {len(revisoes_json)} revisões migradas.")
            return True

        except Exception as e:
            print(f"Erro na migração: {e}")
            return False

    def criar_tabela_revisoes(self):
        """Cria a tabela de revisões se ela não existir"""
        query = """
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
        """
        self.db.execute_query(query)

    def listar_revisoes(self):
        """Lista todas as revisões ativas"""
        query = """
        SELECT hash, id_original, nova_descricao, donos, comentarios, 
               pago_por, quitado, quitacao_individual, data_revisao, revisado_por, ativo
        FROM revisoes 
        WHERE ativo = TRUE
        ORDER BY data_revisao DESC
        """
        result = self.db.execute_query(query, fetch=True)
        return [dict(row) for row in result]

    def adicionar_revisao(self, hash_transacao, id_original, nova_descricao, donos,
                         comentarios='', pago_por='', quitado=False, quitacao_individual=None,
                         data_revisao=None, revisado_por=''):
        """Adiciona uma nova revisão"""
        if data_revisao is None:
            from datetime import datetime
            data_revisao = datetime.now()

        if quitacao_individual is None:
            quitacao_individual = {}

        query = """
        INSERT INTO revisoes (hash, id_original, nova_descricao, donos, comentarios,
                             pago_por, quitado, quitacao_individual, data_revisao, revisado_por) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (
            hash_transacao, id_original, nova_descricao, json.dumps(donos),
            comentarios, pago_por, quitado, json.dumps(quitacao_individual),
            data_revisao, revisado_por
        ))

    def atualizar_revisao(self, hash_transacao, **kwargs):
        """Atualiza uma revisão existente"""
        campos = []
        valores = []

        for campo, valor in kwargs.items():
            if campo in ['donos', 'quitacao_individual']:
                campos.append(f"{campo} = %s")
                valores.append(json.dumps(valor))
            else:
                campos.append(f"{campo} = %s")
                valores.append(valor)

        if not campos:
            return False

        valores.append(hash_transacao)
        query = f"UPDATE revisoes SET {', '.join(campos)} WHERE hash = %s AND ativo = TRUE"
        return self.db.execute_query(query, valores)

    def buscar_revisao_por_hash(self, hash_transacao):
        """Busca uma revisão pelo hash"""
        query = """
        SELECT hash, id_original, nova_descricao, donos, comentarios,
               pago_por, quitado, quitacao_individual, data_revisao, revisado_por, ativo
        FROM revisoes 
        WHERE hash = %s AND ativo = TRUE
        """
        result = self.db.execute_query(query, (hash_transacao,), fetch=True)
        if result:
            revisao = dict(result[0])
            # Converte campos JSON de volta para dicionários
            if revisao['donos']:
                revisao['donos'] = json.loads(revisao['donos']) if isinstance(revisao['donos'], str) else revisao['donos']
            if revisao['quitacao_individual']:
                revisao['quitacao_individual'] = json.loads(revisao['quitacao_individual']) if isinstance(revisao['quitacao_individual'], str) else revisao['quitacao_individual']
            return revisao
        return None

    def revisao_existe(self, hash_transacao):
        """Verifica se uma revisão existe"""
        query = "SELECT COUNT(*) as count FROM revisoes WHERE hash = %s AND ativo = TRUE"
        result = self.db.execute_query(query, (hash_transacao,), fetch=True)
        return result[0]['count'] > 0

    def listar_hashes_revisoes(self):
        """Lista apenas os hashes das revisões ativas (para cache)"""
        query = "SELECT hash FROM revisoes WHERE ativo = TRUE"
        result = self.db.execute_query(query, fetch=True)
        return {row['hash'] for row in result}