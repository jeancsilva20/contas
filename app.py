import os
import atexit
import glob


def cleanup_temp_files():
    """Limpa arquivos temporários antigos na inicialização e encerramento"""
    try:
        temp_dir = 'temp'
        if os.path.exists(temp_dir):
            for temp_file in glob.glob(os.path.join(temp_dir, '*.csv')):
                try:
                    os.remove(temp_file)
                except:
                    pass
    except:
        pass


# Registra função de limpeza para ser executada ao encerrar a aplicação
atexit.register(cleanup_temp_files)

from flask import Flask, render_template, request, jsonify, session, redirect
import os

def inicializar_banco_dados():
    """Inicializa as tabelas do banco de dados se elas não existirem"""
    try:
        print("🚀 Verificando e criando estrutura do banco de dados...")
        print("=" * 60)
        
        from services.database import FonteService, PendenteService, TransacaoService, RevisaoService, PessoaService
        
        # Teste inicial de conexão e escolha de URL
        print("🔌 Testando conexões com banco de dados...")
        db_service = FonteService().db  # Usa o DatabaseService para testar conexão
        
        # Criar todas as tabelas
        print("\n📂 Criando tabela de fontes...")
        fonte_service = FonteService()
        fonte_service.criar_tabela_fontes()
        
        print("⏳ Criando tabela de pendentes...")
        pendente_service = PendenteService()
        pendente_service.criar_tabela_pendentes()
        
        print("💰 Criando tabela de transações...")
        transacao_service = TransacaoService()
        transacao_service.criar_tabela_transacoes()
        
        print("📝 Criando tabela de revisões...")
        revisao_service = RevisaoService()
        revisao_service.criar_tabela_revisoes()
        
        print("👥 Criando tabela de pessoas...")
        pessoa_service = PessoaService()
        pessoa_service.criar_tabela_pessoas()
        
        # Adicionar fontes padrão se não existirem
        print("\n📋 Adicionando fontes padrão...")
        fontes_padrao = ["Cartão C6", "Conta C6", "Cartão XP", "Conta XP", "Cartão C6 Tati", "Manual"]
        fontes_adicionadas = 0
        for fonte in fontes_padrao:
            if not fonte_service.fonte_existe(fonte):
                fonte_service.adicionar_fonte(fonte)
                print(f"   + {fonte}")
                fontes_adicionadas += 1
        
        if fontes_adicionadas == 0:
            print("   ✓ Todas as fontes padrão já existem")
        
        # Adicionar pessoas padrão se não existirem
        print("\n👥 Adicionando pessoas padrão...")
        pessoas_padrao = ["Jean", "João Batista", "João Rafael", "Juliano", "Tati"]
        pessoas_adicionadas = 0
        for pessoa in pessoas_padrao:
            if not pessoa_service.pessoa_existe(pessoa):
                pessoa_service.adicionar_pessoa(pessoa)
                print(f"   + {pessoa}")
                pessoas_adicionadas += 1
        
        if pessoas_adicionadas == 0:
            print("   ✓ Todas as pessoas padrão já existem")
        
        print("\n" + "=" * 60)
        print("✅ Banco de dados inicializado com sucesso!")
        print(f"🔗 Usando conexão: {db_service.database_url}")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar banco de dados: {e}")
        print("💡 Verifique se as credenciais do banco estão corretas")
        return False

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123456789'  # Necessário para sessões

# Inicializar banco de dados na inicialização da aplicação
with app.app_context():
    inicializar_banco_dados()


@app.route('/')
def index():
    return redirect('/rateio')


@app.route('/dados')
def dados():
    """
    Exibe página principal de gerenciamento de dados com tabs
    """
    return render_template('dados.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/upload_content')
def upload_content():
    """
    Retorna apenas o conteúdo da tab de upload
    """
    return render_template('upload_content.html')


@app.route('/fontes_content')
def fontes_content():
    """
    Retorna apenas o conteúdo da tab de fontes
    """
    try:
        from services.database import FonteService
        fonte_service = FonteService()
        fontes = fonte_service.listar_fontes()

        if not fontes:
            print("⚠️ Nenhuma fonte encontrada, tentando migração...")
            if fonte_service.migrar_fontes_json():
                fontes = fonte_service.listar_fontes()
                print(f"✅ {len(fontes)} fontes migradas")

        print(f"📋 Carregando {len(fontes)} fontes")
        return render_template('fontes_content.html', fontes=fontes)
    except Exception as e:
        print(f"❌ Erro ao carregar fontes: {str(e)}")
        return f"Erro ao carregar fontes: {str(e)}", 500


@app.route('/pessoas_content')
def pessoas_content():
    """
    Retorna apenas o conteúdo da tab de pessoas
    """
    try:
        from services.database import PessoaService
        pessoa_service = PessoaService()
        pessoas = pessoa_service.listar_pessoas()

        if not pessoas:
            print("⚠️ Nenhuma pessoa encontrada, tentando migração...")
            if pessoa_service.migrar_pessoas_json():
                pessoas = pessoa_service.listar_pessoas()
                print(f"✅ {len(pessoas)} pessoas migradas")

        print(f"👥 Carregando {len(pessoas)} pessoas")
        return render_template('pessoas_content.html', pessoas=pessoas)
    except Exception as e:
        print(f"❌ Erro ao carregar pessoas: {str(e)}")
        return f"Erro ao carregar pessoas: {str(e)}", 500


@app.route('/limpar_base_content')
def limpar_base_content():
    """
    Retorna apenas o conteúdo da tab de limpar base
    """
    return render_template('limpar_base_content.html')


@app.route('/get_fontes')
def get_fontes():
    """
    Retorna lista de fontes disponíveis
    """
    try:
        from services.database import FonteService

        fonte_service = FonteService()
        fontes = fonte_service.listar_fontes()

        # Se não há fontes no banco, faz migração inicial
        if not fontes:
            if fonte_service.migrar_fontes_json():
                fontes = fonte_service.listar_fontes()

        return jsonify(fontes)

    except Exception as e:
        return jsonify({'error': f'Erro ao carregar fontes: {str(e)}'}), 500


@app.route('/fontes')
def fontes():
    """
    Exibe tela de gerenciamento de fontes
    """
    try:
        from services.database import FonteService

        fonte_service = FonteService()
        fontes = fonte_service.listar_fontes()

        # Se não há fontes no banco, faz migração inicial
        if not fontes:
            if fonte_service.migrar_fontes_json():
                fontes = fonte_service.listar_fontes()

        return render_template('fontes.html', fontes=fontes)

    except Exception as e:
        return f"Erro ao carregar fontes: {str(e)}", 500


@app.route('/salvar_fonte', methods=['POST'])
def salvar_fonte():
    """
    Adiciona uma nova fonte
    """
    try:
        from services.database import FonteService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome da fonte é obrigatório'
            })

        nome_fonte = dados['nome'].strip()

        if not nome_fonte:
            return jsonify({
                'success': False,
                'message': 'Nome da fonte não pode estar vazio'
            })

        fonte_service = FonteService()

        # Verifica se a fonte já existe
        if fonte_service.fonte_existe(nome_fonte):
            return jsonify({
                'success': False,
                'message': 'Esta fonte já existe'
            })

        # Adiciona nova fonte
        fonte_service.adicionar_fonte(nome_fonte)

        return jsonify({
            'success': True,
            'message': 'Fonte adicionada com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar fonte: {str(e)}'
        })


@app.route('/editar_fonte', methods=['POST'])
def editar_fonte():
    """
    Edita uma fonte existente
    """
    try:
        from services.database import FonteService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('nome_antigo') or not dados.get('nome_novo'):
            return jsonify({
                'success': False,
                'message': 'Nome antigo e novo são obrigatórios'
            })

        nome_antigo = dados['nome_antigo'].strip()
        nome_novo = dados['nome_novo'].strip()

        if not nome_novo:
            return jsonify({
                'success': False,
                'message': 'Nome da fonte não pode estar vazio'
            })

        fonte_service = FonteService()

        # Verifica se a fonte antiga existe
        if not fonte_service.fonte_existe(nome_antigo):
            return jsonify({
                'success': False,
                'message': 'Fonte não encontrada'
            })

        # Verifica se o novo nome já existe (exceto se for o mesmo)
        if nome_novo != nome_antigo and fonte_service.fonte_existe(nome_novo):
            return jsonify({
                'success': False,
                'message': 'Já existe uma fonte com este nome'
            })

        # Atualiza a fonte
        fonte_service.editar_fonte(nome_antigo, nome_novo)

        return jsonify({
            'success': True,
            'message': 'Fonte editada com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao editar fonte: {str(e)}'
        })


@app.route('/excluir_fonte', methods=['POST'])
def excluir_fonte():
    """
    Exclui uma fonte
    """
    try:
        from services.database import FonteService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome da fonte é obrigatório'
            })

        nome_fonte = dados['nome'].strip()
        fonte_service = FonteService()

        # Verifica se a fonte existe
        if not fonte_service.fonte_existe(nome_fonte):
            return jsonify({
                'success': False,
                'message': 'Fonte não encontrada'
            })

        # Remove a fonte (soft delete)
        fonte_service.excluir_fonte(nome_fonte)

        return jsonify({
            'success': True,
            'message': 'Fonte excluída com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir fonte: {str(e)}'
        })


@app.route('/pendentes')
def pendentes():
    """
    Exibe transações pendentes de categorização
    """
    from services.database import PendenteService, PessoaService

    try:
        # Carrega dados do banco
        pendente_service = PendenteService()
        pessoa_service = PessoaService()

        print("🔄 Carregando pendentes do banco...")
        pendentes_data = pendente_service.listar_pendentes()
        print(f"📋 Encontrados {len(pendentes_data)} pendentes")

        # Obtém lista de pessoas do banco
        pessoas_lista = pessoa_service.listar_pessoas()

        # Se não há pessoas no banco, faz migração inicial
        if not pessoas_lista:
            print("⚠️ Nenhuma pessoa encontrada, tentando migração...")
            if pessoa_service.migrar_pessoas_json():
                pessoas_lista = pessoa_service.listar_pessoas()
                print(f"✅ {len(pessoas_lista)} pessoas migradas")

    except Exception as e:
        print(f"❌ Erro ao carregar pendentes: {e}")
        pendentes_data = []
        pessoas_lista = []

    return render_template('pendentes.html', 
                         pendentes=pendentes_data,
                         pessoas=pessoas_lista)


@app.route('/process_upload', methods=['POST'])
def process_upload():
    try:
        file = request.files.get('file')
        fonte = request.form.get('fonte')

        # Validações básicas
        if not file:
            return jsonify({
                'success': False,
                'message': 'Arquivo é obrigatório'
            })

        if not fonte:
            return jsonify({
                'success': False,
                'message': 'Fonte é obrigatória'
            })

        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'message': 'Apenas arquivos CSV são suportados'
            })

        # Importa o serviço de importação
        from services.importador import ImportadorTransacoes

        # Verifica as colunas do arquivo
        importador = ImportadorTransacoes()

        # Salva o arquivo temporariamente no sistema de arquivos
        import tempfile
        import uuid

        file_content = file.read()
        file.seek(0)  # Reset para poder ler novamente

        # Gera um ID único para o arquivo temporário
        temp_id = str(uuid.uuid4())
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, f"{temp_id}.csv")

        # Salva o arquivo temporariamente
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)

        # Armazena apenas metadados na sessão
        session['temp_file_id'] = temp_id
        session['temp_file_name'] = file.filename
        session['temp_fonte'] = fonte

        # Sempre redireciona para a tela de mapeamento, independente do conteúdo
        return jsonify({
            'success': False,
            'requires_mapping': True,
            'message': 'Redirecionando para mapeamento de colunas.',
            'redirect_url': '/mapear_colunas'
        })

    except ValueError as e:
        # Erros de validação
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        # Outros erros
        return jsonify({
            'success': False,
            'message': f'Erro ao processar arquivo: {str(e)}'
        })


@app.route('/resumo')
def resumo():
    """
    Exibe painel com resumo dos dados revisados
    """
    try:
        import json
        from collections import defaultdict
        from datetime import datetime

        # Obtém filtros da query string
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        responsavel = request.args.get('responsavel', '')
        valor_minimo = request.args.get('valor_minimo', '')
        valor_maximo = request.args.get('valor_maximo', '')
        pago_por = request.args.get('pago_por', '')
        status_transacao = request.args.get('status_transacao', '')

        # Carrega revisões
        try:
            with open('data/revisoes.json', 'r', encoding='utf-8') as f:
                revisoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            revisoes = []

        # Carrega transações para obter valores e datas
        try:
            with open('data/transacoes.json', 'r', encoding='utf-8') as f:
                transacoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            transacoes = []

        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}

        # Análise dos dados
        total_geral = 0
        por_categoria = defaultdict(float)
        por_mes = defaultdict(float)
        por_pessoa = defaultdict(float)

        for revisao in revisoes:
            # Busca dados da transação original
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue

            # Aplica filtro de data
            data_str = transacao['data']
            if data_inicio and data_str < data_inicio:
                continue
            if data_fim and data_str > data_fim:
                continue

            # Aplica filtro de quem pagou
            pago_por_revisao = revisao.get('pago_por', '')
            if pago_por and pago_por_revisao != pago_por:
                continue

            # Para entradas (valores negativos), mantém como negativo no cálculo
            # Para saídas (valores positivos), usa valor absoluto
            if transacao.get('tipo_movimento') == 'entrada':
                valor = transacao['valor']  # Mantém negativo para entradas
            else:
                valor = abs(transacao['valor'])  # Valor absoluto para saídas

            donos = revisao.get('donos', {})

            # Aplica filtro de responsável
            if responsavel:
                if responsavel not in donos or donos[responsavel] == 0:
                    continue
                # Quando há filtro de responsável, só considera o valor atribuído a essa pessoa
                valor_pessoa_filtrada = valor * (donos[responsavel] / 100)

                # Total geral (só o valor da pessoa filtrada)
                total_geral += valor_pessoa_filtrada

                # Por mês (só o valor da pessoa filtrada)
                try:
                    data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                    mes_ano = data_obj.strftime('%Y-%m')
                    por_mes[mes_ano] += valor_pessoa_filtrada
                except:
                    pass

                # Por pessoa (só a pessoa filtrada)
                por_pessoa[responsavel] += valor_pessoa_filtrada

                # Por categoria (só o valor da pessoa filtrada)
                observacoes = transacao.get('observacoes', '')
                categoria = 'Outros'
                if 'Categoria:' in observacoes:
                    try:
                        categoria = observacoes.split('Categoria:')[1].split(
                            '|')[0].strip()
                    except:
                        pass
                por_categoria[categoria] += valor_pessoa_filtrada
            else:
                # Sem filtro de responsável - considera valor total
                total_geral += valor

                # Por mês
                try:
                    data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                    mes_ano = data_obj.strftime('%Y-%m')
                    por_mes[mes_ano] += valor
                except:
                    pass

                # Por pessoa (baseado nos donos da revisão)
                for pessoa, percentual in donos.items():
                    valor_pessoa = valor * (percentual / 100)
                    por_pessoa[pessoa] += valor_pessoa

                # Por categoria
                observacoes = transacao.get('observacoes', '')
                categoria = 'Outros'
                if 'Categoria:' in observacoes:
                    try:
                        categoria = observacoes.split('Categoria:')[1].split(
                            '|')[0].strip()
                    except:
                        pass
                por_categoria[categoria] += valor

        # Ordena dados para gráficos
        meses_ordenados = sorted(por_mes.keys())
        dados_mensais = [{
            'mes': mes,
            'valor': por_mes[mes]
        } for mes in meses_ordenados]

        dados_categoria = [{
            'categoria': cat,
            'valor': valor
        } for cat, valor in sorted(
            por_categoria.items(), key=lambda x: x[1], reverse=True)]

        dados_pessoa = [{
            'pessoa': pessoa,
            'valor': valor
        } for pessoa, valor in sorted(
            por_pessoa.items(), key=lambda x: x[1], reverse=True)]

        # Obter lista de responsáveis únicos para o filtro
        responsaveis_unicos = set()
        pessoas_pagaram = set()
        for revisao in revisoes:
            donos = revisao.get('donos', {})
            responsaveis_unicos.update(donos.keys())
            pago_por_revisao = revisao.get('pago_por', '')
            if pago_por_revisao:
                pessoas_pagaram.add(pago_por_revisao)
        responsaveis_unicos = sorted(list(responsaveis_unicos))
        pessoas_pagaram = sorted(list(pessoas_pagaram))

        return render_template('resumo.html',
                               total_geral=total_geral,
                               dados_categoria=dados_categoria,
                               dados_mensais=dados_mensais,
                               dados_pessoa=dados_pessoa,
                               total_revisoes=len(revisoes),
                               responsaveis_unicos=responsaveis_unicos,
                               data_inicio=data_inicio,
                               data_fim=data_fim,
                               responsavel=responsavel,
                               pessoas_pagaram=pessoas_pagaram,
                               valor_minimo=valor_minimo,
                               valor_maximo=valor_maximo,
                               pago_por=pago_por,
                               status_transacao=status_transacao)

    except Exception as e:
        return f"Erro ao carregar resumo: {str(e)}", 500


@app.route('/rateio')
def rateio():
    """
    Exibe rateio dos custos entre as pessoas baseado nas revisões
    """
    try:
        from services.database import RevisaoService, TransacaoService
        from collections import defaultdict

        # Obtém filtros da query string
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        status_filter = request.args.get('status_filter', '')

        # Carrega dados do banco
        revisao_service = RevisaoService()
        transacao_service = TransacaoService()

        revisoes = revisao_service.listar_revisoes()
        transacoes = transacao_service.listar_transacoes()

        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}

        # Calcula valores por pessoa
        rateio_pessoa = defaultdict(lambda: {'total': 0, 'quitado': 0, 'pendente': 0})
        total_geral = 0
        total_quitado = 0
        total_pendente = 0
        total_transacoes = 0

        for revisao in revisoes:
            # Busca dados da transação original
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue

            # Aplica filtro de data
            data_str = transacao['data']
            if data_inicio and data_str < data_inicio:
                continue
            if data_fim and data_str > data_fim:
                continue

            # Para entradas, mantém valor negativo; para saídas, usa absoluto
            if transacao.get('tipo_movimento') == 'entrada':
                valor = float(transacao['valor'])  # Negativo para entradas
            else:
                valor = abs(float(transacao['valor']))  # Positivo para saídas

            total_geral += valor
            total_transacoes += 1

            # Distribui valor baseado nos percentuais e status de quitação
            donos = revisao.get('donos', {})
            quitacao_individual = revisao.get('quitacao_individual', {})

            for pessoa, percentual in donos.items():
                valor_pessoa = valor * (percentual / 100)
                rateio_pessoa[pessoa]['total'] += valor_pessoa

                # Verifica se esta pessoa quitou individualmente
                if quitacao_individual.get(pessoa, False):
                    rateio_pessoa[pessoa]['quitado'] += valor_pessoa
                    total_quitado += valor_pessoa
                else:
                    rateio_pessoa[pessoa]['pendente'] += valor_pessoa
                    total_pendente += valor_pessoa

        # Aplica filtro de status se especificado
        if status_filter:
            dados_filtrados = {}
            for pessoa, valores in rateio_pessoa.items():
                if status_filter == 'pendente' and valores['pendente'] > 0:
                    dados_filtrados[pessoa] = valores
                elif status_filter == 'quitado' and valores['quitado'] > 0:
                    dados_filtrados[pessoa] = valores
            rateio_pessoa = dados_filtrados

        # Ordena por valor total (maior para menor)
        dados_rateio = [{
            'pessoa': pessoa,
            'valor_total': valores['total'],
            'valor_quitado': valores['quitado'],
            'valor_pendente': valores['pendente'],
            'percentual_total': (valores['total'] / total_geral * 100) if total_geral > 0 else 0
        } for pessoa, valores in sorted(
            rateio_pessoa.items(), key=lambda x: x[1]['total'], reverse=True)]

        # Calcula saldos entre pessoas (mesmo código da tela de pagamentos)
        saldos_entre_pessoas = calcular_saldos_entre_pessoas(revisoes, transacoes_map)

        # Identifica dívidas pendentes para alertas
        dividas_pendentes = []
        for saldo in saldos_entre_pessoas:
            if abs(saldo['saldo']) > 0.01:  # Ignora valores muito pequenos
                if saldo['saldo'] > 0:
                    dividas_pendentes.append({
                        'devedor': saldo['pessoa2'],
                        'credor': saldo['pessoa1'],
                        'valor': saldo['saldo']
                    })
                else:
                    dividas_pendentes.append({
                        'devedor': saldo['pessoa1'],
                        'credor': saldo['pessoa2'],
                        'valor': abs(saldo['saldo'])
                    })

        # Calcula maior pendência
        maior_pendencia = max([pessoa['valor_pendente'] for pessoa in dados_rateio]) if dados_rateio else 0

        return render_template('rateio.html',
                               dados_rateio=dados_rateio,
                               total_geral=total_geral,
                               total_quitado=total_quitado,
                               total_pendente=total_pendente,
                               total_transacoes=total_transacoes,
                               saldos_entre_pessoas=saldos_entre_pessoas,
                               dividas_pendentes=dividas_pendentes,
                               maior_pendencia=maior_pendencia,
                               data_inicio=data_inicio,
                               data_fim=data_fim)

    except Exception as e:
        return f"Erro ao carregar rateio: {str(e)}", 500


@app.route('/mapear_colunas')
def mapear_colunas():
    """
    Exibe tela de mapeamento de colunas
    """
    try:
        if 'temp_file_id' not in session:
            return redirect('/')

        # Recupera o arquivo temporário
        temp_id = session.get('temp_file_id')
        file_name = session.get('temp_file_name', 'arquivo.csv')
        temp_file_path = os.path.join('temp', f"{temp_id}.csv")

        if not os.path.exists(temp_file_path):
            return "Erro: Arquivo temporário não encontrado", 500

        # Importa o serviço de importação
        from services.importador import ImportadorTransacoes
        importador = ImportadorTransacoes()

        with open(temp_file_path, 'rb') as temp_file:
            colunas_encontradas, colunas_validas, colunas_obrigatorias = importador.verificar_colunas(
                temp_file)

        return render_template('mapear_colunas.html',
                               colunas_encontradas=colunas_encontradas,
                               colunas_obrigatorias=colunas_obrigatorias,
                               file_name=file_name)

    except Exception as e:
        return f"Erro ao carregar mapeamento: {str(e)}", 500


@app.route('/processar_mapeamento', methods=['POST'])
def processar_mapeamento():
    """
    Processa o arquivo CSV com mapeamento de colunas
    """
    try:
        if 'temp_file_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Arquivo não encontrado na sessão'
            })

        # Recupera dados do formulário
        mapeamento = {}
        for key, value in request.form.items():
            if key.startswith('coluna_'):
                coluna_obrigatoria = key.replace('coluna_', '')
                mapeamento[
                    coluna_obrigatoria] = value if value else "DEIXAR_EM_BRANCO"

        # Valida se todas as colunas obrigatórias foram mapeadas
        colunas_obrigatorias = [
            'Data de compra', 'Nome no cartão', 'Final do Cartão', 'Categoria',
            'Descrição', 'Parcela', 'Valor (em R$)', 'Valor Recebido (em R$)'
        ]

        for coluna in colunas_obrigatorias:
            if coluna not in mapeamento:
                return jsonify({
                    'success':
                    False,
                    'message':
                    f'Coluna obrigatória "{coluna}" não foi mapeada'
                })

        # Recupera o arquivo temporário
        temp_id = session.get('temp_file_id')
        temp_file_path = os.path.join('temp', f"{temp_id}.csv")

        if not os.path.exists(temp_file_path):
            return jsonify({
                'success': False,
                'message': 'Arquivo temporário não encontrado'
            })

        # Importa e processa com mapeamento
        from services.importador import ImportadorTransacoes
        importador = ImportadorTransacoes()

        fonte = session.get('temp_fonte', 'Não informado')

        with open(temp_file_path, 'rb') as temp_file:
            transacoes = importador.processar_arquivo_com_mapeamento(
                temp_file, mapeamento, fonte)
            importador.salvar_transacoes(transacoes)

        # Limpa arquivos temporários e sessão
        try:
            os.remove(temp_file_path)
        except:
            pass  # Ignora erro se arquivo já foi removido

        session.pop('temp_file_id', None)
        session.pop('temp_file_name', None)
        session.pop('temp_fonte', None)

        # Prepara mensagem de sucesso
        if importador.novas_transacoes > 0:
            message = f'Importação concluída! {importador.novas_transacoes} novas transações adicionadas.'
            if importador.pendentes_adicionadas > 0:
                message += f' {importador.pendentes_adicionadas} transações enviadas para revisão.'
        else:
            message = 'Arquivo processado, mas nenhuma transação nova foi encontrada.'

        # Direciona para a tela de pendentes após processamento
        return jsonify({
            'success': True,
            'message': message,
            'redirect_url': '/pendentes'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar mapeamento: {str(e)}'
        })


@app.route('/salvar_revisao', methods=['POST'])
def salvar_revisao():
    """
    Salva uma revisão de transação e remove ela dos pendentes
    """
    try:
        from services.database import RevisaoService, PendenteService
        from datetime import datetime

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('hash'):
            return jsonify({'success': False, 'message': 'Dados inválidos'})

        # Validar percentuais
        total_percentual = sum(dados.get('donos', {}).values())
        if total_percentual != 100:
            return jsonify({
                'success': False,
                'message': 'O total dos percentuais deve ser 100%'
            })

        # Criar estrutura de quitação individual para cada pessoa
        quitacao_individual = {}
        pago_por = dados.get('pago_por', '')

        for pessoa in dados['donos'].keys():
            # Se a pessoa que deve é a mesma que pagou, marca como quitado automaticamente
            if pessoa == pago_por:
                quitacao_individual[pessoa] = True
            else:
                quitacao_individual[pessoa] = False

        # Inicializa serviços
        revisao_service = RevisaoService()
        pendente_service = PendenteService()

        # Adiciona nova revisão no banco
        revisao_service.adicionar_revisao(
            hash_transacao=dados['hash'],
            id_original=dados['id'],
            nova_descricao=dados['nova_descricao'],
            donos=dados['donos'],
            comentarios=dados['comentarios'],
            pago_por=dados.get('pago_por', ''),
            quitado=False,  # Por padrão, todas as contas começam não quitadas
            quitacao_individual=quitacao_individual,
            data_revisao=datetime.now(),
            revisado_por='Usuario'  # Pode ser expandido para incluir autenticação
        )

        # Remove transação dos pendentes (soft delete)
        pendente_service.excluir_pendente(dados['hash'])

        return jsonify({
            'success': True,
            'message': 'Revisão salva com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar revisão: {str(e)}'
        })


@app.route('/excluir_pendente', methods=['POST'])
def excluir_pendente():
    """
    Remove uma transação da lista de pendentes
    """
    try:
        from services.database import PendenteService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('hash'):
            return jsonify({
                'success': False,
                'message': 'Hash da transação é obrigatório'
            })

        hash_transacao = dados['hash']
        pendente_service = PendenteService()

        # Verifica se a transação existe
        if not pendente_service.pendente_existe(hash_transacao):
            return jsonify({
                'success': False,
                'message': 'Transação não encontrada na lista de pendentes'
            })

        # Remove a transação (soft delete)
        pendente_service.excluir_pendente(hash_transacao)

        return jsonify({
            'success': True,
            'message': 'Transação removida da lista de pendentes!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir pendente: {str(e)}'
        })

        # Salva a lista atualizada
        with open('data/pendentes.json', 'w', encoding='utf-8') as f:
            json.dump(pendentes_filtrados, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': 'Transação removida com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir transação: {str(e)}'
        })


@app.route('/nova_despesa')
def nova_despesa():
    """
    Exibe formulário para adicionar nova despesa manualmente
    """
    try:
        from services.database import PessoaService

        pessoa_service = PessoaService()
        pessoas_existentes = pessoa_service.listar_pessoas()

        # Se não há pessoas no banco, faz migração inicial
        if not pessoas_existentes:
            if pessoa_service.migrar_pessoas_json():
                pessoas_existentes = pessoa_service.listar_pessoas()

        return render_template('nova_despesa.html',
                               pessoas_existentes=pessoas_existentes)

    except Exception as e:
        return f"Erro ao carregar formulário: {str(e)}", 500


@app.route('/salvar_nova_despesa', methods=['POST'])
def salvar_nova_despesa():
    """
    Salva nova despesa manual diretamente nas revisões
    """
    try:
        from datetime import datetime
        from utils.hash import gerar_hash_transacao
        from services.database import TransacaoService, RevisaoService

        dados = request.get_json()

        # Validações básicas
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Dados não recebidos'
            })

        # Campos obrigatórios
        campos_obrigatorios = ['data', 'descricao', 'valor', 'donos']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({
                    'success': False,
                    'message': f'Campo {campo} é obrigatório'
                                })

        # Validar percentuais
        total_percentual = sum(dados.get('donos', {}).values())
        if total_percentual != 100:
            return jsonify({
                'success': False,
                'message': 'O total dos percentuais deve ser 100%'
            })

        # Converter valor para float
        try:
            valor = float(dados['valor'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Valor deve ser um número válido'
            })

        # Gerar hash único para a transação
        hash_transacao = gerar_hash_transacao(dados['data'],
                                              dados['descricao'], valor,
                                              'manual')

        # Inicializa serviços
        transacao_service = TransacaoService()
        revisao_service = RevisaoService()

        # Adicionar transação no banco
        timestamp = int(datetime.now().timestamp())
        transacao_id = f"manual_{timestamp}"
        
        transacao_service.adicionar_transacao(
            transacao_id=transacao_id,
            tipo='manual',
            data=dados['data'],
            descricao=dados['descricao'],
            valor=valor,
            tipo_movimento='entrada' if valor < 0 else 'saida',
            fonte='Manual',
            hash_transacao=hash_transacao,
            observacoes=dados.get('observacoes', '')
        )

        # Criar estrutura de quitação individual para cada pessoa
        quitacao_individual = {}
        pago_por = dados.get('pago_por', '')

        for pessoa in dados['donos'].keys():
            # Se a pessoa que deve é a mesma que pagou, marca como quitado automaticamente
            if pessoa == pago_por:
                quitacao_individual[pessoa] = True
            else:
                quitacao_individual[pessoa] = False

        # Adicionar revisão no banco
        revisao_service.adicionar_revisao(
            hash_transacao=hash_transacao,
            id_original=transacao_id,
            nova_descricao=dados['descricao'],
            donos=dados['donos'],
            comentarios=dados.get('comentarios', ''),
            pago_por=pago_por,
            quitado=False,  # Por padrão, todas as contas começam não quitadas
            quitacao_individual=quitacao_individual,
            data_revisao=datetime.now(),
            revisado_por='Manual'
        )

        return jsonify({
            'success': True,
            'message': 'Despesa manual adicionada com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar despesa: {str(e)}'
        })


@app.route('/listagens')
def listagens():
    """
    Exibe listagem de transações revisadas com filtros
    """
    try:
        import json
        from collections import defaultdict
        from datetime import datetime

        # Obtém filtros da query string
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        responsavel = request.args.get('responsavel', '')
        status_filtro = request.args.get('status', '')
        pago_por_filtro = request.args.get('pago_por', '')

        # Carrega revisões do banco
        from services.database import RevisaoService, TransacaoService
        revisao_service = RevisaoService()
        transacao_service = TransacaoService()

        revisoes = revisao_service.listar_revisoes()
        transacoes = transacao_service.listar_transacoes()

        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}

        # Lista para armazenar dados processados
        listagem_dados = []

        # Obtém lista de pessoas únicas para os filtros
        pessoas_uniques = set()
        responsaveis_unicos = set()

        # Processa cada revisão
        for revisao in revisoes:
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue

            # Aplica filtro de data
            data_str = transacao['data']
            if data_inicio and data_str < data_inicio:
                continue
            if data_fim and data_str > data_fim:
                continue

            # Aplica filtro de pago_por
            pago_por_revisao = revisao.get('pago_por', '')
            if pago_por_filtro and pago_por_revisao != pago_por_filtro:
                continue

            # Adiciona à lista de pessoas únicas
            if pago_por_revisao:
                pessoas_uniques.add(pago_por_revisao)

            # Valor total da transação (converte Decimal para float)
            valor_total = float(abs(transacao['valor']))
            if transacao.get('tipo_movimento') == 'entrada':
                valor_total = -valor_total

            # Distribui por responsável
            donos = revisao.get('donos', {})
            for pessoa, percentual in donos.items():
                # Adiciona à lista de responsáveis únicos
                responsaveis_unicos.add(pessoa)

                # Aplica filtro de responsável se especificado
                if responsavel and pessoa != responsavel:
                    continue

                # Verifica status individual de quitação
                quitacao_individual = revisao.get('quitacao_individual', {})
                status_individual = quitacao_individual.get(pessoa, False)

                # Aplica filtro de status
                if status_filtro == 'pendente' and status_individual:
                    continue
                if status_filtro == 'quitado' and not status_individual:
                    continue

                valor_rateado = valor_total * (percentual / 100)

                item = {
                    'data':
                    data_str,
                    'descricao':
                    revisao.get('nova_descricao', transacao['descricao']),
                    'valor':
                    transacao['valor'],
                    'fonte':
                    transacao.get('fonte', ''),
                    'observacoes':
                    transacao.get('observacoes', ''),
                    'valor_total':
                    valor_total,
                    'percentual_rateio':
                    percentual,
                    'valor_rateado':
                    valor_rateado,
                    'responsavel':
                    pessoa,
                    'tipo_movimento':
                    transacao.get('tipo_movimento', 'saida'),
                    'pago_por':
                    pago_por_revisao,
                    'quitado':
                    status_individual
                }

                listagem_dados.append(item)

        # Ordena por data (mais recente primeiro) e depois por responsável
        listagem_dados.sort(key=lambda x: (x['data'], x['responsavel']),
                            reverse=True)

        # Converte sets para listas ordenadas
        pessoas_uniques = sorted(list(pessoas_uniques))
        responsaveis_unicos = sorted(list(responsaveis_unicos))

        return render_template('listagens.html',
                               listagem_dados=listagem_dados,
                               pessoas_uniques=pessoas_uniques,
                               responsaveis_unicos=responsaveis_unicos,
                               data_inicio=data_inicio,
                               data_fim=data_fim,
                               responsavel=responsavel)

    except Exception as e:
        return f"Erro ao carregar listagens: {str(e)}", 500


@app.route('/exportar_listagem_csv')
def exportar_listagem_csv():
    """
    Exporta dados da listagem em formato CSV
    """
    try:
        import json
        import csv
        from collections import defaultdict
        from datetime import datetime
        from flask import Response
        import io

        # Obtém filtros da query string
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        responsavel = request.args.get('responsavel', '')
        status_filtro = request.args.get('status', '')
        pago_por_filtro = request.args.get('pago_por', '')

        # Carrega revisões do banco
        from services.database import RevisaoService, TransacaoService
        revisao_service = RevisaoService()
        transacao_service = TransacaoService()

        revisoes = revisao_service.listar_revisoes()
        transacoes = transacao_service.listar_transacoes()

        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}

        # Lista para armazenar dados para CSV
        dados_csv = []

        for revisao in revisoes:
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue

            # Aplica filtros de data
            data_str = transacao['data']
            if data_inicio and data_str < data_inicio:
                continue
            if data_fim and data_str > data_fim:
                continue

            # Aplica filtro de pago_por
            pago_por_revisao = revisao.get('pago_por', '')
            if pago_por_filtro and pago_por_revisao != pago_por_filtro:
                continue

            valor_total = float(abs(transacao['valor']))
            if transacao.get('tipo_movimento') == 'entrada':
                valor_total = -valor_total

            donos = revisao.get('donos', {})

            for pessoa, percentual in donos.items():
                # Aplica filtro de responsável se especificado
                if responsavel and pessoa != responsavel:
                    continue

                # Verifica status individual
                quitacao_individual = revisao.get('quitacao_individual', {})
                status_individual = quitacao_individual.get(pessoa, False)

                # Aplica filtro de status
                if status_filtro == 'pendente' and status_individual:
                    continue
                if status_filtro == 'quitado' and not status_individual:
                    continue

                valor_rateado = valor_total * (float(percentual) / 100)

                dados_csv.append({
                    'Data':
                    data_str,
                    'Descrição':
                    revisao.get('nova_descricao', transacao['descricao']),
                    'Valor':
                    f"R$ {float(transacao['valor']):.2f}",
                    'Fonte':
                    transacao.get('fonte', ''),
                    'Observações':
                    transacao.get('observacoes', ''),
                    'Valor Total':
                    f"R$ {valor_total:.2f}",
                    '% Rateio':
                    f"{float(percentual):.1f}%",
                    'Valor Rateado':
                    f"R$ {valor_rateado:.2f}",
                    'Responsável':
                    pessoa,
                    'Pago Por':
                    pago_por_revisao,
                    'Status Individual':
                    'Quitado' if status_individual else 'Pendente'
                })

        # Ordena por data
        dados_csv.sort(key=lambda x: x['Data'], reverse=True)

        # Cria arquivo CSV em memória
        output = io.StringIO()
        if dados_csv:
            fieldnames = [
                'Data', 'Descrição', 'Valor', 'Fonte', 'Observações',
                'Valor Total', '% Rateio', 'Valor Rateado', 'Responsável',
                'Pago Por', 'Status Individual'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dados_csv)

        # Prepara resposta
        csv_data = output.getvalue()
        output.close()

        # Define nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"listagem_{timestamp}"
        if responsavel:
            nome_arquivo += f"_{responsavel.replace(' ', '_')}"
        if status_filtro:
            nome_arquivo += f"_{status_filtro}"
        if pago_por_filtro:
            nome_arquivo += f"_{pago_por_filtro.replace(' ', '_')}"
        nome_arquivo += ".csv"

        # Retorna CSV como download
        return Response(csv_data,
                        mimetype='text/csv',
                        headers={
                            'Content-Disposition':
                            f'attachment; filename={nome_arquivo}'
                        })

    except Exception as e:
        return f"Erro ao exportar CSV: {str(e)}", 500


@app.route('/exportar_rateio_csv')
def exportar_rateio_csv():
    """
    Exporta dados do rateio em formato CSV
    """
    try:
        import json
        import csv
        from collections import defaultdict
        from datetime import datetime
        from flask import Response
        import io

        # Obtém filtros da query string
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        pessoa_filtro = request.args.get('pessoa', '')

        # Carrega revisões
        try:
            with open('data/revisoes.json', 'r', encoding='utf-8') as f:
                revisoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            revisoes = []

        # Carrega transações
        try:
            with open('data/transacoes.json', 'r', encoding='utf-8') as f:
                transacoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            transacoes = []

        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}

        # Lista para armazenar dados para CSV
        dados_csv = []

        for revisao in revisoes:
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue

            # Aplica filtros de data
            data_str = transacao['data']
            if data_inicio and data_str < data_inicio:
                continue
            if data_fim and data_str > data_fim:
                continue

            valor = abs(transacao['valor'])
            donos = revisao.get('donos', {})

            for pessoa, percentual in donos.items():
                # Aplica filtro de pessoa se especificado
                if pessoa_filtro and pessoa != pessoa_filtro:
                    continue

                valor_pessoa = valor * (percentual / 100)

                dados_csv.append({
                    'Data':
                    data_str,
                    'Descrição':
                    transacao['descricao'],
                    'Valor Total':
                    f"R$ {valor:.2f}",
                    'Pessoa':
                    pessoa,
                    'Percentual':
                    f"{percentual}%",
                    'Valor Atribuído':
                    f"R$ {valor_pessoa:.2f}",
                    'Fonte':
                    transacao.get('fonte', ''),
                    'Observações':
                    transacao.get('observacoes', '')
                })

        # Ordena por data
        dados_csv.sort(key=lambda x: x['Data'])

        # Cria arquivo CSV em memória
        output = io.StringIO()
        if dados_csv:
            fieldnames = [
                'Data', 'Descrição', 'Valor Total', 'Pessoa', 'Percentual',
                'Valor Atribuído', 'Fonte', 'Observações'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dados_csv)

        # Prepara resposta
        csv_data = output.getvalue()
        output.close()

        # Define nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"rateio_{timestamp}"
        if pessoa_filtro:
            nome_arquivo += f"_{pessoa_filtro.replace(' ', '_')}"
        nome_arquivo += ".csv"

        # Retorna CSV como download
        return Response(csv_data,
                        mimetype='text/csv',
                        headers={
                            'Content-Disposition':
                            f'attachment; filename={nome_arquivo}'
                        })

    except Exception as e:
        return f"Erro ao exportar CSV: {str(e)}", 500


@app.route('/pagamentos')
def pagamentos():
    """
    Exibe controle de pagamentos
    """
    try:
        import json
        from collections import defaultdict
        from datetime import datetime

        # Obtém filtros da query string
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        status = request.args.get('status', '')
        pago_por = request.args.get('pago_por', '')

        # Carrega revisões e transações do banco
        from services.database import RevisaoService, TransacaoService
        revisao_service = RevisaoService()
        transacao_service = TransacaoService()

        revisoes = revisao_service.listar_revisoes()
        transacoes = transacao_service.listar_transacoes()

        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}

        # Lista para armazenar dados de pagamentos
        pagamentos_dados = []
        pessoas_uniques = set()
        total_pendentes = 0
        total_valor_pendente = 0

        # Obtém filtro de responsável
        responsavel_filtro = request.args.get('responsavel', '')

        # Obtém lista de todas as pessoas para o filtro
        todas_pessoas = set()
        for revisao in revisoes:
            donos = revisao.get('donos', {})
            todas_pessoas.update(donos.keys())

        # Processa cada revisão
        for revisao in revisoes:
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue

            # Aplica filtro de data
            data_str = transacao['data']
            if data_inicio and data_str < data_inicio:
                continue
            if data_fim and data_str > data_fim:
                continue

            # Valor total da transação (converte Decimal para float)
            valor_total = float(abs(transacao['valor']))
            if transacao.get('tipo_movimento') == 'entrada':
                valor_total = -valor_total

            # Obtém dados de pagamento
            pago_por_revisao = revisao.get('pago_por', '')

            # Aplica filtro de pago_por
            if pago_por and pago_por_revisao != pago_por:
                continue

            # Adiciona pessoas à lista
            pessoas_uniques.add(pago_por_revisao)

            # Distribui por responsável
            donos = revisao.get('donos', {})
            quitacao_individual = revisao.get('quitacao_individual', {})

            for pessoa, percentual in donos.items():
                # Aplica filtro de responsável
                if responsavel_filtro and pessoa != responsavel_filtro:
                    continue

                valor_rateado = valor_total * (percentual / 100)

                # Verifica se esta pessoa específica quitou
                pessoa_quitou = quitacao_individual.get(pessoa, False)

                # Aplica filtro de status baseado na quitação individual
                if status == 'pendente' and pessoa_quitou:
                    continue
                if status == 'quitado' and not pessoa_quitou:
                    continue

                item = {
                    'hash':
                    revisao['hash'],
                    'data':
                    data_str,
                    'descricao':
                    revisao.get('nova_descricao', transacao['descricao']),
                    'valor_rateado':
                    valor_rateado,
                    'responsavel':
                    pessoa,
                    'pago_por':
                    pago_por_revisao,
                    'quitado':
                    pessoa_quitou,
                    'tipo_movimento':
                    transacao.get('tipo_movimento', 'saida')
                }

                pagamentos_dados.append(item)

                # Conta pendentes baseado na quitação individual
                if not pessoa_quitou:
                    total_pendentes += 1
                    total_valor_pendente += abs(valor_rateado)

        # Ordena por data
        pagamentos_dados.sort(key=lambda x: x['data'], reverse=True)

        # Remove strings vazias do set de pessoas
        pessoas_uniques.discard('')
        pessoas_uniques = sorted(list(pessoas_uniques))

        # Calcula saldos entre pessoas
        saldos_entre_pessoas = calcular_saldos_entre_pessoas(
            revisoes, transacoes_map)

        # Lista de responsáveis únicos para o filtro
        responsaveis_unicos = sorted(list(todas_pessoas))

        return render_template('pagamentos.html',
                               pagamentos_dados=pagamentos_dados,
                               pessoas_uniques=pessoas_uniques,
                               responsaveis_unicos=responsaveis_unicos,
                               total_pendentes=total_pendentes,
                               total_valor_pendente=total_valor_pendente,
                               saldos_entre_pessoas=saldos_entre_pessoas,
                               data_inicio=data_inicio,
                               data_fim=data_fim,
                               status=status,
                               pago_por=pago_por,
                               responsavel=responsavel_filtro)

    except Exception as e:
        return f"Erro ao carregar pagamentos: {str(e)}", 500


def calcular_saldos_entre_pessoas(revisoes, transacoes_map):
    """
    Calcula saldos entre pessoas baseado em quem pagou e quem deve
    """
    from collections import defaultdict
    from itertools import combinations

    # Dicionário para armazenar saldos: {(pessoa1, pessoa2): saldo}
    saldos_brutos = defaultdict(float)
    pessoas = set()

    for revisao in revisoes:
        transacao = transacoes_map.get(revisao['hash'])
        if not transacao:
            continue

        pago_por = revisao.get('pago_por', '')
        if not pago_por:
            continue

        # Valor total da transação (converte Decimal para float)
        valor_total = float(abs(float(transacao['valor'])))
        if transacao.get('tipo_movimento') == 'entrada':
            valor_total = -valor_total

        donos = revisao.get('donos', {})
        quitacao_individual = revisao.get('quitacao_individual', {})

        # Para cada pessoa responsável, calcula quanto deve para quem pagou
        for pessoa, percentual in donos.items():
            if pessoa == pago_por:
                continue  # Pessoa não deve para si mesma

            # Pula se esta pessoa já quitou individualmente
            if quitacao_individual.get(pessoa, False):
                continue

            valor_devido = valor_total * (percentual / 100)

            # Cria chave ordenada para o par de pessoas
            chave = tuple(sorted([pessoa, pago_por]))

            # Se pessoa < pago_por na ordem, valor é negativo (pessoa deve)
            # Se pessoa > pago_por na ordem, valor é positivo (pago_por deve)
            if pessoa < pago_por:
                saldos_brutos[chave] -= valor_devido
            else:
                saldos_brutos[chave] += valor_devido

            pessoas.add(pessoa)
            pessoas.add(pago_por)

    # Converte para lista de objetos para exibição
    saldos_entre_pessoas = []
    for (pessoa1, pessoa2), saldo in saldos_brutos.items():
        if abs(saldo) > 0.01:  # Ignora valores muito pequenos
            saldos_entre_pessoas.append({
                'pessoa1': pessoa1,
                'pessoa2': pessoa2,
                'saldo': saldo
            })

    # Ordena por valor absoluto do saldo (maiores dívidas primeiro)
    saldos_entre_pessoas.sort(key=lambda x: abs(x['saldo']), reverse=True)

    return saldos_entre_pessoas


@app.route('/atualizar_status_pagamento', methods=['POST'])
def atualizar_status_pagamento():
    """
    Atualiza status de quitação individual de um pagamento específico
    """
    from services.database import RevisaoService

    try:
        data = request.get_json()

        # Validações básicas
        if not data or not data.get('hash') or not data.get('responsavel'):
            return jsonify({
                'success': False,
                'message': 'Dados obrigatórios não informados'
            })

        hash_transacao = data['hash']
        responsavel = data['responsavel']
        quitado = data.get('quitado', False)

        # Inicializa serviço
        revisao_service = RevisaoService()

        # Busca a revisão
        revisao = revisao_service.buscar_revisao_por_hash(hash_transacao)

        if not revisao:
            return jsonify({
                'success': False,
                'message': 'Revisão não encontrada'
            })

        # Verifica se o responsável existe na lista de donos
        if responsavel not in revisao.get('donos', {}):
            return jsonify({
                'success':
                False,
                'message':
                'Responsável não encontrado nesta despesa'
            })

        # Inicializa quitacao_individual se não existir
        if 'quitacao_individual' not in revisao:
            revisao['quitacao_individual'] = {}
            for pessoa in revisao.get('donos', {}).keys():
                revisao['quitacao_individual'][pessoa] = False

        # Atualiza status de quitação individual
        revisao['quitacao_individual'][responsavel] = quitado

        # Atualiza o campo quitado geral (True apenas se todos quitaram)
        todas_quitadas = all(
            revisao['quitacao_individual'].values())
        revisao['quitado'] = todas_quitadas

        # Atualiza no banco
        revisao_service.atualizar_revisao(
            hash_transacao,
            quitacao_individual=revisao['quitacao_individual'],
            quitado=todas_quitadas
        )

        status_texto = 'quitado' if quitado else 'pendente'
        message = f'Pagamento de {responsavel} marcado como {status_texto} com sucesso!'

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        })


@app.route('/quitar_em_lote', methods=['POST'])
def quitar_em_lote():
    """
    Quita múltiplos pagamentos em lote
    """
    try:
        from services.database import RevisaoService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('itens'):
            return jsonify({
                'success': False,
                'message': 'Lista de itens é obrigatória'
            })

        itens = dados['itens']
        quitado = dados.get('quitado', True)

        revisao_service = RevisaoService()

        itens_processados = 0
        erros = []

        # Processa cada item da lista
        for item in itens:
            hash_transacao = item.get('hash')
            responsavel = item.get('responsavel')

            if not hash_transacao or not responsavel:
                erros.append(
                    f'Item inválido: hash={hash_transacao}, responsavel={responsavel}'
                )
                continue

            # Busca a revisão correspondente
            revisao_encontrada = revisao_service.buscar_revisao_por_hash(hash_transacao)

            if not revisao_encontrada:
                erros.append(
                    f'Revisão não encontrada para hash: {hash_transacao}')
                continue

            # Verifica se o responsável existe na lista de donos
            if responsavel not in revisao_encontrada.get('donos', {}):
                erros.append(
                    f'Responsável {responsavel} não encontrado na despesa {hash_transacao}'
                )
                continue

            # Inicializa quitacao_individual se não existir
            if 'quitacao_individual' not in revisao_encontrada:
                revisao_encontrada['quitacao_individual'] = {}
                for pessoa in revisao_encontrada.get('donos', {}).keys():
                    revisao_encontrada['quitacao_individual'][pessoa] = False

            # Atualiza status de quitação individual
            revisao_encontrada['quitacao_individual'][responsavel] = quitado

            # Atualiza o campo quitado geral (True apenas se todos quitaram)
            todas_quitadas = all(
                revisao_encontrada['quitacao_individual'].values())
            revisao_encontrada['quitado'] = todas_quitadas

            # Atualiza no banco
            revisao_service.atualizar_revisao(
                hash_transacao,
                quitacao_individual=revisao_encontrada['quitacao_individual'],
                quitado=todas_quitadas
            )

            itens_processados += 1

        status_texto = 'quitados' if quitado else 'marcados como pendentes'
        message = f'{itens_processados} pagamentos {status_texto} com sucesso!'

        if erros:
            message += f' {len(erros)} erros encontrados.'

        return jsonify({
            'success': True,
            'message': message,
            'itens_processados': itens_processados,
            'erros': erros
        })

    except Exception as e:
        return jsonify({
            'success':
            False,
            'message':
            f'Erro ao processar quitação em lote: {str(e)}'
        })


@app.route('/pessoas')
def pessoas():
    """
    Exibe tela de gerenciamento de pessoas
    """
    try:
        from services.database import PessoaService

        pessoa_service = PessoaService()
        pessoas = pessoa_service.listar_pessoas()

        # Se não há pessoas no banco, faz migração inicial
        if not pessoas:
            if pessoa_service.migrar_pessoas_json():
                pessoas = pessoa_service.listar_pessoas()

        return render_template('pessoas.html', pessoas=pessoas)

    except Exception as e:
        return f"Erro ao carregar pessoas: {str(e)}", 500


@app.route('/salvar_pessoa', methods=['POST'])
def salvar_pessoa():
    """
    Adiciona uma nova pessoa
    """
    try:
        from services.database import PessoaService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome da pessoa é obrigatório'
            })

        nome_pessoa = dados['nome'].strip()

        if not nome_pessoa:
            return jsonify({
                'success': False,
                'message': 'Nome da pessoa não pode estar vazio'
            })

        pessoa_service = PessoaService()

        # Verifica se a pessoa já existe
        if pessoa_service.pessoa_existe(nome_pessoa):
            return jsonify({
                'success': False,
                'message': 'Esta pessoa já existe'
            })

        # Adiciona nova pessoa
        pessoa_service.adicionar_pessoa(nome_pessoa)

        return jsonify({
            'success': True,
            'message': 'Pessoa adicionada com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar pessoa: {str(e)}'
        })


@app.route('/editar_pessoa', methods=['POST'])
def editar_pessoa():
    """
    Edita uma pessoa existente
    """
    try:
        from services.database import PessoaService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('nome_antigo') or not dados.get('nome_novo'):
            return jsonify({
                'success': False,
                'message': 'Nome antigo e novo são obrigatórios'
            })

        nome_antigo = dados['nome_antigo'].strip()
        nome_novo = dados['nome_novo'].strip()

        if not nome_novo:
            return jsonify({
                'success': False,
                'message': 'Nome da pessoa não pode estar vazio'
            })

        pessoa_service = PessoaService()

        # Verifica se a pessoa antiga existe
        if not pessoa_service.pessoa_existe(nome_antigo):
            return jsonify({
                'success': False,
                'message': 'Pessoa não encontrada'
            })

        # Verifica se o novo nome já existe (exceto se for o mesmo)
        if nome_novo != nome_antigo and pessoa_service.pessoa_existe(nome_novo):
            return jsonify({
                'success': False,
                'message': 'Já existe uma pessoa com este nome'
            })

        # Atualiza a pessoa
        pessoa_service.editar_pessoa(nome_antigo, nome_novo)

        return jsonify({
            'success': True,
            'message': 'Pessoa editada com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao editar pessoa: {str(e)}'
        })


@app.route('/excluir_pessoa', methods=['POST'])
def excluir_pessoa():
    """
    Exclui uma pessoa
    """
    try:
        from services.database import PessoaService

        dados = request.get_json()

        # Validações básicas
        if not dados or not dados.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome da pessoa é obrigatório'
            })

        nome_pessoa = dados['nome'].strip()
        pessoa_service = PessoaService()

        # Verifica se a pessoa existe
        if not pessoa_service.pessoa_existe(nome_pessoa):
            return jsonify({
                'success': False,
                'message': 'Pessoa não encontrada'
            })

        # Remove a pessoa (soft delete)
        pessoa_service.excluir_pessoa(nome_pessoa)

        return jsonify({
            'success': True,
            'message': 'Pessoa excluída com sucesso!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir pessoa: {str(e)}'
        })


@app.route('/limpar_base')
def limpar_base():
    """
    Exibe tela para limpar base de dados
    """
    return render_template('limpar_base.html')


@app.route('/obter_totais_tabelas')
def obter_totais_tabelas():
    """
    Obtém totais das tabelas para exibir antes da limpeza
    """
    try:
        from services.database import DatabaseService

        db_service = DatabaseService()

        # Consultas para obter totais
        total_pendentes = db_service.execute_query(
            "SELECT COUNT(*) as total FROM pendentes WHERE ativo = TRUE", 
            fetch=True
        )[0]['total']

        total_revisoes = db_service.execute_query(
            "SELECT COUNT(*) as total FROM revisoes WHERE ativo = TRUE", 
            fetch=True
        )[0]['total']

        total_transacoes = db_service.execute_query(
            "SELECT COUNT(*) as total FROM transacoes WHERE ativo = TRUE", 
            fetch=True
        )[0]['total']

        return jsonify({
            'success': True,
            'totais': {
                'pendentes': total_pendentes,
                'revisoes': total_revisoes,
                'transacoes': total_transacoes
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter totais: {str(e)}'
        })


@app.route('/limpar_base_dados', methods=['POST'])
def limpar_base_dados():
    """
    Limpa as tabelas de dados (pendentes, revisões e transações)
    """
    try:
        from services.database import DatabaseService

        dados = request.get_json()

        # Validação do PIN
        pin_correto = "1234"
        pin_informado = dados.get('pin', '').strip()

        if not pin_informado:
            return jsonify({
                'success': False,
                'message': 'PIN é obrigatório'
            })

        if pin_informado != pin_correto:
            return jsonify({
                'success': False,
                'message': 'PIN incorreto. Tente novamente.'
            })

        db_service = DatabaseService()

        # Executa limpeza das tabelas
        queries_limpeza = [
            "UPDATE pendentes SET ativo = FALSE",
            "UPDATE revisoes SET ativo = FALSE", 
            "UPDATE transacoes SET ativo = FALSE"
        ]

        for query in queries_limpeza:
            db_service.execute_query(query)

        return jsonify({
            'success': True,
            'message': 'Base de dados limpa com sucesso! Todas as transações, pendentes e revisões foram removidas.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao limpar base de dados: {str(e)}'
        })


if __name__ == '__main__':
    cleanup_temp_files()
    app.run(host='0.0.0.0', port=5000, debug=True)