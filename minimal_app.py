from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from datetime import datetime, date
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

# Funções auxiliares para formatação
def format_date(date_obj):
    """Formata a data para exibição no formato brasileiro"""
    if isinstance(date_obj, datetime) or isinstance(date_obj, date):
        return date_obj.strftime('%d/%m/%Y')
    return date_obj

def format_datetime(dt):
    """Formata a data e hora para exibição no formato brasileiro"""
    if isinstance(dt, datetime):
        return dt.strftime('%d/%m/%Y %H:%M')
    return dt

# Função de simulação para envio de WhatsApp
def send_whatsapp_message(phone, message):
    """
    Simula o envio de mensagem via WhatsApp (para ambiente sem interface gráfica)
    """
    print(f"[SIMULAÇÃO] Enviando WhatsApp para {phone}: {message}")
    return (True, "Mensagem simulada com sucesso")

# Função para criar mensagem de pendência
def create_pendencia_message(pendencia, tipo="nova"):
    """Cria mensagem padrão para pendência"""
    if tipo == "nova":
        message = f"🔔 NOVA PENDÊNCIA REGISTRADA 🔔\n\n"
    elif tipo == "lembrete":
        message = f"🔔 LEMBRETE DE TAREFA PENDENTE 🔔\n\n"
    else:
        message = f"📝 INFORMAÇÃO SOBRE PENDÊNCIA 📝\n\n"
    
    message += f"Pendencias: {pendencia.descricao}\n"
    
    if pendencia.data_prazo:
        message += f"\nPrazo: {format_date(pendencia.data_prazo)}\n"
    
    message += "\nPor favor, não esqueça de solucionar essas pendências\n\nControladoria Geral Pedra Mole/SE"
    return message

# Configurar formatadores de template
@app.template_filter('format_date')
def _format_date(date_obj):
    return format_date(date_obj)

@app.template_filter('format_datetime')
def _format_datetime(dt):
    return format_datetime(dt)

# Cria as tabelas e o usuário admin
with app.app_context():
    db.create_all()
    # Adiciona um usuário admin se não existir
    if not User.query.filter_by(username='controladoriapm').first():
        user = User(username='controladoriapm')
        db.session.add(user)
        db.session.commit()

# Rotas da aplicação
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'controladoriapm' and password == '261214':
            user = User.query.filter_by(username='controladoriapm').first()
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenciais inválidas. Por favor, tente novamente.'
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/pessoas/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_pessoa():
    if request.method == 'POST':
        nome = request.form['nome']
        secretaria = request.form['secretaria']
        telefone = request.form['telefone']
        
        if not nome or not secretaria or not telefone:
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('cadastrar_pessoa'))
        
        nova_pessoa = Pessoa(nome=nome, secretaria=secretaria, telefone=telefone)
        db.session.add(nova_pessoa)
        db.session.commit()
        
        flash('Pessoa cadastrada com sucesso!', 'success')
        return redirect(url_for('listar_pessoas'))
    
    return render_template('cadastrar_pessoa.html')

@app.route('/pessoas')
@login_required
def listar_pessoas():
    pessoas = Pessoa.query.order_by(Pessoa.nome).all()
    return render_template('listar_pessoas.html', pessoas=pessoas)

@app.route('/pessoas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_pessoa(id):
    pessoa = Pessoa.query.get_or_404(id)
    
    if request.method == 'POST':
        pessoa.nome = request.form['nome']
        pessoa.secretaria = request.form['secretaria']
        pessoa.telefone = request.form['telefone']
        
        db.session.commit()
        flash('Cadastro atualizado com sucesso!', 'success')
        return redirect(url_for('listar_pessoas'))
    
    return render_template('editar_pessoa.html', pessoa=pessoa)

@app.route('/pendencias/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_pendencia():
    pessoas = Pessoa.query.order_by(Pessoa.nome).all()
    
    if request.method == 'POST':
        descricao = request.form['descricao']
        pessoa_id = request.form['pessoa_id']
        data_prazo_str = request.form.get('data_prazo', '')
        
        if not descricao or not pessoa_id:
            flash('Descrição e responsável são obrigatórios', 'error')
            return redirect(url_for('cadastrar_pendencia'))
        
        # Processar data de prazo
        data_prazo = None
        if data_prazo_str:
            try:
                data_prazo = datetime.strptime(data_prazo_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de data inválido', 'error')
                return redirect(url_for('cadastrar_pendencia'))
        
        # Criar nova pendência
        nova_pendencia = Pendencia(
            descricao=descricao,
            pessoa_id=pessoa_id,
            data_prazo=data_prazo
        )
        
        db.session.add(nova_pendencia)
        db.session.commit()
        
        # Enviar mensagem por WhatsApp se solicitado
        if 'enviar_whatsapp' in request.form:
            pessoa = Pessoa.query.get(pessoa_id)
            if pessoa and pessoa.telefone:
                message = create_pendencia_message(nova_pendencia, "nova")
                success, msg = send_whatsapp_message(pessoa.telefone, message)
                
                # Registrar mensagem enviada
                nova_mensagem = Mensagem(
                    pendencia_id=nova_pendencia.id,
                    conteudo=message,
                    status_envio='enviado' if success else 'falha'
                )
                db.session.add(nova_mensagem)
                db.session.commit()
                
                if success:
                    flash('Pendência registrada e mensagem enviada com sucesso!', 'success')
                else:
                    flash(f'Pendência registrada, mas houve um problema ao enviar a mensagem: {msg}', 'warning')
            else:
                flash('Pendência registrada, mas o responsável não possui telefone cadastrado', 'warning')
        else:
            flash('Pendência registrada com sucesso!', 'success')
        
        return redirect(url_for('consultar_pendencias'))
    
    return render_template('cadastrar_pendencia.html', pessoas=pessoas, hoje=date.today().strftime('%Y-%m-%d'))

@app.route('/pendencias')
@login_required
def consultar_pendencias():
    # Filtros
    filtro_status = request.args.get('status', 'pendentes')
    
    # Consulta base
    query = Pendencia.query
    
    # Aplicar filtros
    if filtro_status == 'pendentes':
        query = query.filter_by(concluida=False)
    elif filtro_status == 'concluidas':
        query = query.filter_by(concluida=True)
    
    # Ordenar por data de cadastro (mais recentes primeiro)
    pendencias = query.order_by(Pendencia.data_cadastro.desc()).all()
    
    return render_template('consultar_pendencias.html', pendencias=pendencias, filtro_status=filtro_status)

@app.route('/pendencias/<int:id>')
@login_required
def detalhe_pendencia(id):
    pendencia = Pendencia.query.get_or_404(id)
    mensagens = Mensagem.query.filter_by(pendencia_id=id).order_by(Mensagem.data_envio.desc()).all()
    
    return render_template('pendencia_detalhe.html', pendencia=pendencia, mensagens=mensagens)

@app.route('/pendencias/<int:id>/concluir')
@login_required
def concluir_pendencia(id):
    pendencia = Pendencia.query.get_or_404(id)
    pendencia.concluida = True
    pendencia.data_conclusao = datetime.now()
    
    db.session.commit()
    flash('Pendência marcada como concluída!', 'success')
    
    return redirect(url_for('detalhe_pendencia', id=id))

@app.route('/pendencias/<int:id>/enviar')
@login_required
def enviar_lembrete(id):
    pendencia = Pendencia.query.get_or_404(id)
    pessoa = Pessoa.query.get(pendencia.pessoa_id)
    
    if pessoa and pessoa.telefone:
        message = create_pendencia_message(pendencia, "lembrete")
        success, msg = send_whatsapp_message(pessoa.telefone, message)
        
        # Registrar mensagem enviada
        nova_mensagem = Mensagem(
            pendencia_id=pendencia.id,
            conteudo=message,
            status_envio='enviado' if success else 'falha'
        )
        db.session.add(nova_mensagem)
        db.session.commit()
        
        if success:
            flash('Lembrete enviado com sucesso!', 'success')
        else:
            flash(f'Erro ao enviar lembrete: {msg}', 'error')
    else:
        flash('O responsável não possui telefone cadastrado', 'error')
    
    return redirect(url_for('detalhe_pendencia', id=id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)