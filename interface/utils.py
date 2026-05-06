import os

from models.usuario import autenticar_usuario


def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """
    Utilizada para manter o menu ou a saída visível antes de continuar.
    """
    input("\nPressione ENTER para continuar...")


def tela_login():
    print("\n===== LOGIN =====")
    email = input("Email: ")
    senha = input("Senha: ")

    usuario = autenticar_usuario(email, senha)

    if usuario:
        return {
            "id": usuario[0],
            "email": usuario[1],
            "perfil": usuario[2],
            "aluno_id": usuario[3],
            "professor_id": usuario[4]
        }

    return None