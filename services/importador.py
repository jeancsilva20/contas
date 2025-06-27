
import pandas as pd
import os
import json
from datetime import datetime
from utils.hash import gerar_hash_transacao, transacao_existe

class ImportadorTransacoes:

    def __init__(self):
        self.dados_processados = []
        self.novas_transacoes = 0
        self.pendentes_adicionadas = 0

    def verificar_colunas(self, arquivo):
        """
        Verifica se as colunas obrigatórias estão presentes no CSV.
        Retorna as colunas encontradas e um validador.
        """
        colunas_obrigatorias = [
            'Data de compra', 
            'Nome no cartão', 
            'Final do Cartão', 
            'Categoria', 
            'Descrição', 
            'Parcela', 
            'Valor (em R$)'
        ]

        try:
            # Tenta diferentes codificações
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    # Reset do arquivo se for um objeto de arquivo
                    if hasattr(arquivo, 'seek'):
                        arquivo.seek(0)
                    
                    # Lê apenas o cabeçalho do CSV
                    df = pd.read_csv(arquivo, sep=';', decimal=',', encoding=encoding, nrows=0)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Não foi possível ler o arquivo com as codificações suportadas")
            
            colunas_encontradas = df.columns.tolist()
            
            # Reset do arquivo se for um objeto de arquivo
            if hasattr(arquivo, 'seek'):
                arquivo.seek(0)
            
            # Verifica se todas as colunas obrigatórias estão presentes
            for coluna in colunas_obrigatorias:
                if coluna not in colunas_encontradas:
                    return colunas_encontradas, False, colunas_obrigatorias
            
            return colunas_encontradas, True, colunas_obrigatorias
        
        except Exception as e:
            raise Exception(f"Erro ao verificar colunas: {str(e)}")

    def processar_arquivo(self, arquivo, fonte='Não informado'):
        """
        Processa arquivo CSV e extrai transações
        """
        try:
            # Verifica se é CSV
            nome_arquivo = arquivo.filename.lower()
            if not nome_arquivo.endswith('.csv'):
                raise ValueError("Apenas arquivos CSV são suportados")

            return self._processar_csv(arquivo, fonte)

        except Exception as e:
            raise Exception(f"Erro ao processar arquivo: {str(e)}")

    def processar_arquivo_com_mapeamento(self, arquivo, mapeamento, fonte='Não informado'):
        """
        Processa arquivo CSV com mapeamento de colunas personalizado
        """
        try:
            # Tenta diferentes codificações
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    # Reset do arquivo se for um objeto de arquivo
                    if hasattr(arquivo, 'seek'):
                        arquivo.seek(0)
                    
                    # Lê o CSV
                    df = pd.read_csv(arquivo, sep=';', decimal=',', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Não foi possível ler o arquivo com as codificações suportadas")
            
            # Aplica o mapeamento de colunas
            df_mapeado = self._aplicar_mapeamento(df, mapeamento)
            
            # Processa as transações com o DataFrame mapeado
            return self._extrair_transacoes_cartao(df_mapeado, fonte)

        except Exception as e:
            raise Exception(f"Erro ao processar arquivo com mapeamento: {str(e)}")

    def _aplicar_mapeamento(self, df, mapeamento):
        """
        Aplica o mapeamento de colunas ao DataFrame
        """
        df_novo = pd.DataFrame()
        
        for coluna_obrigatoria, coluna_csv in mapeamento.items():
            if coluna_csv == "DEIXAR_EM_BRANCO":
                # Define valores padrão baseado no tipo da coluna
                if coluna_obrigatoria == 'Valor (em R$)':
                    df_novo[coluna_obrigatoria] = 0.0
                elif coluna_obrigatoria in ['Data de compra']:
                    df_novo[coluna_obrigatoria] = '01/01/1900'
                else:
                    df_novo[coluna_obrigatoria] = ''
            else:
                # Usa a coluna mapeada do CSV original
                if coluna_csv in df.columns:
                    df_novo[coluna_obrigatoria] = df[coluna_csv]
                else:
                    # Fallback para valor padrão se a coluna não existir
                    if coluna_obrigatoria == 'Valor (em R$)':
                        df_novo[coluna_obrigatoria] = 0.0
                    elif coluna_obrigatoria in ['Data de compra']:
                        df_novo[coluna_obrigatoria] = '01/01/1900'
                    else:
                        df_novo[coluna_obrigatoria] = ''
        
        return df_novo

    def _processar_csv(self, arquivo, fonte='Não informado'):
        """
        Processa arquivo CSV do cartão de crédito com novo padrão
        """
        try:
            # Tenta diferentes codificações
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    # Reset do arquivo se for um objeto de arquivo
                    if hasattr(arquivo, 'seek'):
                        arquivo.seek(0)
                    
                    # Lê o CSV com separador ponto e vírgula e decimal vírgula
                    df = pd.read_csv(arquivo, sep=';', decimal=',', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Não foi possível ler o arquivo com as codificações suportadas")

            # Processa as transações
            return self._extrair_transacoes_cartao(df, fonte)

        except Exception as e:
            raise Exception(f"Erro ao processar CSV: {str(e)}")

    def _extrair_transacoes_cartao(self, df, fonte='Não informado'):
        """
        Extrai transações do CSV do cartão de crédito - novo padrão
        """
        transacoes = []

        # Define colunas obrigatórias
        colunas_obrigatorias = [
            'Data de compra', 
            'Nome no cartão', 
            'Final do Cartão', 
            'Categoria', 
            'Descrição', 
            'Parcela', 
            'Valor (em R$)'
        ]
        
        # Verifica se as colunas obrigatórias existem
        colunas_df = df.columns.tolist()
        for coluna in colunas_obrigatorias:
            if coluna not in colunas_df:
                raise ValueError(f"Coluna obrigatória '{coluna}' não encontrada no arquivo")

        for index, row in df.iterrows():
            try:
                # Extrai e valida data
                data_str = str(row['Data de compra']).strip()
                if not data_str or data_str.lower() in ['nan', '', 'nat']:
                    continue

                # Converte data do formato DD/MM/YYYY
                data = datetime.strptime(data_str, '%d/%m/%Y')

                # Extrai e valida descrição
                descricao = str(row['Descrição']).strip()
                if not descricao or descricao.lower() in ['nan', '']:
                    continue

                # Extrai e valida valor
                valor_str = str(row['Valor (em R$)']).strip()
                if not valor_str or valor_str.lower() in ['nan', '']:
                    continue

                # Remove aspas duplas se existirem
                valor_str = valor_str.replace('"', '')
                
                # Converte para float (pandas já trata decimal=',')
                valor = float(valor_str)
                valor_abs = abs(valor)

                # Pula valores zerados
                if valor_abs == 0:
                    continue

                # Extrai informações adicionais
                nome_cartao = str(row['Nome no cartão']).strip()
                final_cartao = str(row['Final do Cartão']).strip()
                categoria = str(row['Categoria']).strip()
                parcela = str(row['Parcela']).strip()

                # Monta observações
                observacoes = []
                
                if parcela and parcela.lower() not in ['nan', '']:
                    observacoes.append(f"Parcela: {parcela}")
                
                if categoria and categoria.lower() not in ['nan', '']:
                    observacoes.append(f"Categoria: {categoria}")
                
                if nome_cartao and nome_cartao.lower() not in ['nan', '']:
                    observacoes.append(f"Cartão: {nome_cartao}")
                
                if final_cartao and final_cartao.lower() not in ['nan', '']:
                    observacoes.append(f"Final: {final_cartao}")

                observacoes_str = ' | '.join(observacoes) if observacoes else ''

                # Gera hash único para identificar duplicatas
                hash_transacao = gerar_hash_transacao(data, descricao, valor_abs, 'cartao')

                # Verifica se transação já existe
                if transacao_existe(hash_transacao):
                    continue

                # Cria objeto de transação
                transacao = {
                    'id': f"cartao_{int(datetime.now().timestamp())}_{len(transacoes)}",
                    'tipo': 'cartao',
                    'data': data.strftime('%Y-%m-%d'),
                    'descricao': descricao,
                    'valor': valor_abs,
                    'tipo_movimento': 'saida',  # Cartão sempre é saída
                    'fonte': fonte,
                    'hash': hash_transacao,
                    'observacoes': observacoes_str
                }

                transacoes.append(transacao)

            except ValueError as e:
                # Erro de conversão de data ou valor - pula linha
                print(f"Erro ao processar linha {index}: {str(e)}")
                continue
            except Exception as e:
                # Outros erros - pula linha mas continua
                print(f"Erro inesperado na linha {index}: {str(e)}")
                continue

        return transacoes

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

        # Processa pendentes para revisão
        self._processar_pendentes(transacoes)

    def _processar_pendentes(self, transacoes):
        """
        Adiciona transações de saída aos pendentes para categorização
        """
        # Carrega revisões existentes para verificar o que já foi revisado
        revisoes = self._carregar_json('data/revisoes.json')
        hashes_revisados = {r.get('hash') for r in revisoes if r.get('hash')}

        # Carrega pendentes existentes
        pendentes = self._carregar_json('data/pendentes.json')
        hashes_pendentes = {p.get('hash') for p in pendentes if p.get('hash')}

        # Filtra transações de saída que não foram revisadas e não estão nos pendentes
        novas_pendentes = [
            t for t in transacoes 
            if (t['tipo_movimento'] == 'saida' and 
                t['hash'] not in hashes_revisados and 
                t['hash'] not in hashes_pendentes)
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
