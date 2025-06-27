
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
