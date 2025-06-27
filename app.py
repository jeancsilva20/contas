
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/pendentes')
def pendentes():
    """
    Exibe lançamentos pendentes de revisão
    """
    try:
        import json
        
        # Carrega pendentes
        try:
            with open('data/pendentes.json', 'r', encoding='utf-8') as f:
                pendentes_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pendentes_data = []
        
        # Ordena por data (mais recentes primeiro)
        pendentes_data.sort(key=lambda x: x.get('data', ''), reverse=True)
        
        return render_template('pendentes.html', pendentes=pendentes_data)
        
    except Exception as e:
        return f"Erro ao carregar pendentes: {str(e)}", 500

@app.route('/process_upload', methods=['POST'])
def process_upload():
    try:
        file = request.files.get('file')
        
        # Validações básicas
        if not file:
            return jsonify({'success': False, 'message': 'Arquivo é obrigatório'})
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'message': 'Apenas arquivos CSV são suportados'})
        
        # Importa o serviço de importação
        from services.importador import ImportadorTransacoes
        
        # Verifica as colunas do arquivo
        importador = ImportadorTransacoes()
        
        # Salva o arquivo temporariamente na sessão para uso posterior
        import tempfile
        import base64
        
        file_content = file.read()
        file.seek(0)  # Reset para poder ler novamente
        
        # Codifica o conteúdo do arquivo para a sessão
        from flask import session
        session['temp_file_content'] = base64.b64encode(file_content).decode('utf-8')
        session['temp_file_name'] = file.filename
        
        colunas_encontradas, colunas_validas, colunas_obrigatorias = importador.verificar_colunas(file)
        
        if not colunas_validas:
            # Redireciona para a tela de mapeamento
            return jsonify({
                'success': False, 
                'requires_mapping': True,
                'message': 'Arquivo requer mapeamento de colunas',
                'redirect_url': '/mapear_colunas'
            })
        
        # Se as colunas estão corretas, processa normalmente
        transacoes = importador.processar_arquivo(file)
        importador.salvar_transacoes(transacoes)
        
        # Prepara mensagem de sucesso
        if importador.novas_transacoes > 0:
            message = f'Importação concluída! {importador.novas_transacoes} novas transações adicionadas.'
            if importador.pendentes_adicionadas > 0:
                message += f' {importador.pendentes_adicionadas} transações enviadas para revisão.'
        else:
            message = 'Arquivo processado, mas nenhuma transação nova foi encontrada.'
        
        return jsonify({'success': True, 'message': message})
        
    except ValueError as e:
        # Erros de validação
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        # Outros erros
        return jsonify({'success': False, 'message': f'Erro ao processar arquivo: {str(e)}'})

@app.route('/resumo')
def resumo():
    """
    Exibe painel com resumo dos dados revisados
    """
    try:
        import json
        from collections import defaultdict
        from datetime import datetime
        
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
            
            valor = abs(transacao['valor'])  # Usa valor absoluto para soma
            data_str = transacao['data']
            
            # Total geral
            total_geral += valor
            
            # Por mês
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                mes_ano = data_obj.strftime('%Y-%m')
                por_mes[mes_ano] += valor
            except:
                pass
            
            # Por pessoa (baseado nos donos da revisão)
            donos = revisao.get('donos', {})
            for pessoa, percentual in donos.items():
                valor_pessoa = valor * (percentual / 100)
                por_pessoa[pessoa] += valor_pessoa
            
            # Por categoria (extraída das observações da transação)
            observacoes = transacao.get('observacoes', '')
            categoria = 'Outros'
            if 'Categoria:' in observacoes:
                try:
                    categoria = observacoes.split('Categoria:')[1].split('|')[0].strip()
                except:
                    pass
            por_categoria[categoria] += valor
        
        # Ordena dados para gráficos
        meses_ordenados = sorted(por_mes.keys())
        dados_mensais = [{'mes': mes, 'valor': por_mes[mes]} for mes in meses_ordenados]
        
        dados_categoria = [{'categoria': cat, 'valor': valor} for cat, valor in sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)]
        
        dados_pessoa = [{'pessoa': pessoa, 'valor': valor} for pessoa, valor in sorted(por_pessoa.items(), key=lambda x: x[1], reverse=True)]
        
        return render_template('resumo.html', 
                             total_geral=total_geral,
                             dados_categoria=dados_categoria,
                             dados_mensais=dados_mensais,
                             dados_pessoa=dados_pessoa,
                             total_revisoes=len(revisoes))
        
    except Exception as e:
        return f"Erro ao carregar resumo: {str(e)}", 500

@app.route('/rateio')
def rateio():
    """
    Exibe rateio dos custos entre as pessoas baseado nas revisões
    """
    try:
        import json
        from collections import defaultdict
        
        # Carrega revisões
        try:
            with open('data/revisoes.json', 'r', encoding='utf-8') as f:
                revisoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            revisoes = []
        
        # Carrega transações para obter valores
        try:
            with open('data/transacoes.json', 'r', encoding='utf-8') as f:
                transacoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            transacoes = []
        
        # Cria mapa de transações por hash
        transacoes_map = {t['hash']: t for t in transacoes}
        
        # Calcula valores por pessoa
        rateio_pessoa = defaultdict(float)
        total_geral = 0
        total_transacoes = 0
        
        for revisao in revisoes:
            # Busca dados da transação original
            transacao = transacoes_map.get(revisao['hash'])
            if not transacao:
                continue
            
            valor = abs(transacao['valor'])  # Usa valor absoluto
            total_geral += valor
            total_transacoes += 1
            
            # Distribui valor baseado nos percentuais
            donos = revisao.get('donos', {})
            for pessoa, percentual in donos.items():
                valor_pessoa = valor * (percentual / 100)
                rateio_pessoa[pessoa] += valor_pessoa
        
        # Ordena por valor (maior para menor)
        dados_rateio = [
            {
                'pessoa': pessoa, 
                'valor': valor,
                'percentual_total': (valor / total_geral * 100) if total_geral > 0 else 0
            } 
            for pessoa, valor in sorted(rateio_pessoa.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return render_template('rateio.html', 
                             dados_rateio=dados_rateio,
                             total_geral=total_geral,
                             total_transacoes=total_transacoes)
        
    except Exception as e:
        return f"Erro ao carregar rateio: {str(e)}", 500

@app.route('/mapear_colunas')
def mapear_colunas():
    """
    Exibe tela de mapeamento de colunas
    """
    try:
        from flask import session
        import tempfile
        import base64
        from io import StringIO
        
        if 'temp_file_content' not in session:
            return redirect('/')
        
        # Recupera o arquivo da sessão
        file_content = base64.b64decode(session['temp_file_content'])
        file_name = session.get('temp_file_name', 'arquivo.csv')
        
        # Cria um arquivo temporário em memória
        file_like = StringIO(file_content.decode('utf-8'))
        
        # Importa o serviço de importação
        from services.importador import ImportadorTransacoes
        importador = ImportadorTransacoes()
        
        colunas_encontradas, colunas_validas, colunas_obrigatorias = importador.verificar_colunas(file_like)
        
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
        from flask import session
        import base64
        from io import StringIO
        
        if 'temp_file_content' not in session:
            return jsonify({'success': False, 'message': 'Arquivo não encontrado na sessão'})
        
        # Recupera dados do formulário
        mapeamento = {}
        for key, value in request.form.items():
            if key.startswith('coluna_'):
                coluna_obrigatoria = key.replace('coluna_', '')
                mapeamento[coluna_obrigatoria] = value if value else "DEIXAR_EM_BRANCO"
        
        # Valida se todas as colunas obrigatórias foram mapeadas
        colunas_obrigatorias = [
            'Data de compra', 
            'Nome no cartão', 
            'Final do Cartão', 
            'Categoria', 
            'Descrição', 
            'Parcela', 
            'Valor (em R$)'
        ]
        
        for coluna in colunas_obrigatorias:
            if coluna not in mapeamento:
                return jsonify({'success': False, 'message': f'Coluna obrigatória "{coluna}" não foi mapeada'})
        
        # Recupera o arquivo da sessão
        file_content = base64.b64decode(session['temp_file_content'])
        file_like = StringIO(file_content.decode('utf-8'))
        
        # Importa e processa com mapeamento
        from services.importador import ImportadorTransacoes
        importador = ImportadorTransacoes()
        
        transacoes = importador.processar_arquivo_com_mapeamento(file_like, mapeamento)
        importador.salvar_transacoes(transacoes)
        
        # Limpa a sessão
        session.pop('temp_file_content', None)
        session.pop('temp_file_name', None)
        
        # Prepara mensagem de sucesso
        if importador.novas_transacoes > 0:
            message = f'Importação concluída! {importador.novas_transacoes} novas transações adicionadas.'
            if importador.pendentes_adicionadas > 0:
                message += f' {importador.pendentes_adicionadas} transações enviadas para revisão.'
        else:
            message = 'Arquivo processado, mas nenhuma transação nova foi encontrada.'
        
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao processar mapeamento: {str(e)}'})

@app.route('/salvar_revisao', methods=['POST'])
def salvar_revisao():
    """
    Salva uma revisão de transação e remove ela dos pendentes
    """
    try:
        import json
        from datetime import datetime
        
        dados = request.get_json()
        
        # Validações básicas
        if not dados or not dados.get('hash'):
            return jsonify({'success': False, 'message': 'Dados inválidos'})
        
        # Validar percentuais
        total_percentual = sum(dados.get('donos', {}).values())
        if total_percentual != 100:
            return jsonify({'success': False, 'message': 'O total dos percentuais deve ser 100%'})
        
        # Carrega revisões existentes
        try:
            with open('data/revisoes.json', 'r', encoding='utf-8') as f:
                revisoes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            revisoes = []
        
        # Cria nova revisão
        nova_revisao = {
            'hash': dados['hash'],
            'id_original': dados['id'],
            'nova_descricao': dados['nova_descricao'],
            'donos': dados['donos'],
            'comentarios': dados['comentarios'],
            'data_revisao': datetime.now().isoformat(),
            'revisado_por': 'Usuario'  # Pode ser expandido para incluir autenticação
        }
        
        # Adiciona à lista de revisões
        revisoes.append(nova_revisao)
        
        # Salva revisões atualizadas
        with open('data/revisoes.json', 'w', encoding='utf-8') as f:
            json.dump(revisoes, f, ensure_ascii=False, indent=2)
        
        # Remove transação dos pendentes
        try:
            with open('data/pendentes.json', 'r', encoding='utf-8') as f:
                pendentes = json.load(f)
            
            # Filtra removendo a transação revisada
            pendentes_atualizados = [p for p in pendentes if p.get('hash') != dados['hash']]
            
            # Salva pendentes atualizados
            with open('data/pendentes.json', 'w', encoding='utf-8') as f:
                json.dump(pendentes_atualizados, f, ensure_ascii=False, indent=2)
        
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Se não conseguir carregar pendentes, continua
        
        return jsonify({'success': True, 'message': 'Revisão salva com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao salvar revisão: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
