from app import app, db

def reset_database():
    print("Iniciando reset do banco de dados...")
    
    with app.app_context():
        print("Removendo todas as tabelas...")
        db.drop_all()
        
        print("Recriando todas as tabelas com o novo schema...")
        db.create_all()
        
        print("Banco de dados recriado com sucesso!")

if __name__ == '__main__':
    reset_database()