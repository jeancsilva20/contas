
import pandas as pd
import msoffcrypto
import io
import os
import json
from datetime import datetime
from utils.hash import gerar_hash_transacao, transacao_existe

class ImportadorTransacoes:
    
    def __init__(self):
        self.dados_processados = []
        self.novas_transacoes = 0
        self.pendentes_adicionadas = 0
    
    def processar_arquivo(self, arquivo, senha=None):
        """
        Processa arquivo Excel ou CSV e extrai transações
        """
        try:
            # Determina o tipo de arquivo
            nome_arquivo = arquivo.filename.lower()
            
            if nome_arquivo.endswith(('.xlsx', '.xls')):
                return self._processar_excel(arquivo, senha)
            elif nome_arquivo.endswith('.csv'):
                return self._processar_csv(arquivo)
            else:
                raise ValueError("Formato de arquivo não suportado")
                
        except Exception as e:
            raise Exception(f"Erro ao processar arquivo: {str(e)}")
    
    def _processar_excel(self, arquivo, senha):
        """
        Processa arquivo Excel com senha
        """
        if not senha:
            raise ValueError("Senha é obrigatória para arquivos Excel")
        
        try:
            # Lê o arquivo em bytes
            arquivo_bytes = arquivo.read()
            arquivo.seek(0)  # Reset para próximas operações
            
            # Descriptografa o arquivo
            file_obj = io.BytesIO(arquivo_bytes)
            office_file = msoffcrypto.OfficeFile(file_obj)
            office_file.load_key(password=senha)
            
            # Cria um novo BytesIO para o arquivo descriptografado
            decrypted = io.BytesIO()
            office_file.decrypt(decrypted)
            decrypted.seek(0)
            
            # Lê com pandas
            df = pd.read_excel(decrypted)
            
            # Determina o tipo baseado nas colunas
            tipo_arquivo = self._identificar_tipo_arquivo(df)
            
            # Processa as transações
            return self._extrair_transacoes(df, tipo_arquivo)
            
        except Exception as e:
            if "Invalid password" in str(e) or "Bad password" in str(e):
                raise ValueError("Senha incorreta")
            raise Exception(f"Erro ao processar Excel: {str(e)}")
    
    def _processar_csv(self, arquivo):
        """
        Processa arquivo CSV
        """
        try:
            # Lê o CSV
            df = pd.read_csv(arquivo)
            
            # Determina o tipo baseado nas colunas
            tipo_arquivo = self._identificar_tipo_arquivo(df)
            
            # Processa as transações
            return self._extrair_transacoes(df, tipo_arquivo)
            
        except Exception as e:
            raise Exception(f"Erro ao processar CSV: {str(e)}")
    
    def _identificar_tipo_arquivo(self, df):
        """
        Identifica se é fatura de cartão ou extrato bancário
        """
        colunas = [col.lower() for col in df.columns]
        
        # Palavras-chave para identificação
        cartao_keywords = ['fatura', 'cartao', 'card', 'limite']
        conta_keywords = ['extrato', 'saldo', 'conta', 'banco']
        
        cartao_score = sum(1 for keyword in cartao_keywords if any(keyword in col for col in colunas))
        conta_score = sum(1 for keyword in conta_keywords if any(keyword in col for col in colunas))
        
        return 'cartao' if cartao_score >= conta_score else 'conta'
    
    def _extrair_transacoes(self, df, tipo_arquivo):
        """
        Extrai e padroniza transações do DataFrame
        """
        transacoes = []
        
        # Mapeia colunas possíveis para nossos campos padrão
        mapeamento_data = ['data', 'date', 'data_transacao', 'data_compra']
        mapeamento_descricao = ['descricao', 'description', 'estabelecimento', 'historico', 'memo']
        mapeamento_valor = ['valor', 'value', 'amount', 'quantia']
        
        # Encontra as colunas correspondentes
        col_data = self._encontrar_coluna(df, mapeamento_data)
        col_descricao = self._encontrar_coluna(df, mapeamento_descricao)
        col_valor = self._encontrar_coluna(df, mapeamento_valor)
        
        if not all([col_data, col_descricao, col_valor]):
            raise ValueError("Não foi possível identificar as colunas necessárias no arquivo")
        
        for _, row in df.iterrows():
            try:
                # Extrai dados da linha
                data = pd.to_datetime(row[col_data])
                descricao = str(row[col_descricao]).strip()
                valor = float(row[col_valor])
                
                # Pula linhas vazias ou inválidas
                if pd.isna(data) or not descricao or descricao.lower() in ['nan', '']:
                    continue
                
                # Determina tipo de movimento
                tipo_movimento = 'saida' if valor < 0 else 'entrada'
                valor_abs = abs(valor)
                
                # Determina fonte baseada no tipo
                fonte = self._determinar_fonte(tipo_arquivo)
                
                # Gera hash único
                hash_transacao = gerar_hash_transacao(data, descricao, valor_abs, tipo_arquivo)
                
                # Verifica se já existe
                if transacao_existe(hash_transacao):
                    continue
                
                # Cria objeto de transação
                transacao = {
                    'id': f"{tipo_arquivo}_{int(datetime.now().timestamp())}_{len(transacoes)}",
                    'tipo': tipo_arquivo,
                    'data': data.strftime('%Y-%m-%d'),
                    'descricao': descricao,
                    'valor': valor_abs,
                    'tipo_movimento': tipo_movimento,
                    'fonte': fonte,
                    'hash': hash_transacao,
                    'observacoes': ''
                }
                
                transacoes.append(transacao)
                
            except Exception as e:
                # Pula linhas com erro mas continua processamento
                continue
        
        return transacoes
    
    def _encontrar_coluna(self, df, possiveis_nomes):
        """
        Encontra a coluna correspondente baseada em nomes possíveis
        """
        colunas_df = [col.lower() for col in df.columns]
        
        for nome in possiveis_nomes:
            for col in colunas_df:
                if nome in col:
                    # Retorna o nome original da coluna
                    return df.columns[colunas_df.index(col)]
        return None
    
    def _determinar_fonte(self, tipo_arquivo):
        """
        Determina a fonte baseada no tipo de arquivo
        """
        if tipo_arquivo == 'cartao':
            return 'C6 Carbon'
        else:
            return 'C6 Conta Corrente'
    
    def salvar_transacoes(self, transacoes):
        """
        Salva transações nos arquivos apropriados
        """
        if not transacoes:
            return
        
        # Garante que o diretório data existe
        os.makedirs('data', exist_ok=True)
        
        # Carrega transações existentes
        transacoes_existentes = self._carregar_json('data/transacoes.json')
        
        # Adiciona novas transações
        transacoes_existentes.extend(transacoes)
        self.novas_transacoes = len(transacoes)
        
        # Salva transações atualizadas
        self._salvar_json('data/transacoes.json', transacoes_existentes)
        
        # Processa pendentes (apenas saídas não revisadas)
        self._processar_pendentes(transacoes)
    
    def _processar_pendentes(self, transacoes):
        """
        Adiciona transações de saída aos pendentes se não foram revisadas
        """
        # Carrega revisões existentes
        revisoes = self._carregar_json('data/revisoes.json')
        hashes_revisados = {r.get('hash') for r in revisoes if r.get('hash')}
        
        # Carrega pendentes existentes
        pendentes = self._carregar_json('data/pendentes.json')
        
        # Filtra saídas não revisadas
        novas_pendentes = [
            t for t in transacoes 
            if t['tipo_movimento'] == 'saida' and t['hash'] not in hashes_revisados
        ]
        
        if novas_pendentes:
            pendentes.extend(novas_pendentes)
            self.pendentes_adicionadas = len(novas_pendentes)
            self._salvar_json('data/pendentes.json', pendentes)
    
    def _carregar_json(self, caminho):
        """
        Carrega arquivo JSON ou retorna lista vazia se não existir
        """
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _salvar_json(self, caminho, dados):
        """
        Salva dados em arquivo JSON com formatação
        """
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
