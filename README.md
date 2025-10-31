# Sistema Acadêmico

Sistema web completo para gestão acadêmica desenvolvido em Python com Flask.

## Funcionalidades

### Cadastros
- **Turmas**: Cadastro de turmas com ano, série e turno
- **Disciplinas**: Cadastro de disciplinas com código e carga horária
- **Alunos**: Cadastro completo de alunos com dados pessoais
- **Períodos**: Cadastro de períodos letivos (bimestres, trimestres, etc.)
- **Tipos de Avaliação**: Cadastro de tipos de avaliação com pesos

### Controle Acadêmico
- **Frequência**: Registro de presença/ausência por data e turma (diário de classe)
- **Conteúdo**: Lançamento de conteúdos ministrados por turma e data
- **Notas**: Lançamento de notas por turma, aluno, período e tipo de avaliação

### Relatórios
- Relatórios completos de todas as funcionalidades
- Filtros avançados por data, turma, disciplina e período
- Funcionalidade de impressão

## Tecnologias Utilizadas

- **Backend**: Python 3.x, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Banco de Dados**: SQLite (padrão) ou PostgreSQL/MySQL
- **Ícones**: Bootstrap Icons

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o sistema:
```bash
python app.py
```

4. Acesse no navegador: `http://localhost:5000`

## Estrutura do Projeto

```
sistema-academico/
├── app.py                 # Aplicação principal
├── models.py             # Modelos do banco de dados
├── routes.py             # Rotas da aplicação
├── requirements.txt      # Dependências Python
├── README.md            # Este arquivo
└── templates/           # Templates HTML
    ├── base.html        # Template base
    ├── index.html       # Página inicial
    ├── cadastros/       # Templates de cadastros
    ├── frequencia/      # Templates de frequência
    ├── conteudo/        # Templates de conteúdo
    ├── notas/           # Templates de notas
    └── relatorios/      # Templates de relatórios
```

## Como Usar

1. **Primeiro Acesso**: Cadastre as turmas, disciplinas, alunos, períodos e tipos de avaliação
2. **Controle Diário**: Use as telas de frequência e conteúdo para registrar as atividades diárias
3. **Avaliações**: Lance as notas dos alunos conforme os períodos e tipos de avaliação
4. **Relatórios**: Gere relatórios para acompanhar o desempenho e frequência

## Características

- Interface responsiva e moderna
- Navegação intuitiva com menu lateral
- Validação de dados nos formulários
- Sistema de mensagens de feedback
- Relatórios com filtros avançados
- Funcionalidade de impressão
- Banco de dados SQLite para desenvolvimento

## Desenvolvimento

Para desenvolvimento, o sistema usa SQLite como banco de dados padrão. Para produção, recomenda-se usar PostgreSQL ou MySQL.

## Suporte

Este sistema foi desenvolvido para uso acadêmico e pode ser customizado conforme as necessidades específicas de cada instituição.

## Gerar PDFs (pdfkit + wkhtmltopdf)

Para a funcionalidade de exportar relatórios em PDF, o projeto usa a biblioteca Python `pdfkit`, que depende do executável `wkhtmltopdf`.

Instalação no Windows:

- Usando Chocolatey (recomendado se você tiver o Chocolatey instalado):

```powershell
choco install wkhtmltopdf -y
```

- Ou baixe o instalador em: https://wkhtmltopdf.org/downloads.html (escolha a versão para Windows) e instale manualmente.

Se o `wkhtmltopdf` não estiver no PATH, você pode informar o caminho completo via variável de ambiente `WKHTMLTOPDF_PATH` antes de iniciar a aplicação. Exemplo no PowerShell:

```powershell
$env:WKHTMLTOPDF_PATH = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
python app.py
```

Notas:
- Após instalar o `wkhtmltopdf`, reinicie o terminal/VS Code para que as variáveis de ambiente sejam carregadas corretamente.
- Se a geração de PDF falhar, o sistema registra detalhes em `static/relatorios/pdf_errors.log` para ajudar no diagnóstico.
