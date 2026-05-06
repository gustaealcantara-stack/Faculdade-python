from database import inicializar_db

from services.admin import area_admin

from interface.utils import limpar_terminal, tela_login

from models.aluno import area_aluno
from models.professor import area_professor


def main():
    inicializar_db()

    while True:
        usuario = tela_login()

        if usuario:
            limpar_terminal()
            print("Login realizado com sucesso!")
            print(f"Perfil: {usuario['perfil']}")

            if usuario["perfil"] == "admin":
                area_admin()

            elif usuario["perfil"] == "professor":
                area_professor(usuario)

            elif usuario["perfil"] == "aluno":
                area_aluno(usuario)

            break

        else:
            print("Email ou senha inválidos.")
            tentar = input("Deseja tentar novamente? (s/n): ")

            if tentar.lower() != "s":
                print("Encerrando o sistema...")
                break


if __name__ == "__main__":
    main()
