
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
        
        # Processa o arquivo
        importador = ImportadorTransacoes()
        transacoes = importador.processar_arquivo(file)
        
        # Salva as transações
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
