from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, Pessoa, Pendencia, Mensagem
from helpers import send_whatsapp_message, create_pendencia_message, format_date, format_datetime
from config import Config
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
import os

# Inicializar a aplicação
app = Flask(__name__)
app.config.from_object(Config)

# Configurar o banco de dados
db.init_app(app)

# Configurar login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe de usuário para o login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Loader para o Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Criar o banco de dados se não existir
with app.app_context():
    db.create_all()

# Configurar formatadores de template
@app.template_filter('format_date')
def _format_date(date):
    return format_date(date)

@app.template_filter('format_datetime')
def _format_datetime(dt):
    return format_datetime(dt)

# Rota inicial - login
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            user = User(1)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenciais inválidas. Por favor, tente novamente.'
    
    return render_template('login.html', error=error)

# Dashboard principal
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Cadastro de pessoas
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

# Listagem de pessoas
@app.route('/pessoas')
@login_required
def listar_pessoas():
    pessoas = Pessoa.query.order_by(Pessoa.nome).all()
    return render_template('listar_pessoas.html', pessoas=pessoas)

# Editar pessoa
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

# Cadastro de pendências
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

# Consulta de pendências
@app.route('/pendencias')
@login_required
def consultar_pendencias():
    try:
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
        
        # DEBUG: Imprimir informações para ajudar na solução
        print(f"Número de pendências encontradas: {len(pendencias)}")
        for p in pendencias:
            print(f"Pendência ID: {p.id}, Responsável ID: {p.pessoa_id}, Descrição: {p.descricao}")
        
        return render_template('consultar_pendencias.html', pendencias=pendencias, filtro_status=filtro_status)
    except Exception as e:
        print(f"ERRO ao consultar pendências: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Ocorreu um erro ao consultar pendências: {str(e)}", "error")
        return redirect(url_for('dashboard'))

# Detalhes da pendência
@app.route('/pendencias/<int:id>')
@login_required
def detalhe_pendencia(id):
    pendencia = Pendencia.query.get_or_404(id)
    mensagens = Mensagem.query.filter_by(pendencia_id=id).order_by(Mensagem.data_envio.desc()).all()
    
    return render_template('pendencia_detalhe.html', pendencia=pendencia, mensagens=mensagens)

# Marcar pendência como concluída
@app.route('/pendencias/<int:id>/concluir')
@login_required
def concluir_pendencia(id):
    pendencia = Pendencia.query.get_or_404(id)
    pendencia.concluida = True
    pendencia.data_conclusao = datetime.now()
    
    db.session.commit()
    flash('Pendência marcada como concluída!', 'success')
    
    return redirect(url_for('detalhe_pendencia', id=id))

# Enviar lembrete sobre a pendência
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

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Verificar e enviar lembretes diariamente
def check_pendencias():
    with app.app_context():
        hoje = date.today()
        # Buscar pendências não concluídas com prazo para hoje
        pendencias_prazo = Pendencia.query.filter_by(concluida=False).filter(Pendencia.data_prazo == hoje).all()
        
        for pendencia in pendencias_prazo:
            pessoa = Pessoa.query.get(pendencia.pessoa_id)
            if pessoa and pessoa.telefone:
                message = create_pendencia_message(pendencia, "lembrete")
                success, _ = send_whatsapp_message(pessoa.telefone, message)
                
                # Registrar mensagem enviada
                nova_mensagem = Mensagem(
                    pendencia_id=pendencia.id,
                    conteudo=message,
                    status_envio='enviado' if success else 'falha'
                )
                db.session.add(nova_mensagem)
        
        db.session.commit()

# Inicializar o agendador
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_pendencias, trigger="cron", hour=8)
scheduler.start()

# Ponto de entrada para execução
if __name__ == '__main__':
    # Criar pasta de banco de dados se não existir
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Criar as tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)