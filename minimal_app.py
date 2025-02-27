from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
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

# Modelo de usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)

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
    return "Sistema de Controle de Pendências - Login Funcionando!"

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