import sqlite3
import random

from database import get_connection

from interface.menus import menu_aluno
from interface.utils import pausar

from services.notas import consultar_notas_aluno


def gerar_rgm():
    """Gera um RGM aleatório e único no banco de dados"""
    while True:
        # gera um numero de 8 digitos, underscore apenas para legibilidade
        rgm = random.randint(10_000_000, 99_999_999)

        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Busca o RGM no banco de dados para validar se existe ou não
            cursor.execute("SELECT 1 FROM alunos WHERE rgm = ?", (rgm,))

            # Se existir continua no loop e gera um novo RGM
            # Se não existir aluno com RGM o codigo avança, utiliza o RGM gerado
            if not cursor.fetchone():
                return rgm


def gerar_email_aluno(nome:str, sobrenome:str, rgm:int):
    """Gera um email universitário para aluno. Também evita 
    que duas pessoas com o mesmo nome e sobrenome tenham emails iguas
    """

    # Evita que duas pessoas com o mesmo nome e sobrenome tenham emails iguas
    email = f"{nome}.{sobrenome}{str(rgm)[-3:]}@cs.cruzeirodosul.edu.br".lower()
    return email


def inserir_aluno(nome:str, sobrenome:str, curso:str):
    rgm = gerar_rgm()
    email = gerar_email_aluno(nome, sobrenome, rgm)
    senha = str(rgm)[:4]  # primeiros 4 dígitos
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()  
            
            dados_aluno = (rgm, nome, sobrenome, email, curso)

            # Insere alunos no banco de dados
            cursor.execute('INSERT INTO alunos (rgm, nome, sobrenome, email, curso) VALUES (?, ?, ?, ?, ?)',
                           dados_aluno)

            aluno_id = cursor.lastrowid

            # cria usuário 'aluno' na mesma conexão
            cursor.execute("""
                INSERT INTO usuarios (
                    email,
                    senha,
                    perfil,
                    aluno_id
                )
                VALUES (?, ?, ?, ?)
            """, (
                email,
                senha,
                "aluno",
                aluno_id
            ))

            print("Aluno cadastrado com sucesso!")
            print(f"RGM: {rgm}")
            print(f"Email: {email}")
            print(f"Senha inicial: {senha}")

    except Exception as e:
        print(f"Erro: {e}")


def editar_aluno(novo_nome:str, novo_sobrenome:str, novo_curso:str, rgm: int):
    """Atualiza os dados e gera um e-email novo com os novos nomes."""
    
    
    novo_email = gerar_email_aluno(novo_nome, novo_sobrenome, rgm)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            sql = """
            UPDATE alunos
            SET nome = ?,
                sobrenome = ?,
                email = ?,
                curso = ?
            WHERE rgm = ?
            """
            
            ############################################################################
            cursor.execute(sql, (novo_nome, novo_sobrenome, novo_email, novo_curso, rgm))

            if cursor.rowcount > 0:
                print(f"Sucesso: Aluno do RGM {rgm} atualizado!")
            else:
                print(f"Aviso: RGM {rgm} não encontrado para edição.")
                
    except sqlite3.Error as e:
        print(f"Erro ao editar banco de dados: {e}")


def deletar_aluno(rgm: int):
    """Remove o aluno e também o usuário vinculado a ele."""    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM alunos WHERE rgm = ?",
                (rgm,)
            )
            resultado = cursor.fetchone()

            if not resultado:
                print(f"Nenhum aluno encontrado com RGM {rgm}.")
                return

            aluno_id = resultado[0]

            cursor.execute(
                "DELETE FROM usuarios WHERE aluno_id = ?",
                (aluno_id,)
            )

            cursor.execute(
                "DELETE FROM alunos WHERE id = ?",
                (aluno_id,)
            )

            print(f"Aluno de RGM {rgm} e seu usuário foram removidos com sucesso.")

    except Exception as e:
        print(f"Erro: {e}")


def obter_alunos():
    """Retorna como dados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alunos')
        return cursor.fetchall()


def exibir_alunos(dados_alunos):
    """Exibe os alunos formatados"""
    print("\n---- LISTA DE ALUNOS ----\n")
    if not dados_alunos:
        print("Nenhum aluno cadastrado no sistema.")
    else:
        for _, rgm, nome, sobrenome, email, curso in dados_alunos:
            print(f"RGM: {rgm} | {nome} {sobrenome}\nemail: {email} | {curso}\n")
    print("--" * 15)


def obter_rgm_por_id(aluno_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT rgm
        FROM alunos
        WHERE id = ?
        """, (aluno_id,))

        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]


def area_aluno(usuario):

    rgm = obter_rgm_por_id(
        usuario["aluno_id"]
    )

    while True:
        menu_aluno()
        opcao = input("Escolha: ")

        if opcao == "1":
            consultar_notas_aluno(rgm)
            pausar()

        elif opcao == "0":
            break

        print("Opção inválida, tente novamente.")
