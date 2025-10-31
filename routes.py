from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db, Turma, Disciplina, Aluno, Periodo, TipoAvaliacao, TurmaDisciplina, Frequencia, Conteudo, Nota
from datetime import datetime, date
from sqlalchemy import and_, or_
import re
from utils import generate_pdf
import os

# Configurar o caminho do wkhtmltopdf
if os.name == 'nt':  # Windows
    os.environ['WKHTMLTOPDF_PATH'] = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:  # Linux/Mac
    os.environ['WKHTMLTOPDF_PATH'] = 'wkhtmltopdf'

# Rota principal
@app.route('/')
def index():
    # Contar registros para o dashboard
    turmas_count = Turma.query.filter_by(ativa=True).count()
    alunos_count = Aluno.query.filter_by(ativo=True).count()
    disciplinas_count = Disciplina.query.filter_by(ativa=True).count()
    periodos_count = Periodo.query.filter_by(ativo=True).count()
    
    return render_template('index.html', 
                         turmas_count=turmas_count,
                         alunos_count=alunos_count,
                         disciplinas_count=disciplinas_count,
                         periodos_count=periodos_count)

# ========== ROTAS DE CADASTRO ==========

# Cadastro de Turmas
@app.route('/cadastros/turmas')
def turmas():
    turmas = Turma.query.filter_by(ativa=True).all()
    return render_template('cadastros/turmas.html', turmas=turmas)

@app.route('/cadastros/turmas/novo', methods=['GET', 'POST'])
def nova_turma():
    if request.method == 'POST':
        turma = Turma(
            nome=request.form['nome'],
            ano=int(request.form['ano']),
            serie=request.form['serie'],
            turno=request.form['turno']
        )
        db.session.add(turma)
        db.session.commit()
        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('turmas'))
    return render_template('cadastros/nova_turma.html')

@app.route('/cadastros/turmas/editar/<int:id>', methods=['GET', 'POST'])
def editar_turma(id):
    turma = Turma.query.get_or_404(id)
    if request.method == 'POST':
        turma.nome = request.form['nome']
        turma.ano = int(request.form['ano'])
        turma.serie = request.form['serie']
        turma.turno = request.form['turno']
        db.session.commit()
        flash('Turma atualizada com sucesso!', 'success')
        return redirect(url_for('turmas'))
    return render_template('cadastros/editar_turma.html', turma=turma)

@app.route('/cadastros/turmas/excluir/<int:id>')
def excluir_turma(id):
    turma = Turma.query.get_or_404(id)
    turma.ativa = False
    db.session.commit()
    flash('Turma excluída com sucesso!', 'success')
    return redirect(url_for('turmas'))

# Cadastro de Disciplinas
@app.route('/cadastros/disciplinas')
def disciplinas():
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    return render_template('cadastros/disciplinas.html', disciplinas=disciplinas)

@app.route('/cadastros/disciplinas/nova', methods=['GET', 'POST'])
def nova_disciplina():
    if request.method == 'POST':
        disciplina = Disciplina(
            nome=request.form['nome'],
            codigo=request.form['codigo'],
            carga_horaria=int(request.form['carga_horaria'])
        )
        db.session.add(disciplina)
        db.session.commit()
        flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('disciplinas'))
    return render_template('cadastros/nova_disciplina.html')

@app.route('/cadastros/disciplinas/editar/<int:id>', methods=['GET', 'POST'])
def editar_disciplina(id):
    disciplina = Disciplina.query.get_or_404(id)
    if request.method == 'POST':
        disciplina.nome = request.form['nome']
        disciplina.codigo = request.form['codigo']
        disciplina.carga_horaria = int(request.form['carga_horaria'])
        db.session.commit()
        flash('Disciplina atualizada com sucesso!', 'success')
        return redirect(url_for('disciplinas'))
    return render_template('cadastros/editar_disciplina.html', disciplina=disciplina)

@app.route('/cadastros/disciplinas/excluir/<int:id>')
def excluir_disciplina(id):
    disciplina = Disciplina.query.get_or_404(id)
    disciplina.ativa = False
    db.session.commit()
    flash('Disciplina excluída com sucesso!', 'success')
    return redirect(url_for('disciplinas'))

# Cadastro de Alunos
@app.route('/cadastros/alunos')
def alunos():
    alunos = Aluno.query.filter_by(ativo=True).all()
    return render_template('cadastros/alunos.html', alunos=alunos)

@app.route('/cadastros/alunos/novo', methods=['GET', 'POST'])
def novo_aluno():
    # Buscar todas as turmas ativas para o formulário
    turmas = Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()
    
    if request.method == 'POST':
        try:
            # Pegar dados do formulário
            matricula = request.form.get('matricula', '').strip() or None
            cpf = request.form.get('cpf', '').strip() or None
            nome = request.form.get('nome', '').strip()
            data_nascimento = request.form.get('data_nascimento', '').strip() or None
            telefone = request.form.get('telefone', '').strip() or None
            email = request.form.get('email', '').strip() or None
            endereco = request.form.get('endereco', '').strip() or None
            turma_id = request.form.get('turma_id', '').strip() or None

            # Validações
            if matricula:
                existe_matricula = Aluno.query.filter_by(matricula=matricula).first()
                if existe_matricula:
                    flash('Esta matrícula já está em uso.', 'error')
                    return render_template('cadastros/novo_aluno.html', turmas=turmas)

            if cpf:
                existe_cpf = Aluno.query.filter_by(cpf=cpf).first()
                if existe_cpf:
                    flash('Este CPF já está em uso.', 'error')
                    return render_template('cadastros/novo_aluno.html', turmas=turmas)

            # Converter data de nascimento se fornecida
            data_nascimento_convertida = None
            if data_nascimento:
                data_nascimento_convertida = datetime.strptime(data_nascimento, '%Y-%m-%d').date()

            # Criar novo aluno
            aluno = Aluno(
                nome=nome,
                matricula=matricula,
                cpf=cpf,
                data_nascimento=data_nascimento_convertida,
                telefone=telefone,
                email=email,
                endereco=endereco,
                turma_id=turma_id
            )
            
            db.session.add(aluno)
            db.session.commit()
            flash('Aluno cadastrado com sucesso!', 'success')
            return redirect(url_for('alunos'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar aluno: {str(e)}")
            flash('Erro ao cadastrar aluno. Verifique os dados e tente novamente.', 'error')
            return render_template('cadastros/novo_aluno.html', turmas=turmas)
            
    return render_template('cadastros/novo_aluno.html', turmas=turmas)

@app.route('/cadastros/alunos/editar/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):
    aluno = Aluno.query.get_or_404(id)
    turmas = Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()
    
    if request.method == 'POST':
        try:
            # Pegar dados do formulário
            matricula = request.form.get('matricula', '').strip() or None
            cpf = request.form.get('cpf', '').strip() or None
            nome = request.form.get('nome', '').strip()
            data_nascimento = request.form.get('data_nascimento', '').strip() or None
            telefone = request.form.get('telefone', '').strip() or None
            email = request.form.get('email', '').strip() or None
            endereco = request.form.get('endereco', '').strip() or None
            turma_id = request.form.get('turma_id', '').strip() or None
            
            # Validar matrícula única se foi alterada
            if matricula != aluno.matricula:
                existe_matricula = Aluno.query.filter(
                    Aluno.id != id,
                    Aluno.matricula == matricula
                ).first()
                if existe_matricula:
                    flash('Esta matrícula já está em uso.', 'error')
                    return render_template('cadastros/editar_aluno.html', aluno=aluno, turmas=turmas)
            
            # Validar CPF único se foi alterado
            if cpf != aluno.cpf:
                existe_cpf = Aluno.query.filter(
                    Aluno.id != id,
                    Aluno.cpf == cpf
                ).first()
                if existe_cpf:
                    flash('Este CPF já está em uso.', 'error')
                    return render_template('cadastros/editar_aluno.html', aluno=aluno, turmas=turmas)
            
            # Converter data de nascimento se fornecida
            data_nascimento_convertida = None
            if data_nascimento:
                data_nascimento_convertida = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
                
            # Atualizar dados do aluno
            aluno.nome = nome
            aluno.matricula = matricula
            aluno.cpf = cpf
            aluno.data_nascimento = data_nascimento_convertida
            aluno.telefone = telefone
            aluno.email = email
            aluno.endereco = endereco
            aluno.turma_id = turma_id
            
            db.session.commit()
            flash('Aluno atualizado com sucesso!', 'success')
            return redirect(url_for('alunos'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar aluno: {str(e)}")
            flash('Erro ao atualizar aluno. Verifique os dados e tente novamente.', 'error')
            return render_template('cadastros/editar_aluno.html', aluno=aluno, turmas=turmas)
            
    return render_template('cadastros/editar_aluno.html', aluno=aluno, turmas=turmas)

@app.route('/cadastros/alunos/excluir/<int:id>')
def excluir_aluno(id):
    aluno = Aluno.query.get_or_404(id)
    aluno.ativo = False
    db.session.commit()
    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('alunos'))

# Cadastro de Períodos
@app.route('/cadastros/periodos')
def periodos():
    periodos = Periodo.query.filter_by(ativo=True).all()
    return render_template('cadastros/periodos.html', periodos=periodos)

@app.route('/cadastros/periodos/novo', methods=['GET', 'POST'])
def novo_periodo():
    if request.method == 'POST':
        periodo = Periodo(
            nome=request.form['nome'],
            data_inicio=datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date(),
            data_fim=datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date()
        )
        db.session.add(periodo)
        db.session.commit()
        flash('Período cadastrado com sucesso!', 'success')
        return redirect(url_for('periodos'))
    return render_template('cadastros/novo_periodo.html')

@app.route('/cadastros/periodos/editar/<int:id>', methods=['GET', 'POST'])
def editar_periodo(id):
    periodo = Periodo.query.get_or_404(id)
    if request.method == 'POST':
        periodo.nome = request.form['nome']
        periodo.data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
        periodo.data_fim = datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date()
        db.session.commit()
        flash('Período atualizado com sucesso!', 'success')
        return redirect(url_for('periodos'))
    return render_template('cadastros/editar_periodo.html', periodo=periodo)

@app.route('/cadastros/periodos/excluir/<int:id>')
def excluir_periodo(id):
    periodo = Periodo.query.get_or_404(id)
    periodo.ativo = False
    db.session.commit()
    flash('Período excluído com sucesso!', 'success')
    return redirect(url_for('periodos'))

# Cadastro de Tipos de Avaliação
@app.route('/cadastros/tipos_avaliacao')
def tipos_avaliacao():
    tipos = TipoAvaliacao.query.filter_by(ativo=True).all()
    return render_template('cadastros/tipos_avaliacao.html', tipos=tipos)

@app.route('/cadastros/tipos_avaliacao/novo', methods=['GET', 'POST'])
def novo_tipo_avaliacao():
    if request.method == 'POST':
        tipo = TipoAvaliacao(
            nome=request.form['nome'],
            peso=float(request.form['peso'])
        )
        db.session.add(tipo)
        db.session.commit()
        flash('Tipo de avaliação cadastrado com sucesso!', 'success')
        return redirect(url_for('tipos_avaliacao'))
    return render_template('cadastros/novo_tipo_avaliacao.html')

@app.route('/cadastros/tipos_avaliacao/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_avaliacao(id):
    tipo = TipoAvaliacao.query.get_or_404(id)
    if request.method == 'POST':
        tipo.nome = request.form['nome']
        tipo.peso = float(request.form['peso'])
        db.session.commit()
        flash('Tipo de avaliação atualizado com sucesso!', 'success')
        return redirect(url_for('tipos_avaliacao'))
    return render_template('cadastros/editar_tipo_avaliacao.html', tipo=tipo)

@app.route('/cadastros/tipos_avaliacao/excluir/<int:id>')
def excluir_tipo_avaliacao(id):
    tipo = TipoAvaliacao.query.get_or_404(id)
    tipo.ativo = False
    db.session.commit()
    flash('Tipo de avaliação excluído com sucesso!', 'success')
    return redirect(url_for('tipos_avaliacao'))

# ========== ROTAS DE FREQUÊNCIA ==========

@app.route('/frequencia')
def frequencia():
    turmas = Turma.query.filter_by(ativa=True).all()
    return render_template('frequencia/index.html', turmas=turmas)

@app.route('/frequencia/registrar', methods=['GET', 'POST'])
def registrar_frequencia():
    # Buscar todas as turmas ativas primeiro
    turmas = Turma.query.filter_by(ativa=True).all()
    print(f"DEBUG: Encontradas {len(turmas)} turmas ativas")
    for turma in turmas:
        print(f"DEBUG: Turma: {turma.nome} - {turma.serie} ({turma.turno})")
    
    # Obter parâmetros da URL
    turma_id = request.args.get('turma_id')
    data = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    
    print(f"DEBUG: Parâmetros recebidos - turma_id: {turma_id}, data: {data}")
    
    # Se tiver turma_id, buscar a turma específica e seus alunos
    turma = None
    alunos = []
    if turma_id:
        turma = Turma.query.get(turma_id)
        if turma:
            print(f"DEBUG: Turma encontrada: {turma.nome}")
            alunos = Aluno.query.filter_by(ativo=True, turma_id=turma_id).all()
            print(f"DEBUG: Encontrados {len(alunos)} alunos na turma")
    
    if request.method == 'POST':
        turma_id = request.form.get('turma_id')
        data_str = request.form.get('data')
        
        # Validação dos campos obrigatórios
        if not turma_id or turma_id == '':
            flash('Por favor, selecione uma turma.', 'error')
            return redirect(url_for('registrar_frequencia'))
        
        if not data_str:
            flash('Por favor, selecione uma data.', 'error')
            return redirect(url_for('registrar_frequencia'))
        
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida. Por favor, selecione uma data válida.', 'error')
            return redirect(url_for('registrar_frequencia'))
        
        # Verificar se a turma existe
        turma = Turma.query.get(turma_id)
        if not turma:
            flash('Turma não encontrada.', 'error')
            return redirect(url_for('registrar_frequencia'))
        
        # Buscar alunos da turma
        alunos = Aluno.query.filter_by(ativo=True, turma_id=turma_id).all()
        
        if not alunos:
            flash('Nenhum aluno cadastrado nesta turma.', 'warning')
            return redirect(url_for('registrar_frequencia'))
        
        # Registrar frequência para cada aluno
        registros_adicionados = 0
        for aluno in alunos:
            presente = request.form.get(f'aluno_{aluno.id}') == 'on'
            frequencia = Frequencia(
                turma_id=turma_id,
                aluno_id=aluno.id,
                data=data,
                presente=presente,
                observacoes=request.form.get(f'obs_{aluno.id}', '')
            )
            db.session.add(frequencia)
            registros_adicionados += 1
        
        db.session.commit()
        flash(f'Frequência registrada com sucesso! {registros_adicionados} registro(s) adicionado(s).', 'success')
        return redirect(url_for('frequencia'))
    
    turma_id = request.args.get('turma_id')
    data = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    
    # Buscar todas as turmas ativas
    turmas = Turma.query.filter_by(ativa=True).all()
    
    if turma_id:
        turma = Turma.query.get(turma_id)
        if turma:
            alunos = Aluno.query.filter_by(ativo=True, turma_id=turma_id).order_by(Aluno.nome).all()
            return render_template('frequencia/registrar.html', turma=turma, alunos=alunos, turmas=turmas, data=data)
        else:
            flash('Turma não encontrada!', 'error')
    
    return render_template('frequencia/registrar.html', turmas=turmas, turma_id=turma_id, data=data)

@app.route('/frequencia/consultar')
def consultar_frequencia():
    turma_id = request.args.get('turma_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Frequencia.query
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    if data_inicio:
        query = query.filter(Frequencia.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    if data_fim:
        query = query.filter(Frequencia.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    frequencias = query.order_by(Frequencia.data.desc()).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    
    return render_template('frequencia/consultar.html', frequencias=frequencias, turmas=turmas)


# Rotas para editar/excluir frequência
@app.route('/frequencia/editar/<int:id>', methods=['GET', 'POST'])
def frequencia_editar(id):
    freq = Frequencia.query.get_or_404(id)
    turmas = Turma.query.filter_by(ativa=True).all()
    alunos = Aluno.query.filter_by(ativo=True).all()

    if request.method == 'POST':
        try:
            freq.turma_id = int(request.form.get('turma_id') or freq.turma_id)
            freq.aluno_id = int(request.form.get('aluno_id') or freq.aluno_id)
            if request.form.get('data'):
                freq.data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
            freq.presente = True if request.form.get('presente') == 'on' else False
            freq.observacoes = request.form.get('observacoes')
            db.session.commit()
            flash('Frequência atualizada com sucesso!', 'success')
            return redirect(url_for('consultar_frequencia'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar frequência: {e}")
            flash('Erro ao atualizar a frequência.', 'error')

    return render_template('frequencia/editar.html', frequencia=freq, turmas=turmas, alunos=alunos)


@app.route('/frequencia/excluir/<int:id>')
def frequencia_excluir(id):
    freq = Frequencia.query.get_or_404(id)
    try:
        db.session.delete(freq)
        db.session.commit()
        flash('Registro de frequência excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir frequência: {e}")
        flash('Erro ao excluir o registro de frequência.', 'error')
    return redirect(url_for('consultar_frequencia'))

# ========== ROTAS DE CONTEÚDO ==========

@app.route('/conteudo')
def conteudo():
    turmas = Turma.query.filter_by(ativa=True).all()
    return render_template('conteudo/index.html', turmas=turmas)

@app.route('/conteudo/novo', methods=['GET', 'POST'])
def novo_conteudo():
    if request.method == 'POST':
        conteudo = Conteudo(
            turma_id=request.form['turma_id'],
            disciplina_id=request.form['disciplina_id'],
            data=datetime.strptime(request.form['data'], '%Y-%m-%d').date(),
            titulo=request.form['titulo'],
            descricao=request.form.get('descricao'),
            conteudo_ministrado=request.form.get('conteudo_ministrado'),
            atividades=request.form.get('atividades')
        )
        db.session.add(conteudo)
        db.session.commit()
        flash('Conteúdo registrado com sucesso!', 'success')
        return redirect(url_for('conteudo'))
    
    turma_id = request.args.get('turma_id')
    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    data = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('conteudo/novo.html', 
                         turmas=turmas, 
                         disciplinas=disciplinas, 
                         turma_id=turma_id,
                         data=data)

@app.route('/conteudo/consultar')
def consultar_conteudo():
    turma_id = request.args.get('turma_id')
    disciplina_id = request.args.get('disciplina_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Conteudo.query
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    if disciplina_id:
        query = query.filter_by(disciplina_id=disciplina_id)
    if data_inicio:
        query = query.filter(Conteudo.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    if data_fim:
        query = query.filter(Conteudo.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    conteudos = query.order_by(Conteudo.data.desc()).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    
    return render_template('conteudo/consultar.html', conteudos=conteudos, turmas=turmas, disciplinas=disciplinas)


# Rotas para editar/excluir conteúdo
@app.route('/conteudo/editar/<int:id>', methods=['GET', 'POST'])
def conteudo_editar(id):
    conteudo = Conteudo.query.get_or_404(id)
    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).all()

    if request.method == 'POST':
        try:
            conteudo.turma_id = int(request.form['turma_id'])
            conteudo.disciplina_id = int(request.form['disciplina_id'])
            conteudo.data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
            conteudo.titulo = request.form['titulo']
            conteudo.descricao = request.form.get('descricao')
            conteudo.conteudo_ministrado = request.form.get('conteudo_ministrado')
            conteudo.atividades = request.form.get('atividades')
            db.session.commit()
            flash('Conteúdo atualizado com sucesso!', 'success')
            return redirect(url_for('consultar_conteudo'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar conteúdo: {e}")
            flash('Erro ao atualizar o conteúdo. Verifique os dados e tente novamente.', 'error')

    return render_template('conteudo/editar.html', conteudo=conteudo, turmas=turmas, disciplinas=disciplinas)


@app.route('/conteudo/excluir/<int:id>')
def conteudo_excluir(id):
    conteudo = Conteudo.query.get_or_404(id)
    try:
        db.session.delete(conteudo)
        db.session.commit()
        flash('Conteúdo excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir conteúdo: {e}")
        flash('Erro ao excluir o conteúdo.', 'error')
    return redirect(url_for('consultar_conteudo'))

# ========== ROTAS DE NOTAS ==========

@app.route('/notas')
def notas():
    turmas = Turma.query.filter_by(ativa=True).all()
    return render_template('notas/index.html', turmas=turmas)

@app.route('/notas/lancar', methods=['GET', 'POST'])
def lancar_notas():
    if request.method == 'POST':
        turma_id = request.form['turma_id']
        disciplina_id = request.form['disciplina_id']
        periodo_id = request.form['periodo_id']
        tipo_avaliacao_id = request.form['tipo_avaliacao_id']
        
        # Buscar alunos da turma
        alunos = Aluno.query.filter_by(ativo=True).all()
        
        # Lançar notas para cada aluno
        for aluno in alunos:
            nota_valor = request.form.get(f'nota_{aluno.id}')
            if nota_valor and nota_valor.strip():
                nota = Nota(
                    turma_id=turma_id,
                    aluno_id=aluno.id,
                    disciplina_id=disciplina_id,
                    periodo_id=periodo_id,
                    tipo_avaliacao_id=tipo_avaliacao_id,
                    nota=float(nota_valor),
                    observacoes=request.form.get(f'obs_{aluno.id}', '')
                )
                db.session.add(nota)
        
        db.session.commit()
        flash('Notas lançadas com sucesso!', 'success')
        return redirect(url_for('notas'))
    
    # Obter parâmetros da URL
    turma_id = request.args.get('turma_id')
    disciplina_id = request.args.get('disciplina_id')
    periodo_id = request.args.get('periodo_id')
    tipo_avaliacao_id = request.args.get('tipo_avaliacao_id')
    
    # Buscar dados necessários
    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    periodos = Periodo.query.filter_by(ativo=True).all()
    tipos_avaliacao = TipoAvaliacao.query.filter_by(ativo=True).all()
    
    # Se tiver turma_id, buscar os alunos da turma
    alunos = []
    if turma_id:
        print(f"DEBUG: Buscando alunos para a turma {turma_id}")
        alunos = Aluno.query.filter_by(ativo=True, turma_id=turma_id).order_by(Aluno.nome).all()
        print(f"DEBUG: Encontrados {len(alunos)} alunos na turma")
    
    return render_template('notas/lancar.html', 
                         turmas=turmas, 
                         disciplinas=disciplinas, 
                         periodos=periodos, 
                         tipos_avaliacao=tipos_avaliacao,
                         alunos=alunos,
                         turma_id=turma_id,
                         disciplina_id=disciplina_id,
                         periodo_id=periodo_id,
                         tipo_avaliacao_id=tipo_avaliacao_id)

@app.route('/notas/consultar')
def consultar_notas():
    turma_id = request.args.get('turma_id')
    disciplina_id = request.args.get('disciplina_id')
    periodo_id = request.args.get('periodo_id')
    tipo_avaliacao_id = request.args.get('tipo_avaliacao_id')
    
    query = Nota.query
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    if disciplina_id:
        query = query.filter_by(disciplina_id=disciplina_id)
    if periodo_id:
        query = query.filter_by(periodo_id=periodo_id)
    if tipo_avaliacao_id:
        query = query.filter_by(tipo_avaliacao_id=tipo_avaliacao_id)
    
    notas = query.order_by(Nota.data_lancamento.desc()).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    periodos = Periodo.query.filter_by(ativo=True).all()
    tipos_avaliacao = TipoAvaliacao.query.filter_by(ativo=True).all()
    
    return render_template('notas/consultar.html', 
                         notas=notas, turmas=turmas, disciplinas=disciplinas,
                         periodos=periodos, tipos_avaliacao=tipos_avaliacao)


# Rotas para editar/excluir notas
@app.route('/notas/editar/<int:id>', methods=['GET', 'POST'])
def notas_editar(id):
    nota = Nota.query.get_or_404(id)
    periodos = Periodo.query.filter_by(ativo=True).all()
    tipos_avaliacao = TipoAvaliacao.query.filter_by(ativo=True).all()

    if request.method == 'POST':
        try:
            nota.nota = float(request.form['nota'])
            nota.observacoes = request.form.get('observacoes')
            nota.periodo_id = int(request.form.get('periodo_id') or nota.periodo_id)
            nota.tipo_avaliacao_id = int(request.form.get('tipo_avaliacao_id') or nota.tipo_avaliacao_id)
            if request.form.get('data_lancamento'):
                nota.data_lancamento = datetime.strptime(request.form['data_lancamento'], '%Y-%m-%d')
            db.session.commit()
            flash('Nota atualizada com sucesso!', 'success')
            return redirect(url_for('consultar_notas'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar nota: {e}")
            flash('Erro ao atualizar a nota. Verifique os dados e tente novamente.', 'error')

    return render_template('notas/editar.html', nota=nota, periodos=periodos, tipos_avaliacao=tipos_avaliacao)


@app.route('/notas/excluir/<int:id>')
def notas_excluir(id):
    nota = Nota.query.get_or_404(id)
    try:
        db.session.delete(nota)
        db.session.commit()
        flash('Nota excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir nota: {e}")
        flash('Erro ao excluir a nota.', 'error')
    return redirect(url_for('consultar_notas'))

# ========== ROTAS DE RELATÓRIOS ==========

@app.route('/relatorios')
def relatorios():
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    return render_template('relatorios/index.html', data_relatorio=data_relatorio)

@app.route('/relatorios/turmas')
def relatorio_turmas():
    turmas = Turma.query.filter_by(ativa=True).all()
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    formato = request.args.get('formato')
    
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        filename = f"turmas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/turmas.html',
            output_file,
            turmas=turmas,
            data_relatorio=data_relatorio
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_turmas'))
    
    return render_template('relatorios/turmas.html', 
                         turmas=turmas,
                         data_relatorio=data_relatorio)

@app.route('/relatorios/disciplinas')
def relatorio_disciplinas():
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    formato = request.args.get('formato')
    
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        filename = f"disciplinas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/disciplinas.html',
            output_file,
            disciplinas=disciplinas,
            data_relatorio=data_relatorio
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_disciplinas'))
    
    return render_template('relatorios/disciplinas.html', 
                         disciplinas=disciplinas,
                         data_relatorio=data_relatorio)

@app.route('/relatorios/alunos')
def relatorio_alunos():
    turma_id = request.args.get('turma_id')
    formato = request.args.get('formato')
    
    # Buscar todas as turmas ativas para o filtro
    turmas = Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()
    
    # Buscar alunos com base no filtro
    alunos_query = Aluno.query.filter_by(ativo=True)
    
    # Se uma turma foi selecionada, filtrar os alunos dessa turma
    if turma_id:
        alunos_query = alunos_query.filter_by(turma_id=turma_id)
    
    # Executar a query
    alunos = alunos_query.order_by(Aluno.nome).all()
    
    # Formatar a data do relatório
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        filename = f"alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/alunos.html',
            output_file,
            alunos=alunos,
            turmas=turmas,
            data_relatorio=data_relatorio,
            turma_selecionada=turma_id
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_alunos'))
    
    return render_template('relatorios/alunos.html', 
                         alunos=alunos,
                         turmas=turmas,
                         data_relatorio=data_relatorio,
                         turma_selecionada=turma_id)

@app.route('/relatorios/frequencia')
def relatorio_frequencia():
    turma_id = request.args.get('turma_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    formato = request.args.get('formato')
    
    query = Frequencia.query
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    if data_inicio:
        query = query.filter(Frequencia.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    if data_fim:
        query = query.filter(Frequencia.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    frequencias = query.order_by(Frequencia.data.desc()).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        filename = f"frequencia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/frequencia.html',
            output_file,
            frequencias=frequencias,
            turmas=turmas,
            data_relatorio=data_relatorio
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_frequencia'))
    
    return render_template('relatorios/frequencia.html', 
                         frequencias=frequencias, 
                         turmas=turmas,
                         data_relatorio=data_relatorio)

@app.route('/relatorios/conteudo')
def relatorio_conteudo():
    turma_id = request.args.get('turma_id')
    disciplina_id = request.args.get('disciplina_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    formato = request.args.get('formato')
    
    query = Conteudo.query
    
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    if disciplina_id:
        query = query.filter_by(disciplina_id=disciplina_id)
    if data_inicio:
        query = query.filter(Conteudo.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    if data_fim:
        query = query.filter(Conteudo.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    conteudos = query.order_by(Conteudo.data.desc()).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).all()
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        filename = f"conteudo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/conteudo.html',
            output_file,
            conteudos=conteudos,
            turmas=turmas,
            disciplinas=disciplinas,
            data_relatorio=data_relatorio
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_conteudo'))
    
    return render_template('relatorios/conteudo.html', 
                         conteudos=conteudos, 
                         turmas=turmas, 
                         disciplinas=disciplinas,
                         data_relatorio=data_relatorio)

def organizar_notas_periodo(notas_aluno_disciplina, periodo_id):
    """Organiza as notas do período e calcula a média ponderada."""
    notas_periodo = [n for n in notas_aluno_disciplina if n.periodo_id == periodo_id]
    if not notas_periodo:
        return None, None
        
    # Soma ponderada das notas pelo peso do tipo de avaliação
    soma_pesos = sum(n.tipo_avaliacao.peso for n in notas_periodo)
    if soma_pesos == 0:
        return notas_periodo, None
        
    soma_notas = sum(n.nota * n.tipo_avaliacao.peso for n in notas_periodo)
    media = soma_notas / soma_pesos
    
    # Ordenar notas por tipo de avaliação
    notas_periodo.sort(key=lambda x: x.tipo_avaliacao.nome)
    return notas_periodo, media

def calcular_media_final(medias_periodos):
    """Calcula a média final baseada nas médias dos períodos."""
    medias_validas = [m for m in medias_periodos if m is not None]
    if not medias_validas:
        return None
    return sum(medias_validas) / len(medias_validas)

def calcular_faltas_periodo(aluno_id, turma_id, periodo_inicio, periodo_fim):
    """Calcula total de faltas do aluno em um período."""
    return Frequencia.query.filter(
        Frequencia.aluno_id == aluno_id,
        Frequencia.turma_id == turma_id,
        Frequencia.data >= periodo_inicio,
        Frequencia.data <= periodo_fim,
        Frequencia.presente == False
    ).count()


def _periodo_order_value(p):
    """Gera uma chave de ordenação para `Periodo`.

    Ordem de prioridade:
    1. atributos numéricos `numero` ou `ordem` (se existirem)
    2. número extraído do início de `nome` (ex: '1º Bimestre')
    3. `data_inicio` (se existir)
    4. fallback grande (garante que fique no final)
    """
    # 1) tentar atributos explícitos
    for attr in ('numero', 'ordem'):
        val = getattr(p, attr, None)
        if val is not None:
            try:
                return int(val)
            except Exception:
                # se não for inteiro, ignorar
                pass

    # 2) tentar extrair número do nome (ex: '1º Bimestre', '2 - Bimestre')
    nome = str(getattr(p, 'nome', '') or '')
    m = re.match(r"\s*(\d+)", nome)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            pass

    # 3) usar data_inicio quando disponível
    data = getattr(p, 'data_inicio', None)
    if data is not None:
        return data

    # 4) fallback: valor alto para colocar no final
    return 999999

@app.route('/relatorios/boletim')
def boletim():
    turma_id = request.args.get('turma_id')
    aluno_id = request.args.get('aluno_id')
    formato = request.args.get('formato')
    disciplina_id = request.args.get('disciplina_id')  # Adicionar disciplina_id dos parâmetros
    
    # Buscar todos os alunos ativos
    query = Aluno.query.filter_by(ativo=True)
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    if aluno_id:
        query = query.filter_by(id=aluno_id)
    
    alunos = query.order_by(Aluno.nome).all()

    # Carregar períodos usados por notas: somente aqueles com notas lançadas
    aluno_ids = [a.id for a in alunos]
    periodo_ids = []
    if aluno_ids:
        q = db.session.query(Nota.periodo_id).filter(Nota.aluno_id.in_(aluno_ids))
        if disciplina_id:
            q = q.filter(Nota.disciplina_id == disciplina_id)
        periodo_ids = [row[0] for row in q.distinct().all()]

    if periodo_ids:
        periodos = Periodo.query.filter(Periodo.ativo == True, Periodo.id.in_(periodo_ids)).all()
        periodos = sorted(periodos, key=_periodo_order_value)
    else:
        periodos = []

    # Carregar períodos usados por notas: somente aqueles com notas lançadas
    aluno_ids = [a.id for a in alunos]
    periodo_ids = []
    if aluno_ids:
        periodo_ids = [row[0] for row in db.session.query(Nota.periodo_id)
                      .filter(Nota.aluno_id.in_(aluno_ids))
                      .distinct()
                      .all()]

    if periodo_ids:
        periodos = Periodo.query.filter(Periodo.ativo == True, Periodo.id.in_(periodo_ids)).all()
        periodos = sorted(periodos, key=_periodo_order_value)
    else:
        periodos = []

    turmas = Turma.query.filter_by(ativa=True).all()
    disciplinas = {d.id: d for d in Disciplina.query.filter_by(ativa=True).all()}
    
    # Estrutura para armazenar os boletins
    boletins = {}
    
    for aluno in alunos:
        # Buscar todas as notas do aluno
        notas = Nota.query.filter_by(aluno_id=aluno.id).all()
        
        # Agrupar notas por disciplina
        notas_por_disciplina = {}
        for nota in notas:
            if nota.disciplina_id not in notas_por_disciplina:
                notas_por_disciplina[nota.disciplina_id] = []
            notas_por_disciplina[nota.disciplina_id].append(nota)
        
        # Calcular médias por disciplina e período
        medias = {}
        for disciplina_id, notas_disciplina in notas_por_disciplina.items():
            notas_por_periodo = {}
            medias_periodos = {}
            
            for periodo in periodos:
                notas_periodo, media = organizar_notas_periodo(notas_disciplina, periodo.id)
                if notas_periodo:
                    notas_por_periodo[periodo.id] = notas_periodo
                    medias_periodos[periodo.id] = media
            
            media_final = calcular_media_final([
                media for media in medias_periodos.values() if media is not None
            ])
            
            medias[disciplina_id] = {
                'por_periodo': medias_periodos,
                'notas_por_tipo': notas_por_periodo,
                'media_final': media_final
            }
        
        # Adicionar ao dicionário de boletins
        if medias:  # Só adiciona se o aluno tiver notas
            boletins[aluno.id] = {
                'aluno': aluno,
                'medias': medias
            }
    
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Se formato for PDF, gerar arquivo PDF
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        # Nome do arquivo baseado no filtro
        if aluno_id and len(boletins) == 1:
            aluno = list(boletins.values())[0]['aluno']
            filename = f"boletim_{aluno.nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:
            filename = f"boletim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/boletim.html',
            output_file,
            boletins=boletins,
            turmas=turmas,
            alunos=alunos,
            periodos=periodos,
            disciplinas=disciplinas,
            data_relatorio=data_relatorio
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('boletim', turma_id=turma_id, aluno_id=aluno_id))
    
    # Se não for PDF, renderizar HTML normal
    return render_template('relatorios/boletim.html',
                         boletins=boletins,
                         turmas=turmas,
                         alunos=alunos,
                         periodos=periodos,
                         disciplinas=disciplinas,
                         data_relatorio=data_relatorio)

@app.route('/relatorios/notas')
def relatorio_notas():
    print("\nDEBUG: Iniciando relatorio_notas")
    turma_id = request.args.get('turma_id')
    disciplina_id = request.args.get('disciplina_id')
    periodo_id = request.args.get('periodo_id')
    formato = request.args.get('formato')
    print(f"DEBUG: Parâmetros: turma_id={turma_id}, disciplina_id={disciplina_id}, periodo_id={periodo_id}")
    
    # Buscar turma e disciplina se fornecidos
    turma = None
    disciplina = None
    if turma_id:
        turma = Turma.query.get(turma_id)
    if disciplina_id:
        disciplina = Disciplina.query.get(disciplina_id)

    # Buscar alunos da turma
    query_alunos = Aluno.query.filter_by(ativo=True)
    if turma_id:
        query_alunos = query_alunos.filter_by(turma_id=turma_id)
    alunos = query_alunos.order_by(Aluno.nome).all()

    # Estrutura para armazenar as notas por aluno
    notas_por_aluno = {}
    if turma_id and disciplina_id and periodo_id:
        print(f"DEBUG: Filtrando por turma={turma_id}, disciplina={disciplina_id}, periodo={periodo_id}")
        
        # Buscar todos os tipos de avaliação
        tipos_avaliacao = TipoAvaliacao.query.filter_by(ativo=True).all()
        print(f"DEBUG: Encontrados {len(tipos_avaliacao)} tipos de avaliação")
        
        for aluno in alunos:
            print(f"DEBUG: Processando aluno {aluno.nome}")
            notas_por_aluno[aluno.id] = {
                'codigo': aluno.matricula,
                'nome': aluno.nome,
                'notas': {},
                'media_final': 0.0
            }
            
            # Buscar notas do aluno
            notas_aluno = Nota.query.filter_by(
                aluno_id=aluno.id,
                turma_id=turma_id,
                disciplina_id=disciplina_id,
                periodo_id=periodo_id
            ).all()
            print(f"DEBUG: Encontradas {len(notas_aluno)} notas para o aluno {aluno.nome}")
            
            soma_notas = 0
            soma_pesos = 0
            for tipo in tipos_avaliacao:
                nota = next((n for n in notas_aluno if n.tipo_avaliacao_id == tipo.id), None)
                if nota:
                    print(f"DEBUG: Nota {nota.nota} para {tipo.nome}")
                    notas_por_aluno[aluno.id]['notas'][tipo.nome] = nota.nota
                    soma_notas += nota.nota * tipo.peso
                    soma_pesos += tipo.peso
                else:
                    notas_por_aluno[aluno.id]['notas'][tipo.nome] = '-'
                    print(f"DEBUG: Sem nota para {tipo.nome}")
            
            # Calcular média final
            if soma_pesos > 0:
                notas_por_aluno[aluno.id]['media_final'] = round(soma_notas / soma_pesos, 2)

    # Buscar dados para filtros
    turmas = Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).order_by(Disciplina.nome).all()
    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Carregar períodos usados por notas: somente aqueles com notas lançadas
    query_periodos = db.session.query(Nota.periodo_id).distinct()
    if turma_id:
        query_periodos = query_periodos.filter(Nota.turma_id == turma_id)
    if disciplina_id:
        query_periodos = query_periodos.filter(Nota.disciplina_id == disciplina_id)
    periodo_ids = [row[0] for row in query_periodos.all()]
    
    periodos = []
    if periodo_ids:
        periodos = Periodo.query.filter(
            Periodo.id.in_(periodo_ids), 
            Periodo.ativo == True
        ).all()
        periodos = sorted(periodos, key=_periodo_order_value)

    # Carregar períodos usados por notas: somente aqueles com notas lançadas
    query_periodos = db.session.query(Nota.periodo_id).distinct()
    if turma_id:
        query_periodos = query_periodos.filter(Nota.turma_id == turma_id)
    if disciplina_id:
        query_periodos = query_periodos.filter(Nota.disciplina_id == disciplina_id)
    periodo_ids = [row[0] for row in query_periodos.all()]
    
    periodos = []
    if periodo_ids:
        periodos = Periodo.query.filter(
            Periodo.id.in_(periodo_ids), 
            Periodo.ativo == True
        ).all()
        periodos = sorted(periodos, key=_periodo_order_value)
    
    if formato == 'pdf':
        # Criar diretório para relatórios se não existir
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        
        filename = f"notas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)
        
        success, result = generate_pdf(
            'relatorios/notas.html',
            output_file,
            notas_por_aluno=notas_por_aluno,
            turma=turma,
            disciplina=disciplina,
            turmas=turmas,
            disciplinas=disciplinas,
            periodos=periodos,
            tipos_avaliacao=tipos_avaliacao if 'tipos_avaliacao' in locals() else [],
            data_relatorio=data_relatorio
        )
        
        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_notas'))
    
    print(f"DEBUG: notas_por_aluno tem {len(notas_por_aluno)} alunos")
    if 'tipos_avaliacao' in locals():
        print(f"DEBUG: tipos_avaliacao tem {len(tipos_avaliacao)} tipos")
        for tipo in tipos_avaliacao:
            print(f"DEBUG: Tipo de avaliação: {tipo.nome}")
    else:
        print("DEBUG: tipos_avaliacao não está definido")
    
    print("DEBUG: Renderizando template com:")
    print(f"- turma: {turma.nome if turma else 'None'}")
    print(f"- disciplina: {disciplina.nome if disciplina else 'None'}")
    print(f"- turmas: {len(turmas)} registros")
    print(f"- disciplinas: {len(disciplinas)} registros")
    print(f"- periodos: {len(periodos)} registros")
    
    return render_template('relatorios/notas.html', 
                         notas_por_aluno=notas_por_aluno,
                         turma=turma,
                         disciplina=disciplina,
                         turmas=turmas, 
                         disciplinas=disciplinas, 
                         periodos=periodos,
                         tipos_avaliacao=tipos_avaliacao if 'tipos_avaliacao' in locals() else [],
                         data_relatorio=data_relatorio)


@app.route('/relatorios/mapa_acompanhamento')
def relatorio_mapa():
    turma_id = request.args.get('turma_id')
    disciplina_id = request.args.get('disciplina_id')
    formato = request.args.get('formato')

    # Buscar alunos ativos (filtrar por turma se informado)
    query = Aluno.query.filter_by(ativo=True)
    if turma_id:
        query = query.filter_by(turma_id=turma_id)
    alunos = query.order_by(Aluno.nome).all()

    # Carregar períodos usados por notas: somente aqueles com notas lançadas
    query_periodos = db.session.query(Nota.periodo_id).distinct()
    if turma_id:
        query_periodos = query_periodos.filter(Nota.turma_id == turma_id)
    if disciplina_id:
        query_periodos = query_periodos.filter(Nota.disciplina_id == disciplina_id)
    periodo_ids = [row[0] for row in query_periodos.all()]
    
    periodos = []
    if periodo_ids:
        periodos = Periodo.query.filter(
            Periodo.id.in_(periodo_ids), 
            Periodo.ativo == True
        ).all()
        periodos = sorted(periodos, key=_periodo_order_value)

    # Montar o mapa com notas, médias e faltas por período
    mapa = []
    for aluno in alunos:
        notas_query = Nota.query.filter_by(aluno_id=aluno.id)
        if disciplina_id:
            notas_query = notas_query.filter_by(disciplina_id=disciplina_id)
        notas_aluno = notas_query.all()

        notas_por_periodo = {}
        medias_periodos = {}
        for periodo in periodos:
            notas_periodo, media = organizar_notas_periodo(notas_aluno, periodo.id)
            if notas_periodo:
                notas_por_periodo[periodo.id] = notas_periodo
                medias_periodos[periodo.id] = media

        media_final = calcular_media_final([m for m in medias_periodos.values() if m is not None])

        # Calcular faltas por período
        faltas_por_periodo = {}
        total_faltas = 0
        for periodo in periodos:
            faltas = calcular_faltas_periodo(
                aluno_id=aluno.id,
                turma_id=aluno.turma_id,
                periodo_inicio=periodo.data_inicio,
                periodo_fim=periodo.data_fim
            )
            faltas_por_periodo[periodo.id] = faltas
            total_faltas += faltas

        mapa.append({
            'aluno': aluno,
            'notas_por_periodo': notas_por_periodo,
            'medias_periodos': medias_periodos,
            'media_final': media_final,
            'faltas_por_periodo': faltas_por_periodo,
            'total_faltas': total_faltas
        })

    data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M')

    if formato == 'pdf':
        os.makedirs(os.path.join('static', 'relatorios'), exist_ok=True)
        filename = f"mapa_acompanhamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_file = os.path.join('static', 'relatorios', filename)

        success, result = generate_pdf(
            'relatorios/mapa_acompanhamento.html',
            output_file,
            mapa=mapa,
            alunos=alunos,
            periodos=periodos,
            data_relatorio=data_relatorio,
            turma_id=turma_id,
            disciplina_id=disciplina_id
        )

        if success:
            return send_file(
                result,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Erro ao gerar PDF. Por favor, tente novamente.', 'error')
            return redirect(url_for('relatorio_notas'))

    # Buscar turmas e disciplinas para o filtro
    turmas = Turma.query.filter_by(ativa=True).order_by(Turma.nome).all()
    disciplinas = Disciplina.query.filter_by(ativa=True).order_by(Disciplina.nome).all()

    return render_template('relatorios/mapa_acompanhamento.html', 
                         mapa=mapa,
                         alunos=alunos,
                         periodos=periodos,
                         turmas=turmas,
                         disciplinas=disciplinas,
                         data_relatorio=data_relatorio,
                         turma_id=turma_id,
                         disciplina_id=disciplina_id)

