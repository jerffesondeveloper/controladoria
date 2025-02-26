from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pessoa(db.Model):
    __tablename__ = 'pessoas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    secretaria = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamento com pendências (sem backref)
    pendencias = db.relationship('Pendencia', back_populates='responsavel')
    
    def __repr__(self):
        return f'<Pessoa {self.nome}>'

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
    
    # Definir o relacionamento com a pessoa (back_populates em vez de backref)
    responsavel = db.relationship('Pessoa', back_populates='pendencias')
    
    # Histórico de mensagens enviadas
    mensagens = db.relationship('Mensagem', backref='pendencia', lazy=True)
    
    def __repr__(self):
        return f'<Pendencia {self.id}>'
    
class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    
    id = db.Column(db.Integer, primary_key=True)
    pendencia_id = db.Column(db.Integer, db.ForeignKey('pendencias.id'), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.now)
    conteudo = db.Column(db.Text, nullable=False)
    status_envio = db.Column(db.String(20), default='enviado')
    
    def __repr__(self):
        return f'<Mensagem {self.id}>'