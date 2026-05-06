import random
from database import get_connection


from interface.utils import pausar, limpar_terminal
from interface.menus import menu_professor

from services.notas import inserir_ou_atualizar_notas, consultar_notas_professor


def gerar_registro_professor():
    """Gera um registro único paro o professor de 5 dígitos"""
    while True:
        registro_professor = random.randint(10_000, 99_999)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM professores WHERE registro_professor = ?", (registro_professor,))

            if not cursor.fetchone():
                return registro_professor


def gerar_email_professor(nome: str, sobrenome: str, registro_professor: int):
    """
    Gera um email institucional para professor. Também evita 
    que duas pessoas com o mesmo nome e sobrenome tenham emails iguas
    """
    email = f"{nome}.{sobrenome}{str(registro_professor)[-3:]}@prof.cruzeirodosul.edu.br".lower()
    return email


def inserir_professor(nome:str, sobrenome:str):
    registro_professor = gerar_registro_professor()
    email = gerar_email_professor(nome, sobrenome, registro_professor)

    senha = str(registro_professor)[:4]  # primeiros 4 dígitos

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            dados_professor = (registro_professor, nome, sobrenome, email)

            # Insere professores no banco de dados
            cursor.execute(
                "INSERT INTO professores (registro_professor, nome, sobrenome, email) VALUES (?, ?, ?, ?)",
                dados_professor
            )

            professor_id = cursor.lastrowid

            # cria usuário 'professor' na mesma conexão
            cursor.execute("""
                INSERT INTO usuarios (
                    email,
                    senha,
                    perfil,
                    professor_id
                )
                VALUES (?, ?, ?, ?)
            """, (
                email,
                senha,
                "professor",
                professor_id
            ))

            print("Professor cadastrado com sucesso!")
            print(f"Registro: {registro_professor}")
            print(f"Email: {email}")
            print(f"Senha inicial: {senha}")

    except Exception as e:
        print(f"Erro: {e}")


def editar_professor(novo_nome: str, novo_sobrenome: str, registro_professor: int):
    novo_email = gerar_email_professor(novo_nome, novo_sobrenome, registro_professor)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            sql = """
            UPDATE professores
            SET nome = ?,
                sobrenome = ?,
                email = ?
            WHERE registro_professor = ?
            """
            cursor.execute(sql, (novo_nome, novo_sobrenome, novo_email, registro_professor))

            if cursor.rowcount > 0:
                print("Professor atualizado com sucesso!")
            else:
                print("Registro não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")


def deletar_professor(registro_professor: int):
    """Remove o professor e também o usuário vinculado a ele."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # busca o id do professor pelo registro
            cursor.execute(
                "SELECT id FROM professores WHERE registro = ?",
                (registro_professor,)
            )
            resultado = cursor.fetchone()

            if not resultado:
                print(f"Nenhum professor encontrado com registro {registro_professor}.")
                return

            professor_id = resultado[0]

            # remove o usuário vinculado
            cursor.execute(
                "DELETE FROM usuarios WHERE professor_id = ?",
                (professor_id,)
            )

            # remove o professor
            cursor.execute(
                "DELETE FROM professores WHERE id = ?",
                (professor_id,)
            )

            print(f"Professor de registro {registro_professor} e seu usuário foram removidos com sucesso.")

    except Exception as e:
        print(f"Erro: {e}")


def obter_professores():
    """Retorna como dados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professores')
        return cursor.fetchall()


def exibir_professores(dados_professor):
    print("\n---- LISTA DE PROFESSORES ----\n")

    if not dados_professor:
        print("Nenhum professor cadastrado.")
    else:
        for _, registro_professor, nome, sobrenome, email in dados_professor:
            print(f"Registro: {registro_professor} | {nome} {sobrenome}")
            print(f"Email: {email}\n")

    print("--" * 15)


def obter_registro_por_id(professor_id):
    from database import get_connection

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT registro_professor
            FROM professores
            WHERE id = ?
        """, (professor_id,))

        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]

        return None
    

def area_professor(usuario):

    registro = obter_registro_por_id(
        usuario["professor_id"]
    )

    while True:
        menu_professor()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":

            rgm = int(input("RGM aluno: "))
            codigo = input("Código disciplina: ")

            a1 = float(input("Nota A1: "))
            a2 = float(input("Nota A2: "))

            af_input = input("Nota AF (aperte ENTER se não houver): ")

            af = float(af_input) if af_input.strip() != "" else None
            
            faltas = int(input("Faltas: "))

            inserir_ou_atualizar_notas(
                registro,
                rgm,
                codigo,
                a1,
                a2,
                af,
                faltas
            )

            pausar()

        elif opcao == "2":
            limpar_terminal()
            consultar_notas_professor(registro)
            pausar()

        elif opcao == "0":
            break
