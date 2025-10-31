from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sistema_academico_2025'

# Usar SQLite em memória no Vercel
if os.environ.get('VERCEL_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_academico.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir modelos diretamente aqui para evitar importação circular
class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    serie = db.Column(db.String(50), nullable=False)
    turno = db.Column(db.String(20), nullable=False)  # Manhã, Tarde, Noite
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    frequencias = db.relationship('Frequencia', backref='turma', lazy=True)
    conteudos = db.relationship('Conteudo', backref='turma', lazy=True)
    notas = db.relationship('Nota', backref='turma', lazy=True)
    turma_disciplinas = db.relationship('TurmaDisciplina', backref='turma', lazy=True)

    def __repr__(self):
        return f'<Turma {self.nome}>'

class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    turma_disciplinas = db.relationship('TurmaDisciplina', backref='disciplina', lazy=True)
    conteudos = db.relationship('Conteudo', backref='disciplina', lazy=True)
    notas = db.relationship('Nota', backref='disciplina', lazy=True)

    def __repr__(self):
        return f'<Disciplina {self.nome}>'

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    endereco = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=True)
    
    # Relacionamentos
    turma = db.relationship('Turma', backref='alunos', lazy=True)
    frequencias = db.relationship('Frequencia', backref='aluno', lazy=True)
    notas = db.relationship('Nota', backref='aluno', lazy=True)

    def __repr__(self):
        return f'<Aluno {self.nome}>'

class Periodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notas = db.relationship('Nota', backref='periodo', lazy=True)

    def __repr__(self):
        return f'<Periodo {self.nome}>'

class TipoAvaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.Float, nullable=False)  # Peso da avaliação (ex: 0.3 para 30%)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notas = db.relationship('Nota', backref='tipo_avaliacao', lazy=True)

    def __repr__(self):
        return f'<TipoAvaliacao {self.nome}>'

class TurmaDisciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    professor = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TurmaDisciplina {self.turma.nome} - {self.disciplina.nome}>'

class Frequencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=True)
    observacoes = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Frequencia {self.aluno.nome} - {self.data}>'

class Conteudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    conteudo_ministrado = db.Column(db.Text)
    atividades = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Conteudo {self.titulo} - {self.data}>'

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo.id'), nullable=False)
    tipo_avaliacao_id = db.Column(db.Integer, db.ForeignKey('tipo_avaliacao.id'), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.Text)
    data_lancamento = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Nota {self.aluno.nome} - {self.nota}>'

# Importar rotas
from routes import *

# Configuração para produção
app.config['DEBUG'] = False
app.config['ENV'] = 'production'

# Inicializar banco de dados em produção de forma compatível com várias
# versões do Flask (algumas builds serverless não expõem
# `before_first_request`). Usamos um before_request que executa a
# inicialização apenas uma vez por processo.
app.config['DB_INITIALIZED'] = False

@app.before_request
def ensure_db_initialized():
    if not app.config.get('DB_INITIALIZED'):
        try:
            with app.app_context():
                db.create_all()
        except Exception:
            # Não falhar na importação — levantar o erro para aparecer nos logs
            raise
        app.config['DB_INITIALIZED'] = True

# Configuração para servidores WSGI
application = app

# Para desenvolvimento local
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Verificar turmas ao iniciar
        turmas = Turma.query.filter_by(ativa=True).all()
        print(f"\nTurmas ativas no sistema: {len(turmas)}")
        for turma in turmas:
            print(f"- {turma.nome} ({turma.serie} - {turma.turno})")
    
    app.run(debug=True)