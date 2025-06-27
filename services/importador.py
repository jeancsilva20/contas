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

    def processar_arquivo(self, arquivo, senha=None):
        """
        Processa arquivo CSV e extrai transações
        """
        try:
            # Verifica se é CSV
            nome_arquivo = arquivo.filename.lower()
            if not nome_arquivo.endswith('.csv'):
                raise ValueError("Apenas arquivos CSV são suportados")

            return self._processar_csv(arquivo)

        except Exception as e:
            raise Exception(f"Erro ao processar arquivo: {str(e)}")

    def _processar_csv(self, arquivo):
        """
        Processa arquivo CSV do cartão de crédito
        """
        try:
            # Lê o CSV com separador ponto e vírgula
            df = pd.read_csv(arquivo, sep=';', encoding='utf-8')

            # Processa as transações
            return self._extrair_transacoes_cartao(df)

        except Exception as e:
            raise Exception(f"Erro ao processar CSV: {str(e)}")

    def _extrair_transacoes_cartao(self, df):
        """
        Extrai transações do CSV do cartão de crédito
        """
        transacoes = []

        # Verifica se as colunas necessárias existem
        colunas_necessarias = ['Data de compra', 'Descrição', 'Valor (em R$)']
        colunas_df = df.columns.tolist()

        for coluna in colunas_necessarias:
            if coluna not in colunas_df:
                raise ValueError(f"Coluna '{coluna}' não encontrada no arquivo")

        for index, row in df.iterrows():
            try:
                # Extrai dados da linha
                data_str = str(row['Data de compra']).strip()
                if not data_str or data_str.lower() in ['nan', '']:
                    continue

                # Converte data do formato DD/MM/YYYY
                data = datetime.strptime(data_str, '%d/%m/%Y')

                descricao = str(row['Descrição']).strip()
                if not descricao or descricao.lower() in ['nan', '']:
                    continue

                # Processa o valor
                valor_str = str(row['Valor (em R$)']).strip()
                if not valor_str or valor_str.lower() in ['nan', '']:
                    continue

                # Remove aspas e converte vírgula para ponto
                valor_str = valor_str.replace('"', '').replace(',', '.')
                valor = float(valor_str)
                valor_abs = abs(valor)

                # Informações adicionais se disponíveis
                observacoes = []

                # Parcela
                if 'Parcela' in colunas_df and not pd.isna(row['Parcela']):
                    parcela = str(row['Parcela']).strip()
                    if parcela and parcela.lower() != 'nan':
                        observacoes.append(f"Parcela: {parcela}")

                # Categoria
                if 'Categoria' in colunas_df and not pd.isna(row['Categoria']):
                    categoria = str(row['Categoria']).strip()
                    if categoria and categoria.lower() != 'nan':
                        observacoes.append(f"Categoria: {categoria}")

                # Nome no cartão
                if 'Nome no cartão' in colunas_df and not pd.isna(row['Nome no cartão']):
                    nome_cartao = str(row['Nome no cartão']).strip()
                    if nome_cartao and nome_cartao.lower() != 'nan':
                        observacoes.append(f"Cartão: {nome_cartao}")

                observacoes_str = ' | '.join(observacoes) if observacoes else ''

                # Gera hash único
                hash_transacao = gerar_hash_transacao(data, descricao, valor_abs, 'cartao')

                # Verifica se já existe
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
                    'fonte': 'Cartão de Crédito',
                    'hash': hash_transacao,
                    'observacoes': observacoes_str
                }

                transacoes.append(transacao)

            except Exception as e:
                # Pula linhas com erro mas continua processamento
                print(f"Erro ao processar linha {index}: {str(e)}")
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