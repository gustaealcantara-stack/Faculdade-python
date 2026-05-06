from database import excluir_todas_tabelas, inicializar_db

from interface.utils import limpar_terminal, pausar
from interface.menus import menu_admin, menu_alunos, menu_professores, menu_disciplinas

from models.aluno import inserir_aluno, obter_alunos, exibir_alunos, editar_aluno, deletar_aluno
from models.professor import inserir_professor, obter_professores, exibir_professores, editar_professor, deletar_professor
from models.disciplina import inserir_disciplina, obter_disciplinas, exibir_disciplinas, editar_disciplina, deletar_disciplina

from services.notas import matricular_aluno


def area_admin():
    while True:
        menu_admin()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            limpar_terminal()
            gerenciar_alunos()

        elif opcao == "2":
            limpar_terminal()
            gerenciar_professores()

        elif opcao == "3":
            limpar_terminal()
            gerenciar_disciplinas()

        elif opcao == "4":
            rgm = int(input("RGM do aluno: "))
            codigo = input("Código disciplina: ")
            registro = int(input("Registro professor: "))

            matricular_aluno(
                rgm,
                codigo,
                registro
            )

            pausar()

        elif opcao == "5":
            confirmacao = input(
                "Tem certeza que deseja excluir TODAS as tabelas? (s/n): "
            )

            if confirmacao.lower() == "s":
                excluir_todas_tabelas()
                inicializar_db()
                print("Banco recriado.")
            else:
                print("Cancelado.")

            pausar()

        elif opcao == "6":
            limpar_terminal()

        elif opcao == "0":
            print("Encerrando o sistema...")
            break

        else:
            print("Opção inválida.")
            pausar()


def gerenciar_alunos():
    while True:
        menu_alunos()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome =str(input("Nome:"))
            sobrenome =str(input("Sobrenome:"))
            curso =str(input("curso:"))

            inserir_aluno(nome, sobrenome, curso)
            pausar()

        elif opcao == "2":
            limpar_terminal()
            alunos = obter_alunos()
            exibir_alunos(alunos)
            pausar()

        elif opcao == "3":
            rgm = int(input("Digite o RGM do aluno: "))
            novo_nome = input("Novo nome: ")
            novo_sobrenome = input("Novo sobrenome: ")
            novo_curso = input("Novo curso: ")

            editar_aluno(novo_nome, novo_sobrenome, novo_curso, rgm)
            pausar()

        elif opcao == "4":
            rgm = int(input("Digite o RGM do aluno: "))
            confirmacao = input(f"Tem certeza que deseja excluir o aluno de RGM {rgm}? (s/n): ")

            if confirmacao.lower() == "s":
                deletar_aluno(rgm)
            else:
                print("Operação cancelada.")

            pausar()

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")
            pausar()


def gerenciar_professores():
    while True:
        menu_professores()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome: ")
            sobrenome = input("Sobrenome: ")

            inserir_professor(nome, sobrenome)
            pausar()

        elif opcao == "2":
            limpar_terminal()
            professores = obter_professores()
            exibir_professores(professores)
            pausar()

        elif opcao == "3":
            registro = int(input("Digite o registro do professor: "))
            novo_nome = input("Novo nome: ")
            novo_sobrenome = input("Novo sobrenome: ")

            editar_professor(novo_nome, novo_sobrenome, registro)
            pausar()

        elif opcao == "4":
            registro = int(input("Digite o registro do professor: "))
            confirmacao = input(
                f"Tem certeza que deseja excluir o professor de registro {registro}? (s/n): "
            )

            if confirmacao.lower() == "s":
                deletar_professor(registro)
            else:
                print("Operação cancelada.")

            pausar()

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")
            pausar()


def gerenciar_disciplinas():
    while True:
        menu_disciplinas()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome da disciplina: ")

            inserir_disciplina(nome)
            pausar()

        elif opcao == "2":
            limpar_terminal()
            disciplinas = obter_disciplinas()
            exibir_disciplinas(disciplinas)
            pausar()

        elif opcao == "3":
            codigo = input("Digite o código da disciplina: ")
            novo_nome = input("Novo nome da disciplina: ")

            editar_disciplina(novo_nome, codigo)
            pausar()

        elif opcao == "4":
            codigo = input("Digite o código da disciplina: ")
            confirmacao = input(
                f"Tem certeza que deseja excluir a disciplina {codigo}? (s/n): "
            )

            if confirmacao.lower() == "s":
                deletar_disciplina(codigo)
            else:
                print("Operação cancelada.")

            pausar()

        elif opcao == "0":
            break

        else:
            print("Opção inválida.")
            pausar()