from database import excluir_todas_tabelas, inicializar_db

from interface.utils import limpar_terminal, pausar, extrair_primeiro_nome, extrair_sobrenome
from interface.menus import menu_admin, menu_alunos, menu_professores, menu_disciplinas, exibir_professores, exibir_disciplinas, exibir_alunos

from models.aluno import inserir_aluno, obter_alunos, editar_aluno, deletar_aluno
from models.professor import inserir_professor, obter_professores, editar_professor, deletar_professor
from models.disciplina import inserir_disciplina, obter_disciplinas, editar_disciplina, deletar_disciplina

from services.notas import vincular_aluno_disciplina


# Lista de cursos aceitos pelo sistema
CURSOS_PERMITIDOS = ("CCP", "ADS", "GTI", "EC", "SI")


def area_admin() -> None:
    """
    Exibe e controla o menu principal da área administrativa.

    Esta função centraliza o gerenciamento do sistema, permitindo:

    1. Gerenciar alunos.
    2. Gerenciar professores.
    3. Gerenciar disciplinas.
    4. Limpar o terminal.
    5. Excluir todas as tabelas e recriar o banco de dados.
    0. Encerrar o sistema.

    Returns:
        None
    """

    while True:
        menu_admin()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Acessa o submenu de gerenciamente de alunos
            limpar_terminal()
            gerenciar_alunos()

        elif opcao == "2":
            # Acessa o submenu de gerenciamento de professores
            limpar_terminal()
            gerenciar_professores()

        elif opcao == "3":
            # Acessa o submenu de gerenciamento de disciplinas
            limpar_terminal()
            gerenciar_disciplinas()

        elif opcao == "4":
            # Limpa o terminal
            limpar_terminal()

        elif opcao == "5":
            # Apaga todas as tabelas do banco de dados e
            # solicita confirmação antes de apagar
            confirmacao = input(
                "Tem certeza que deseja excluir TODAS as tabelas? (s/n): "
            ).strip()[:1]

            if confirmacao.lower() == "s":
                # Remoce todas as tabelas e recria a estrutura do banco de dados
                excluir_todas_tabelas()
                inicializar_db()
                print("Banco recriado.")
            else:
                print("Cancelado.")

            pausar()

        elif opcao == "0":
            # Encerra o sistema
            print("Encerrando o sistema...")
            break

        else:
            # Trata opções inválidas
            print("Opção inválida.")
            pausar()


def permitir_curso(curso: str) -> bool:
    """
    Valida se o curso informado está entre os cursos permitidos no sistema.

    Os cursos válidos são definidos internamente pela lista:
    - CCP -> Ciência da Computação
    - ADS -> Análise e Desenvolvimento de Sistemas 
    - GTI -> Gestão da Tecnologia da Informação
    - EC -> Engenharia de Computação
    - SI -> Sistemas de Informação 

    Args:
        curso (str): Código do curso informado pelo usuário.

    Returns:
        bool:
            - True: caso o curso seja válido
            - False: caso o curso não esteja na lista permitida
    """

    # Verifica se o curso está na lista permitida
    if curso in CURSOS_PERMITIDOS:
        return True
    
    # Informa os cursos válidos caso seja inválido
    print(f"Curso inválido! Cursos permitidos: {', '.join(CURSOS_PERMITIDOS)}")
    return False
    

def gerenciar_alunos() -> None:
    """
    Menu principal de gerenciamento de alunos.

    Permite executar operações básicas do sistema de alunos, como:
    - cadastro de aluno;
    - listagem de alunos;
    - edição de dados;
    - vinculação com disciplinas e professores;
    - exclusão de aluno.

    O fluxo permanece em loop até o usuário escolher sair.

    Returns:
        None
    """
    
    while True:    
        menu_alunos()
    
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = extrair_primeiro_nome(input("Nome: "))
            sobrenome = extrair_sobrenome(input("Sobrenome: "))
            curso = input("Curso: ").upper().strip()

            if permitir_curso(curso):
                inserir_aluno(nome, sobrenome, curso)
            else:
                print("Opção inválida.")

            pausar()

        elif opcao == "2":
            limpar_terminal()
            alunos = obter_alunos()
            exibir_alunos(alunos)
            pausar()

        elif opcao == "3":
            rgm = int(input("Digite o RGM do aluno: "))
            novo_nome = extrair_primeiro_nome(input("Novo nome: "))           
            novo_sobrenome = extrair_sobrenome(input("Novo sobrenome: "))
            novo_curso = input("Curso: ")
            novo_curso = novo_curso.upper().strip()

            if permitir_curso(novo_curso):
                editar_aluno(novo_nome, novo_sobrenome, novo_curso, rgm)
            else:
                print("Opção inválida.")
                
            pausar()

        elif opcao == "4":
            rgm = int(input("RGM do aluno: "))
            codigo = input("Código disciplina: ").upper()
            registro = int(input("Registro professor: "))
            
            
            vincular_aluno_disciplina(
                rgm,
                codigo,
                registro
            )
            
            pausar()

        elif opcao == "5":
            rgm = int(input("Digite o RGM do aluno: "))
            confirmacao = input(
                f"Tem certeza que deseja excluir o aluno de RGM {rgm}? (s/n): "
                ).strip()[:1]


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


def gerenciar_professores() -> None:
    """
    Menu principal de gerenciamento de professores.

    Permite realizar operações básicas no sistema, como:
    - cadastro de professores;
    - listagem de professores;
    - edição de dados;
    - exclusão de professores.

    O fluxo permanece em loop até o usuário optar por sair.

    Returns:
        None
    """

    while True:
        menu_professores()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = extrair_primeiro_nome(input("Nome: "))
            sobrenome = extrair_sobrenome(input("Sobrenome: "))
            inserir_professor(str(nome), str(sobrenome))
            pausar()

        elif opcao == "2":
            limpar_terminal()
            professores = obter_professores()
            exibir_professores(professores)
            pausar()

        elif opcao == "3":
            registro = int(input("Digite o registro do professor: "))
            novo_nome = extrair_primeiro_nome(input("Novo nome: "))
            novo_sobrenome = extrair_sobrenome(input("Novo sobrenome: "))

            editar_professor(novo_nome, novo_sobrenome, registro)
            pausar()

        elif opcao == "4":
            registro = int(input("Digite o registro do professor: "))
            confirmacao = input(
                f"Tem certeza que deseja excluir o professor de registro {registro}? (s/n): "
            ).strip()[:1]

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
    """
    Menu principal de gerenciamento de disciplinas.

    Permite executar operações básicas do sistema, como:
    - cadastro de disciplinas;
    - listagem de disciplinas;
    - edição de disciplinas;
    - exclusão de disciplinas.

    O fluxo permanece em loop até o usuário escolher sair.

    Returns:
        None
    """
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
            ).strip()[:1]

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