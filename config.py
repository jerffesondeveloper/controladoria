import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Configuração básica
    SECRET_KEY = os.environ.get('SECRET_KEY', 'controladoriapm_secret_key')
    
    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///controladoriapm.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Credenciais fixas para login
    ADMIN_USERNAME = 'controladoriapm'
    ADMIN_PASSWORD = '261214'
    
    # Configurações de WhatsApp
    WHATSAPP_ENABLED = True