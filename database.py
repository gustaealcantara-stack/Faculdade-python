import sqlite3


def get_connection():
    """Cria a conexão com o banco de dados"""
    conn = sqlite3.connect("faculdade.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db ():
    """Cria as tabelas do banco de dados caso ainda não existam"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Tabela de alunos
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

        # Tabela de professores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_professor INTEGER UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
        """)

        # Tabela de disciplinas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL
        )
        """)

       # Tabela de notas: relação entre aluno, professor e disciplina com notas e faltas
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
        
        # Usuários do sistema: autenticação e vínculo com aluno ou professor
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL CHECK (perfil IN ('aluno', 'professor', 'admin')),
            aluno_id INTEGER,
            professor_id INTEGER,
                       
            FOREIGN KEY (aluno_id) REFERENCES alunos(id),
            FOREIGN KEY (professor_id) REFERENCES professores(id),
                       
            -- Garante integridade dos dados:
            -- Apenas um vínculo deve existir, de acordo com o perfil                       
            CHECK (
                (perfil = 'aluno' AND aluno_id IS NOT NULL AND professor_id IS NULL) OR
                (perfil = 'professor' AND professor_id IS NOT NULL AND aluno_id IS NULL) OR
                (perfil = 'admin' AND aluno_id IS NULL AND professor_id IS NULL)
            )
        )
        """)
        
        # Garante que sempre exista um admin
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


def excluir_tabela(nome_tabela: str):
    """Exclui apenas uma tabela das válidas"""
    tabelas_validas = ["alunos", "professores", "disciplinas", "notas", "usuarios"]
    if nome_tabela not in tabelas_validas:
        print("Erro: tabela inválida.")
        return
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {nome_tabela}")
            print(f"Tabela '{nome_tabela}' excluída com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao excluir tabela: {e}")


def excluir_todas_tabelas():
    tabelas = ["notas", "usuarios", "alunos", "professores", "disciplinas"]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            for tabela in tabelas:
                cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
                print(f"Tabela '{tabela}' excluída com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao excluir tabelas: {e}")