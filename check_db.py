from app import app, db, Turma
from datetime import datetime

def check_and_fix_database():
    with app.app_context():
        print("Verificando banco de dados...")
        
        # Verificar turmas existentes
        turmas = Turma.query.all()
        print(f"\nTotal de turmas: {len(turmas)}")
        
        if len(turmas) == 0:
            print("\nCriando turmas de exemplo...")
            turmas_exemplo = [
                Turma(
                    nome='Turma A',
                    ano=2025,
                    serie='1º Ano',
                    turno='Manhã',
                    ativa=True,
                    data_criacao=datetime.now()
                ),
                Turma(
                    nome='Turma B',
                    ano=2025,
                    serie='2º Ano',
                    turno='Tarde',
                    ativa=True,
                    data_criacao=datetime.now()
                ),
                Turma(
                    nome='Turma C',
                    ano=2025,
                    serie='3º Ano',
                    turno='Noite',
                    ativa=True,
                    data_criacao=datetime.now()
                )
            ]
            
            for turma in turmas_exemplo:
                db.session.add(turma)
            
            try:
                db.session.commit()
                print("Turmas de exemplo criadas com sucesso!")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao criar turmas: {str(e)}")
                return
        
        # Verificar turmas ativas
        turmas_ativas = Turma.query.filter_by(ativa=True).all()
        print(f"\nTurmas ativas: {len(turmas_ativas)}")
        
        for turma in turmas_ativas:
            print(f"- {turma.nome} ({turma.serie} - {turma.turno})")
        
        if len(turmas_ativas) == 0:
            print("\nAtivando todas as turmas...")
            for turma in turmas:
                turma.ativa = True
            try:
                db.session.commit()
                print("Turmas ativadas com sucesso!")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao ativar turmas: {str(e)}")

if __name__ == '__main__':
    check_and_fix_database()