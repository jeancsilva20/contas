
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process_upload', methods=['POST'])
def process_upload():
    # Mock processing - apenas simula o processamento
    password = request.form.get('password')
    file = request.files.get('file')
    
    if not password:
        return jsonify({'success': False, 'message': 'Senha é obrigatória'})
    
    if not file:
        return jsonify({'success': False, 'message': 'Arquivo é obrigatório'})
    
    # Simula processamento bem-sucedido
    return jsonify({'success': True, 'message': 'Importação iniciada com sucesso!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
