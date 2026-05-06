import sqlite3
from database import get_connection


def autenticar_usuario(email: str, senha: str):
    """
    Autentica um usuário pelo email e senha.
    Retorna os dados do usuário se encontrar, senão retorna None.
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
    

def obter_usuarios():
    """Retorna todos os usuários cadastrados."""
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
