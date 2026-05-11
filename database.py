import sqlite3


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco de dados SQLite e
    abre o arquivo ``faculdade.db``
    
    Returns:
        sqlite3.Connection: Objeto de conexão com o banco de dados.
    """
    # Abre (ou cria, caso não exista) o arquivo do banco de dados.
    conn = sqlite3.connect("faculdade.db")

    # Ativa a verificação de chaves estrangeiras no SQLite.
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def inicializar_db() -> None:
    """
     Cria todas as tabelas do sistema caso ainda não existam.

    As tabelas criadas são:
    - alunos
    - professores
    - disciplinas
    - notas
    - usuarios

    Ao final da inicialização, a função também garante a existência
    de um usuário administrador padrão, utilizando ``INSERT OR IGNORE``
    para evitar duplicações.

    Usuário administrador padrão:
    - Email: admin@cruzeirodosul.edu.br
    - Senha: admin123

    Returns:
        None
    """
    
    # Abre uma conexão com o banco e fecha automaticamente ao final.
    with get_connection() as conn:
        cursor = conn.cursor()

        # ==========================================================
        # TABELA ALUNOS
        # Armazena os dados cadastrais dos alunos.
        # ==========================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rgm INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            curso TEXT
        )
        """)
        
        # ==========================================================
        # TABELA PROFESSORES
        # Armazena os dados cadastrais dos professores.
        # ==========================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_professor INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
        """)

        # ==========================================================
        # TABELA DISCIPLINAS
        # Armazena as disciplinas disponíveis no sistema.
        # ==========================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL
        )
        """)

        # ==========================================================
        # TABELA NOTAS
        # Representa o vínculo entre:
        # - aluno
        # - professor
        # - disciplina
        #
        # Também armazena:
        # - notas A1, A2 e AF
        # - média final
        # - quantidade de faltas
        # ==========================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL, 
            professor_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            a1 REAL,
            a2 REAL,
            af REAL,
            media REAL,
            faltas INTEGER DEFAULT 0,
                       
            FOREIGN KEY (aluno_id) REFERENCES alunos(id),
            FOREIGN KEY (professor_id) REFERENCES professores(id),
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id)
        )
        """)
        
        # ==========================================================
        # TABELA USUARIOS
        # Responsável pela autenticação e controle de acesso.
        #
        # Perfis permitidos:
        # - aluno
        # - professor
        # - admin
        #
        # Dependendo do perfil:
        # - aluno     -> deve possuir aluno_id
        # - professor -> deve possuir professor_id
        # - admin     -> não possui vínculo com aluno ou professor
        #
        # A restrição CHECK garante essas regras automaticamente.
        # ==========================================================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL CHECK (
                perfil IN ('aluno', 'professor', 'admin')
            ),
            aluno_id INTEGER,
            professor_id INTEGER,
                       
            FOREIGN KEY (aluno_id) REFERENCES alunos(id),
            FOREIGN KEY (professor_id) REFERENCES professores(id),
                                              
            CHECK (
                (perfil = 'aluno' AND aluno_id IS NOT NULL AND professor_id IS NULL) OR
                (perfil = 'professor' AND professor_id IS NOT NULL AND aluno_id IS NULL) OR
                (perfil = 'admin' AND aluno_id IS NULL AND professor_id IS NULL)
            )
        )
        """)
        
        # ==========================================================
        # USUÁRIO ADMINISTRADOR PADRÃO
        #
        # INSERT OR IGNORE:
        # - Insere o registro caso ele ainda não exista.
        # - Se já existir um usuário com o mesmo e-mail, nada acontece.
        # ==========================================================
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (
                email,
                senha,
                perfil,
                aluno_id,
                professor_id
            )
            VALUES (?, ?, ?, NULL, NULL)
        """, (
            "admin@cruzeirodosul.edu.br",
            "admin123",
            "admin"
        ))


def excluir_todas_tabelas() -> None:
    """
    Exclui todas as tabelas do banco de dados.

    A ordem de exclusão é importante para evitar erros de
    chave estrangeira (FOREIGN KEY constraint failed). Por isso,
    a tabela ``notas`` é removida primeiro, seguida pelas tabelas
    que dependem dela ou que possuem relacionamentos entre si.

    Tabelas excluídas:
    1. notas
    2. usuarios
    3. alunos
    4. professores
    5. disciplinas

    Returns:
        None
    """

    # Lista de tabelas na ordem correta de exclusão.
    tabelas = ["notas", "usuarios", "alunos", "professores", "disciplinas"]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Percorre a lista e remove cada tabela.
            for tabela in tabelas:
                cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
                print(f"Tabela '{tabela}' excluída com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao excluir tabelas: {e}")
