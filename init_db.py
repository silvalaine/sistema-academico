from app import app, db, Turma, Disciplina, Aluno
from datetime import datetime

def init_db():
    with app.app_context():
        print("Iniciando criação do banco de dados...")
        
        # Criar todas as tabelas
        db.create_all()
        print("Tabelas criadas com sucesso!")
        
        # Verificar se já existem turmas
        turmas_count = Turma.query.count()
        print(f"Total de turmas existentes: {turmas_count}")
        
        if turmas_count == 0:
            # Criar algumas turmas de exemplo
            turmas = [
                Turma(nome='Turma A', ano=2025, serie='1º Ano', turno='Manhã', ativa=True),
                Turma(nome='Turma B', ano=2025, serie='2º Ano', turno='Tarde', ativa=True),
                Turma(nome='Turma C', ano=2025, serie='3º Ano', turno='Noite', ativa=True)
            ]
            
            for turma in turmas:
                db.session.add(turma)
            
            try:
                db.session.commit()
                print('Turmas de exemplo foram criadas com sucesso!')
            except Exception as e:
                db.session.rollback()
                print('Erro ao criar turmas:', str(e))
        else:
            print(f'O banco já possui {turmas_count} turmas cadastradas.')
            
        # Mostrar turmas ativas
        turmas_ativas = Turma.query.filter_by(ativa=True).all()
        print('\nTurmas ativas:')
        for turma in turmas_ativas:
            print(f'- {turma.nome} ({turma.serie} - {turma.turno})')

if __name__ == '__main__':
    init_db()