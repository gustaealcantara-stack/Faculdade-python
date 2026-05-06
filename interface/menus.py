def menu_admin():
    print("\n===== MENU ADMIN =====")
    """Exibe o menu principal para administrador."""
    print("1 - Gerenciar alunos")
    print("2 - Gerenciar professores")
    print("3 - Gerenciar disciplinas")
    print("4 - Matricular aluno")
    print("5 - Excluir todas as tabelas")
    print("6 - Limpar terminal")
    print("0 - Sair")
    print("=" * 29)


def menu_alunos():
    """Exibe o menu de alunos para administradores."""
    print("\n===== MENU ALUNOS =====")
    print("1 - Cadastrar aluno")
    print("2 - Listar alunos")
    print("3 - Editar aluno")
    print("4 - Deletar aluno")
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
