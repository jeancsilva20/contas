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
        # Cache para melhorar performance
        self._cache_transacoes_existentes = set()
        self._cache_revisoes_existentes = set()
        self._cache_pendentes_existentes = set()

    def _inicializar_cache(self):
        """Inicializa cache com dados existentes para evitar consultas repetidas"""
        try:
            from services.database import TransacaoService, RevisaoService, PendenteService

            # Cache de transações existentes
            transacao_service = TransacaoService()
            transacoes = transacao_service.listar_transacoes()
            self._cache_transacoes_existentes = {t.get('hash') for t in transacoes if t.get('hash')}

            # Cache de revisões existentes
            revisao_service = RevisaoService()
            revisoes = revisao_service.listar_revisoes()
            self._cache_revisoes_existentes = {r.get('hash') for r in revisoes if r.get('hash')}

            # Cache de pendentes existentes
            pendente_service = PendenteService()
            pendentes = pendente_service.listar_pendentes()
            self._cache_pendentes_existentes = {p.get('hash') for p in pendentes if p.get('hash')}

        except Exception as e:
            print(f"Erro ao inicializar cache: {e}")

    def _converter_valor_brasileiro(self, valor_str):
        """
        Converte valores monetários do formato brasileiro para float
        Versão otimizada com validações mais rápidas
        """
        if not valor_str:
            return 0.0

        # Conversão rápida para string e verificações básicas
        valor_str = str(valor_str).strip()
        if not valor_str or valor_str.lower() in ['nan', '', 'nat', 'none']:
            return 0.0

        try:
            # Remove prefixos monetários de uma vez
            valor_str = valor_str.replace('"', '').replace('R$', '').replace('$ ', '').strip()

            if not valor_str:
                return 0.0

            # Detecção otimizada de formato
            if ',' in valor_str and '.' in valor_str:
                # Verifica qual é o último separador decimal
                ultimo_ponto = valor_str.rfind('.')
                ultima_virgula = valor_str.rfind(',')

                if ultimo_ponto < ultima_virgula:
                    # Formato brasileiro: 1.234,56
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                else:
                    # Formato americano: 1,234.56
                    valor_str = valor_str.replace(',', '')
            elif ',' in valor_str:
                # Só vírgula - formato decimal brasileiro simples
                valor_str = valor_str.replace(',', '.')

            return float(valor_str)

        except (ValueError, TypeError):
            return 0.0

    def _detectar_separador(self, arquivo, encoding):
        """
        Detecta automaticamente o separador do CSV de forma mais eficiente
        """
        if hasattr(arquivo, 'seek'):
            arquivo.seek(0)

        # Lê apenas os primeiros 512 bytes para detectar separador
        chunk = arquivo.read(512)
        if hasattr(arquivo, 'seek'):
            arquivo.seek(0)

        # Decodifica se necessário
        if isinstance(chunk, bytes):
            chunk = chunk.decode(encoding, errors='ignore')

        # Conta separadores apenas na primeira linha
        primeira_linha = chunk.split('\n')[0]
        virgulas = primeira_linha.count(',')
        pontos_virgulas = primeira_linha.count(';')

        return ',' if virgulas > pontos_virgulas else ';'

    def verificar_colunas(self, arquivo):
        """
        Verifica se as colunas obrigatórias estão presentes no CSV.
        Versão otimizada com menos tentativas de encoding.
        """
        colunas_obrigatorias = [
            'Data de compra', 'Nome no cartão', 'Final do Cartão', 'Categoria', 
            'Descrição', 'Parcela', 'Valor (em R$)', 'Valor Recebido (em R$)'
        ]

        try:
            # Ordem otimizada de encodings (mais comuns primeiro)
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None

            for encoding in encodings:
                try:
                    if hasattr(arquivo, 'seek'):
                        arquivo.seek(0)

                    separador = self._detectar_separador(arquivo, encoding)

                    # Lê apenas o cabeçalho (mais eficiente)
                    df = pd.read_csv(arquivo, sep=separador, decimal=',', 
                                   encoding=encoding, nrows=0)
                    break
                except (UnicodeDecodeError, pd.errors.EmptyDataError):
                    continue

            if df is None:
                raise Exception("Não foi possível ler o arquivo com as codificações suportadas")

            colunas_encontradas = df.columns.tolist()

            if hasattr(arquivo, 'seek'):
                arquivo.seek(0)

            # Verificação otimizada
            colunas_faltantes = set(colunas_obrigatorias) - set(colunas_encontradas)
            return colunas_encontradas, len(colunas_faltantes) == 0, colunas_obrigatorias

        except Exception as e:
            raise Exception(f"Erro ao verificar colunas: {str(e)}")

    def processar_arquivo(self, arquivo, fonte='Não informado'):
        """Processa arquivo CSV e extrai transações"""
        try:
            nome_arquivo = arquivo.filename.lower()
            if not nome_arquivo.endswith('.csv'):
                raise ValueError("Apenas arquivos CSV são suportados")

            return self._processar_csv(arquivo, fonte)
        except Exception as e:
            raise Exception(f"Erro ao processar arquivo: {str(e)}")

    def processar_arquivo_com_mapeamento(self, arquivo, mapeamento, fonte='Não informado'):
        """Processa arquivo CSV com mapeamento de colunas personalizado"""
        try:
            # Inicializa cache
            self._inicializar_cache()
            print(f"🔄 Cache inicializado - Transações existentes: {len(self._cache_transacoes_existentes)}")

            # Ordem otimizada de encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None

            for encoding in encodings:
                try:
                    if hasattr(arquivo, 'seek'):
                        arquivo.seek(0)

                    separador = self._detectar_separador(arquivo, encoding)
                    df = pd.read_csv(arquivo, sep=separador, decimal=',', encoding=encoding)
                    break
                except (UnicodeDecodeError, pd.errors.EmptyDataError):
                    continue

            if df is None:
                raise Exception("Não foi possível ler o arquivo com as codificações suportadas")

            df_mapeado = self._aplicar_mapeamento(df, mapeamento)
            return self._extrair_transacoes_cartao(df_mapeado, fonte)

        except Exception as e:
            raise Exception(f"Erro ao processar arquivo com mapeamento: {str(e)}")

    def _aplicar_mapeamento(self, df, mapeamento):
        """Aplica o mapeamento de colunas ao DataFrame de forma otimizada"""
        df_novo = pd.DataFrame(index=df.index)  # Mantém mesmo índice

        # Valores padrão definidos uma vez
        valores_padrao = {
            'Valor (em R$)': 0.0,
            'Data de compra': '01/01/1900'
        }

        for coluna_obrigatoria, coluna_csv in mapeamento.items():
            if coluna_csv == "DEIXAR_EM_BRANCO":
                valor_padrao = valores_padrao.get(coluna_obrigatoria, '')
                df_novo[coluna_obrigatoria] = valor_padrao
            else:
                if coluna_csv in df.columns:
                    df_novo[coluna_obrigatoria] = df[coluna_csv]
                else:
                    valor_padrao = valores_padrao.get(coluna_obrigatoria, '')
                    df_novo[coluna_obrigatoria] = valor_padrao

        return df_novo

    def _processar_csv(self, arquivo, fonte='Não informado'):
        """Processa arquivo CSV do cartão de crédito com otimizações"""
        try:
            # Inicializa cache
            self._inicializar_cache()
            print(f"🔄 Cache inicializado - Transações existentes: {len(self._cache_transacoes_existentes)}")

            # Ordem otimizada de encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None

            for encoding in encodings:
                try:
                    if hasattr(arquivo, 'seek'):
                        arquivo.seek(0)

                    separador = self._detectar_separador(arquivo, encoding)
                    df = pd.read_csv(arquivo, sep=separador, decimal=',', encoding=encoding)
                    break
                except (UnicodeDecodeError, pd.errors.EmptyDataError):
                    continue

            if df is None:
                raise Exception("Não foi possível ler o arquivo com as codificações suportadas")

            return self._extrair_transacoes_cartao(df, fonte)

        except Exception as e:
            raise Exception(f"Erro ao processar CSV: {str(e)}")

    def _extrair_transacoes_cartao(self, df, fonte='Não informado'):
        """Extrai transações do CSV de forma otimizada"""
        transacoes = []

        # Verifica colunas obrigatórias uma vez
        colunas_obrigatorias = [
            'Data de compra', 'Nome no cartão', 'Final do Cartão', 'Categoria', 
            'Descrição', 'Parcela', 'Valor (em R$)', 'Valor Recebido (em R$)'
        ]

        colunas_faltantes = set(colunas_obrigatorias) - set(df.columns)
        if colunas_faltantes:
            raise ValueError(f"Colunas obrigatórias não encontradas: {', '.join(colunas_faltantes)}")

        # Remove linhas vazias antecipadamente
        df = df.dropna(subset=['Data de compra', 'Descrição'])

        # Processa em lotes para melhor performance
        timestamp_base = int(datetime.now().timestamp())

        for index, row in df.iterrows():
            try:
                # Validação rápida de data
                data_str = str(row['Data de compra']).strip()
                if not data_str or data_str.lower() in ['nan', '', 'nat']:
                    continue

                # Validação rápida de descrição
                descricao = str(row['Descrição']).strip()
                if not descricao or descricao.lower() in ['nan', '']:
                    continue

                # Conversão otimizada de data
                try:
                    data = datetime.strptime(data_str, '%d/%m/%Y')
                except ValueError:
                    continue

                # Conversão otimizada de valores
                valor = self._converter_valor_brasileiro(row['Valor (em R$)'])
                valor_recebido = self._converter_valor_brasileiro(row.get('Valor Recebido (em R$)', ''))

                # Determina tipo de movimento e valor final
                tipo_movimento, valor_final = self._determinar_tipo_movimento(valor, valor_recebido)

                if valor_final == 0:
                    continue

                # Gera hash e verifica duplicata usando cache
                hash_transacao = gerar_hash_transacao(data, descricao, valor_final, 'cartao')
                if hash_transacao in self._cache_transacoes_existentes:
                    continue

                # Monta observações de forma otimizada
                observacoes_str = self._montar_observacoes(row)

                # Valor para armazenamento
                valor_para_armazenar = -valor_final if tipo_movimento == 'entrada' else valor_final

                # Cria transação
                transacao = {
                    'id': f"cartao_{timestamp_base}_{len(transacoes)}",
                    'tipo': 'cartao',
                    'data': data.strftime('%Y-%m-%d'),
                    'descricao': descricao,
                    'valor': valor_para_armazenar,
                    'tipo_movimento': tipo_movimento,
                    'fonte': fonte,
                    'hash': hash_transacao,
                    'observacoes': observacoes_str
                }
                
                transacoes.append(transacao)
                
                # Log a cada 10 transações processadas
                if len(transacoes) % 10 == 0:
                    print(f"📊 {len(transacoes)} transações processadas...")
                # Atualiza cache
                self._cache_transacoes_existentes.add(hash_transacao)

            except Exception as e:
                # Log do erro sem interromper processamento
                print(f"Erro na linha {index}: {str(e)}")
                continue

        return transacoes

    def _determinar_tipo_movimento(self, valor, valor_recebido):
        """Determina tipo de movimento de forma otimizada"""
        if valor_recebido == 0 and valor < 0:
            return 'entrada', abs(valor)
        elif valor == 0 and valor_recebido > 0:
            return 'entrada', valor_recebido
        elif valor > 0 and valor_recebido == 0:
            return 'saida', valor
        elif valor_recebido > 0:
            return 'entrada', valor_recebido
        else:
            return 'saida', abs(valor)

    def _montar_observacoes(self, row):
        """Monta observações de forma otimizada"""
        observacoes = []

        # Campos e suas labels
        campos = [
            ('Parcela', 'Parcela'),
            ('Categoria', 'Categoria'),
            ('Nome no cartão', 'Cartão'),
            ('Final do Cartão', 'Final')
        ]

        for campo, label in campos:
            valor = str(row.get(campo, '')).strip()
            if valor and valor.lower() not in ['nan', '']:
                observacoes.append(f"{label}: {valor}")

        return ' | '.join(observacoes)

    def salvar_transacoes(self, transacoes):
        """Salva transações no banco de dados usando processamento em lotes otimizado"""
        if not transacoes:
            print("⚠️ Nenhuma transação para salvar")
            return

        from services.database import TransacaoService

        transacao_service = TransacaoService()
        novas_transacoes_count = 0

        print(f"💾 Iniciando salvamento de {len(transacoes)} transações...")

        # Processa em lotes de 10 transações para evitar sobrecarga
        batch_size = 10
        total_batches = (len(transacoes) + batch_size - 1) // batch_size
        
        for i in range(0, len(transacoes), batch_size):
            batch_num = (i // batch_size) + 1
            batch = transacoes[i:i + batch_size]
            
            print(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} transações)...")
            
            try:
                # Valida estrutura do lote antes de enviar
                for j, transacao in enumerate(batch):
                    if not isinstance(transacao, dict):
                        print(f"❌ Erro: Item {j} do lote {batch_num} não é um dicionário")
                        continue
                    
                    required_fields = ['id', 'tipo', 'data', 'descricao', 'valor', 'tipo_movimento', 'fonte', 'hash']
                    missing_fields = [field for field in required_fields if field not in transacao]
                    
                    if missing_fields:
                        print(f"❌ Erro: Item {j} do lote {batch_num} tem campos faltantes: {missing_fields}")
                        continue
                
                # Envia lote para o banco
                transacao_service.adicionar_transacoes_lote(batch)
                novas_transacoes_count += len(batch)
                print(f"✅ Lote {batch_num}/{total_batches} processado com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao processar lote {batch_num}: {e}")
                # Continua com próximo lote mesmo se um falhar
                continue

        self.novas_transacoes = novas_transacoes_count
        print(f"💾 Salvamento concluído. Total processado: {novas_transacoes_count} transações")
        
        # Processa pendentes após salvamento bem-sucedido
        self._processar_pendentes(transacoes)

    def _processar_pendentes(self, transacoes):
        """Adiciona transações aos pendentes usando cache com processamento otimizado"""
        from services.database import PendenteService

        pendente_service = PendenteService()
        novas_pendentes = []

        print(f"🔄 Verificando {len(transacoes)} transações para pendentes...")

        # Filtra usando cache
        for i, transacao in enumerate(transacoes):
            try:
                hash_transacao = transacao.get('hash')
                if not hash_transacao:
                    print(f"⚠️ Transação {i} sem hash, pulando...")
                    continue
                    
                if (hash_transacao not in self._cache_revisoes_existentes and 
                    hash_transacao not in self._cache_pendentes_existentes):
                    novas_pendentes.append(transacao)
                    print(f"➕ Transação {i} adicionada aos pendentes")
                else:
                    print(f"⏭️ Transação {i} já existe em revisões ou pendentes")
                    
            except Exception as e:
                print(f"❌ Erro ao processar transação {i} para pendentes: {e}")
                continue

        # Processa pendentes em lotes menores
        if novas_pendentes:
            print(f"📋 Processando {len(novas_pendentes)} novas transações pendentes...")
            
            batch_size = 10  # Reduzido para evitar sobrecarga
            total_batches = (len(novas_pendentes) + batch_size - 1) // batch_size
            
            for i in range(0, len(novas_pendentes), batch_size):
                batch_num = (i // batch_size) + 1
                batch = novas_pendentes[i:i + batch_size]
                
                try:
                    print(f"📦 Processando lote de pendentes {batch_num}/{total_batches}...")
                    
                    # Verifica se o serviço de pendentes tem método para lotes
                    if hasattr(pendente_service, 'adicionar_transacoes_lote'):
                        pendente_service.adicionar_transacoes_lote(batch)
                    else:
                        # Fallback: adiciona um por um
                        for transacao in batch:
                            pendente_service.adicionar_pendente(
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
                    
                    print(f"✅ Lote de pendentes {batch_num}/{total_batches} processado")
                    
                except Exception as e:
                    print(f"❌ Erro ao processar lote de pendentes {batch_num}: {e}")
                    continue

            self.pendentes_adicionadas = len(novas_pendentes)
            print(f"📋 Processamento de pendentes concluído: {self.pendentes_adicionadas} adicionadas")
        else:
            print("📋 Nenhuma transação nova para pendentes")
            self.pendentes_adicionadas = 0

    def _carregar_json(self, caminho):
        """Carrega arquivo JSON ou retorna lista vazia se não existir"""
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _salvar_json(self, caminho, dados):
        """Salva dados em arquivo JSON com formatação"""
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)