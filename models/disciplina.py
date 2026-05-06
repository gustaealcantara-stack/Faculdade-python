from database import get_connection


def gerar_codigo_disciplina(nome: str):
    """Gera o código tipo BD001 baseado no nome da disciplina."""

    if not nome.strip():
        raise ValueError("Nome da disciplina não pode ser vazio")

    # pega a str e transforma em uma lista de str separada
    # Ex.: Banco de dados -> palavras = ["Banco", "de", "Dados"]
    palavras = nome.split()

    # evita de pegar as conjuções
    ignorar = ["de", "da","do", "das", "dos", "para"]
    iniciais = list()

    for p in palavras:
        if p.lower() not in ignorar:
            iniciais.append(p[0].upper())
    
    # garante pelo menos 2 letras
    if len(iniciais) >= 2:
        sigla = "".join(iniciais[:2]) # pega as duas iniciais da primeira e segunda palavra
    else:
        sigla = palavras[0][:2].upper() # pega a primeira e segunda letra da palavra

    
    # Cria um contador para gerar o código da disciplina
    # Ex.: Banco de Dados Introdutorio -> BD001
    # Banco de Dados Avançado -> testa BD001, se existir, passa para o próximo BD002
    with get_connection() as conn:
        cursor = conn.cursor()

        contador = 1
        
        while True:
            codigo = f"{sigla}{contador:03d}"

            cursor.execute(
                "SELECT 1 FROM disciplinas WHERE codigo = ?",
                (codigo,)
            )

            if not cursor.fetchone():
                return codigo

            contador += 1


def inserir_disciplina(nome: str):
    """Insere uma nova disciplina no banco de dados"""
    codigo = gerar_codigo_disciplina(nome)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO disciplinas (nome, codigo) VALUES (?, ?)",
                (nome, codigo)
            )

            print(f"Disciplina cadastrada! Código: {codigo}")

    except Exception as e:
        print(f"Erro ao inserir disciplina: {e}")


def editar_disciplina(novo_nome: str, codigo: str):
    """Edita o nome de uma disciplina a partir do código."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE disciplinas SET nome = ? WHERE codigo = ?",
                (novo_nome, codigo)
            )

            if cursor.rowcount > 0:
                print("Disciplina atualizada com sucesso!")
            else:
                print("Código não encontrado.")

    except Exception as e:
        print(f"Erro: {e}")


def deletar_disciplina(codigo: str):
    """Remove uma disciplina pelo código."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM disciplinas WHERE codigo = ?", (codigo,))

            if cursor.rowcount > 0:
                print("Disciplina removida.")
            else:
                print("Código não encontrado.")

    except Exception as e:
        print(f"Erro: {e}")


def obter_disciplinas():
    """Retorna as disciplinas cadastradas."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, codigo FROM disciplinas")
        return cursor.fetchall()
    

def exibir_disciplinas(dados):
    print("\n---- LISTA DE DISCIPLINAS ----\n")

    if not dados:
        print("Nenhuma disciplina cadastrada.")
    else:
        for _, nome, codigo in dados:
            print(f"Código: {codigo} | {nome}")

    print("--" * 15)