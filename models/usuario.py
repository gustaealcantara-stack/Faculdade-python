import sqlite3
from database import get_connection


def autenticar_usuario(email: str, senha: str) -> tuple | None:
    """
    Autentica um usuário no sistema com base em email e senha.

    A função consulta a tabela `usuarios` e verifica se existe
    um registro com as credenciais informadas.

    Args:
        email (str): Email do usuário.
        senha (str): Senha do usuário.

    Returns:
         tuple | None:
            - tuple: dados do usuário autenticado no formato
              (id, email, perfil, aluno_id, professor_id)
            - None: caso não exista usuário com as credenciais informadas
              ou ocorra falha na consulta
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, email, perfil, aluno_id, professor_id
                FROM usuarios
                WHERE email = ? AND senha = ?
            """, (email, senha))

            return cursor.fetchone()

    except Exception as e:
        print(f"Erro ao autenticar usuário: {e}")
        return None
    

def obter_usuarios() -> list[tuple] | list:
    """
    Retorna todos os usuários cadastrados no sistema.

    Essa função consulta a tabela ``usuarios`` e retorna todos os registros
    existentes no banco de dados.

    Returns:
        list[tuple] | list:
            - list[tuple]: lista de usuários encontrados no banco,
              onde cada registro contém (id, email, perfil, aluno_id, professor_id)
            - list: lista vazia caso ocorra erro na consulta ou não existam dados
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, email, perfil, aluno_id, professor_id
                FROM usuarios
            """)

            return cursor.fetchall()

    except Exception as e:
        print(f"Erro ao obter usuários: {e}")
        # mesmo dando erro passa uma lista vazia
        return []
