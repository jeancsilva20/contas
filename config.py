
import os
from pathlib import Path

class Config:
    """Configurações da aplicação"""
    
    # Configurações básicas do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui_123456789'
    
    # Configurações de arquivos
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    TEMP_DIR = BASE_DIR / 'temp'
    UPLOAD_DIR = BASE_DIR / 'uploads'
    
    # Tamanho máximo de arquivo (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Extensões de arquivo permitidas
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    
    # Configurações de encoding
    DEFAULT_ENCODING = 'utf-8'
    FALLBACK_ENCODINGS = ['latin-1', 'iso-8859-1', 'cp1252']
    
    # Configurações de dados
    FONTES_PADRAO = ['Cartão C6', 'Conta C6', 'Cartão XP', 'Conta XP']
    PESSOAS_PADRAO = ['Jean', 'João Rafael', 'Juliano', 'Tati', 'João Batista']
    
    # Configurações de validação
    TOLERANCE_PERCENTAGE = 0.01  # Tolerância para validação de percentuais
    
    # Configurações de paginação
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 100
    
    @classmethod
    def init_app(cls, app):
        """Inicializa configurações específicas da aplicação"""
        # Cria diretórios necessários
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        
        # Configura Flask
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 5000

# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
