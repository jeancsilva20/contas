
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
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["invalid password", "bad password", "incorrect password", "wrong password"]):
                raise ValueError("Senha incorreta para o arquivo")
            elif "password" in error_msg:
                raise ValueError("Erro de senha ou arquivo corrompido")
            else:
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
        Identifica se é fatura de cartão ou extrato bancário baseado nas colunas
        """
        colunas = [col.lower().strip() for col in df.columns]
        
        # Colunas características de fatura de cartão
        cartao_keywords = [
            'data de compra', 'nome no cartao', 'final do cartao', 
            'categoria', 'parcela', 'valor (em us$)', 'cotacao', 'valor (em r$)'
        ]
        
        # Colunas características de extrato bancário
        conta_keywords = [
            'data lancamento', 'data contabil', 'titulo', 
            'entrada(r$)', 'saida(r$)', 'saldo do dia'
        ]
        
        cartao_score = sum(1 for keyword in cartao_keywords 
                          if any(keyword in col for col in colunas))
        conta_score = sum(1 for keyword in conta_keywords 
                         if any(keyword in col for col in colunas))
        
        return 'cartao' if cartao_score > conta_score else 'conta'
    
    def _extrair_transacoes(self, df, tipo_arquivo):
        """
        Extrai e padroniza transações do DataFrame
        """
        transacoes = []
        
        if tipo_arquivo == 'cartao':
            # Mapeamento para fatura de cartão
            col_data = self._encontrar_coluna(df, ['data de compra', 'data_compra', 'data'])
            col_descricao = self._encontrar_coluna(df, ['descricao', 'description'])
            col_valor = self._encontrar_coluna(df, ['valor (em r$)', 'valor_rs', 'valor'])
            col_parcela = self._encontrar_coluna(df, ['parcela'])
        else:
            # Mapeamento para extrato bancário
            col_data = self._encontrar_coluna(df, ['data lancamento', 'data_lancamento', 'data'])
            col_descricao = self._encontrar_coluna(df, ['descricao', 'description'])
            col_titulo = self._encontrar_coluna(df, ['titulo'])
            col_entrada = self._encontrar_coluna(df, ['entrada(r$)', 'entrada'])
            col_saida = self._encontrar_coluna(df, ['saida(r$)', 'saida'])
        
        if not col_data or not col_descricao:
            raise ValueError("Não foi possível identificar as colunas necessárias no arquivo")
        
        for _, row in df.iterrows():
            try:
                # Extrai dados da linha
                data = pd.to_datetime(row[col_data])
                descricao = str(row[col_descricao]).strip()
                
                # Pula linhas vazias ou inválidas
                if pd.isna(data) or not descricao or descricao.lower() in ['nan', '']:
                    continue
                
                if tipo_arquivo == 'cartao':
                    if not col_valor:
                        continue
                    valor = float(row[col_valor])
                    tipo_movimento = 'saida'  # Fatura de cartão sempre é saída
                    valor_abs = abs(valor)
                    
                    # Adiciona informação de parcela se disponível
                    observacoes = ''
                    if col_parcela and not pd.isna(row[col_parcela]):
                        observacoes = f"Parcela: {row[col_parcela]}"
                        
                else:  # extrato bancário
                    # Determina valor e tipo de movimento
                    entrada = 0 if pd.isna(row[col_entrada]) else float(row[col_entrada])
                    saida = 0 if pd.isna(row[col_saida]) else float(row[col_saida])
                    
                    if entrada > 0:
                        valor_abs = entrada
                        tipo_movimento = 'entrada'
                    elif saida > 0:
                        valor_abs = saida
                        tipo_movimento = 'saida'
                    else:
                        continue  # Pula se não há valor
                    
                    # Adiciona título como observação se disponível
                    observacoes = ''
                    if col_titulo and not pd.isna(row[col_titulo]):
                        observacoes = f"Título: {row[col_titulo]}"
                
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
                    'observacoes': observacoes
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
        colunas_df = [col.lower().strip() for col in df.columns]
        
        for nome in possiveis_nomes:
            nome_lower = nome.lower().strip()
            # Busca correspondência exata primeiro
            for i, col in enumerate(colunas_df):
                if nome_lower == col:
                    return df.columns[i]
            
            # Busca correspondência parcial
            for i, col in enumerate(colunas_df):
                if nome_lower in col or col in nome_lower:
                    return df.columns[i]
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
