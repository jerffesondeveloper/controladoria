from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from datetime import datetime
import os

app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = 'chave-secreta-temporaria'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/controladoriapm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização das extensões
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuário para login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)

# Seus modelos originais
class Pessoa(db.Model):
    __tablename__ = 'pessoas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    secretaria = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamento com pendências
    pendencias = db.relationship('Pendencia', back_populates='responsavel')

class Pendencia(db.Model):
    __tablename__ = 'pendencias'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_prazo = db.Column(db.Date, nullable=True)
    concluida = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    
    # Chave estrangeira para o responsável
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoas.id'), nullable=False)
    
    # Relacionamento com a pessoa
    responsavel = db.relationship('Pessoa', back_populates='pendencias')
    
    # Histórico de mensagens enviadas
    mensagens = db.relationship('Mensagem', backref='pendencia', lazy=True)

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    
    id = db.Column(db.Integer, primary_key=True)
    pendencia_id = db.Column(db.Integer, db.ForeignKey('pendencias.id'), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.now)
    conteudo = db.Column(db.Text, nullable=False)
    status_envio = db.Column(db.String(20), default='enviado')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Cria as tabelas
with app.app_context():
    db.create_all()
    # Adiciona um usuário de teste se não existir
    if not User.query.filter_by(username='controladoriapm').first():
        user = User(username='controladoriapm')
        db.session.add(user)
        db.session.commit()

@app.route('/')
@login_required
def home():
    return "Sistema de Controle de Pendências - Modelos Completos!"

@app.route('/login')
def login():
    user = User.query.filter_by(username='controladoriapm').first()
    login_user(user)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return "Logout realizado com sucesso!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)