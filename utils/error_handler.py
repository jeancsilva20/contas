
import logging
import traceback
from functools import wraps
from flask import jsonify, request, current_app

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Classe base para erros da aplicação"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

class ValidationError(AppError):
    """Erro de validação de dados"""
    def __init__(self, message, field=None):
        super().__init__(message, 400)
        self.field = field

class FileError(AppError):
    """Erro relacionado a arquivos"""
    def __init__(self, message):
        super().__init__(message, 422)

class DatabaseError(AppError):
    """Erro relacionado a banco de dados/arquivos JSON"""
    def __init__(self, message):
        super().__init__(message, 500)

def handle_errors(f):
    """Decorator para tratamento de erros em rotas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError as e:
            logger.error(f"Erro da aplicação: {e.message}")
            return jsonify({
                'success': False,
                'message': e.message,
                'field': getattr(e, 'field', None)
            }), e.status_code
        except FileNotFoundError as e:
            logger.error(f"Arquivo não encontrado: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Arquivo não encontrado'
            }), 404
        except PermissionError as e:
            logger.error(f"Erro de permissão: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro de permissão ao acessar arquivo'
            }), 403
        except ValueError as e:
            logger.error(f"Erro de valor: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erro de validação: {str(e)}'
            }), 400
        except Exception as e:
            logger.error(f"Erro não tratado: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500
    
    return decorated_function

def log_request_info():
    """Log informações da requisição"""
    logger.info(f"{request.method} {request.url} - IP: {request.remote_addr}")

def validate_required_fields(data, required_fields):
    """Valida campos obrigatórios"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Campos obrigatórios não preenchidos: {', '.join(missing_fields)}")

def validate_file_extension(filename, allowed_extensions):
    """Valida extensão do arquivo"""
    if not filename:
        raise FileError("Nome do arquivo não informado")
    
    extension = filename.lower().split('.')[-1]
    if f".{extension}" not in allowed_extensions:
        raise FileError(f"Extensão .{extension} não permitida. Extensões aceitas: {', '.join(allowed_extensions)}")

def validate_percentage_total(percentages, tolerance=0.01):
    """Valida se o total de percentuais é 100%"""
    total = sum(percentages.values())
    if abs(total - 100) > tolerance:
        raise ValidationError(f"O total dos percentuais deve ser 100%. Total atual: {total:.2f}%")

def safe_json_load(file_path, default=None):
    """Carrega arquivo JSON com tratamento de erro"""
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Arquivo {file_path} não encontrado, usando valor padrão")
        return default if default is not None else []
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do arquivo {file_path}: {str(e)}")
        raise DatabaseError(f"Erro na estrutura do arquivo {file_path}")
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo {file_path}: {str(e)}")
        raise DatabaseError(f"Erro ao carregar dados do arquivo {file_path}")

def safe_json_save(data, file_path):
    """Salva arquivo JSON com tratamento de erro"""
    import json
    import os
    try:
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Salva com backup
        backup_path = f"{file_path}.backup"
        if os.path.exists(file_path):
            import shutil
            shutil.copy2(file_path, backup_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # Remove backup se salvou com sucesso
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo {file_path}: {str(e)}")
        
        # Restaura backup se existir
        backup_path = f"{file_path}.backup"
        if os.path.exists(backup_path):
            import shutil
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
            
        raise DatabaseError(f"Erro ao salvar dados no arquivo {file_path}")
