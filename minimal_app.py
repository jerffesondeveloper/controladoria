from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/controladoriapm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo simples para teste
class Teste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

# Cria as tabelas
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Sistema de Controle de Pendências - Banco de Dados Conectado!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)