from database import inicializar_db

from services.admin import area_admin

from interface.utils import limpar_terminal, tela_login

from models.aluno import area_aluno
from models.professor import area_professor


def main():
    """
    Função principal do sistema.
    """

    # Inicializa o banco de dados
    inicializar_db()

    while True:
        usuario = tela_login()

        # Verifica se o login foi realizado com sucesso
        if usuario:
            limpar_terminal()

            print("Login realizado com sucesso!")
            print(f"Perfil: {usuario['perfil']}")

            # Direciona o usuário conforme o perfil logado
            if usuario["perfil"] == "admin":
                area_admin()

            elif usuario["perfil"] == "professor":
                area_professor(usuario)

            elif usuario["perfil"] == "aluno":
                area_aluno(usuario)

            # Após sair da área correspondente, encerra o programa.
            break

        else:
            print("Email ou senha inválidos.")
            tentar = input("Deseja tentar novamente? (s/n): ").strip().lower()[:1]

            # Encerra o sistema caso a resposta seja diferente de "s"
            if tentar.lower() != "s":
                print("Encerrando o sistema...")
                break


if __name__ == "__main__":
    main()
