def menu_admin():
    print("\n===== MENU ADMIN =====")
    """Exibe o menu principal para administrador."""
    print("1 - Gerenciar alunos")
    print("2 - Gerenciar professores")
    print("3 - Gerenciar disciplinas")
    print("4 - Limpar terminal")
    print("5 - Excluir todas as tabelas")
    print("0 - Sair")
    print("=" * 29)


def menu_alunos():
    """Exibe o menu de alunos para administradores."""
    print("\n===== MENU ALUNOS =====")
    print("1 - Cadastrar aluno")
    print("2 - Listar alunos")
    print("3 - Editar aluno")
    print("4 - Vincular aluno à disciplina")
    print("5 - Deletar aluno")
    print("0 - Voltar")
    print("=" * 29)


def menu_professores():
    """Exibe o menu de professores para administradores."""
    print("\n===== MENU PROFESSORES =====")
    print("1 - Cadastrar professor")
    print("2 - Listar professores")
    print("3 - Editar professor")
    print("4 - Deletar professor")
    print("0 - Voltar")
    print("=" * 29)


def menu_disciplinas():
    """Exibe o menu de disciplinas para administradores."""
    print("\n===== MENU DISCIPLINAS =====")
    print("1 - Cadastrar disciplina")
    print("2 - Listar disciplinas")
    print("3 - Editar disciplina")
    print("4 - Deletar disciplina")
    print("0 - Voltar")
    print("=" * 29)


def menu_professor():
    """Exibe o menu do professor. Apenas para Professores"""
    print("\n===== ÁREA PROFESSOR =====")
    print("1 - Lançar/Atualizar notas")
    print("2 - Consultar notas dos alunos")
    print("0 - Sair")
    print("=" * 30)


def menu_aluno():
    """Exibe o menu do aluno. Apenas para Alunos"""
    print("\n===== ÁREA ALUNO =====")
    print("1 - Consultar minhas notas")
    print("0 - Sair")


def exibir_professores(dados_professor: list[tuple]) -> None:
    """
    Exibe no terminal a lista de professores cadastrados no sistema.

    A função recebe os dados retornados pela consulta ao banco de dados
    e os apresenta de forma organizada no console.

    Estrutura esperada de cada registro:
        (id, registro_professor, nome, sobrenome, email)

    Comportamento:
    - Se não houver dados, exibe uma mensagem informando que não há
      professores cadastrados.
    - Caso existam registros, percorre a lista e imprime as informações
      principais de cada professor.

    Args:
        dados_professor (list[tuple]):
            Lista de tuplas contendo os dados dos professores.

    Returns:
        None
    """

    print("\n---- LISTA DE PROFESSORES ----\n")

    # Verifica se há dados retornados da consulta
    if not dados_professor:
        print("Nenhum professor cadastrado.")
    else:
        # Percorre cada professor ignorando o ID interno
        for _, registro_professor, nome, sobrenome, email in dados_professor:
            print(f"Registro: {registro_professor} | {nome} {sobrenome}")
            print(f"Email: {email}\n")

    print("--" * 15)


def exibir_disciplinas(dados: list[tuple]) -> None:
    """
    Exibe a lista de disciplinas formatada no terminal.

    Args:
        dados (list[tuple]):
            Lista de disciplinas no formato (id, nome, codigo),
            geralmente vinda de uma consulta SQL.

    Returns:
        None
    """

    print("\n---- LISTA DE DISCIPLINAS ----\n")

    if not dados:
        print("Nenhuma disciplina cadastrada.")
    else:
        for _, nome, codigo in dados:
            print(f"Código: {codigo} | {nome}")

    print("--" * 15)


def exibir_alunos(dados_alunos: list[tuple]) -> None:
    """
    Exibe a lista de alunos formatada no terminal.

    A função recebe os dados já buscados no banco e apenas
    organiza a saída para visualização.

    Args:
        dados_alunos (list[tuple]):
            Lista de alunos no formato retornado pelo SQLite,
            geralmente contendo (id, rgm, nome, sobrenome, email, curso).

    Returns:
        None:
            A função não retorna valores, apenas imprime os dados
            formatados no terminal.
    """

    print("\n---- LISTA DE ALUNOS ----\n")

    # Caso não exista nenhum aluno cadastrado
    if not dados_alunos:
        print("Nenhum aluno cadastrado no sistema.")
    else:
        # Desempacota cada registro do banco de dados
        for _, rgm, nome, sobrenome, email, curso in dados_alunos:
            print(f"RGM: {rgm} | {nome} {sobrenome}\nemail: {email} | {curso}\n")
    print("--" * 15)

