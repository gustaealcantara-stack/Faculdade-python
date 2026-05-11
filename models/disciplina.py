from database import get_connection


def gerar_codigo_disciplina(nome: str)-> str:
    """
    Gera um código único para disciplina no formato SIGLA + número sequencial.

    A sigla é formada pelas iniciais das palavras relevantes do nome da disciplina,
    ignorando conectivos comuns (ex: "de", "da", "do", "e").

    Exemplo:
        "Banco de Dados" → BD001, BD002, ...

    Regras:
    - Se o nome estiver vazio, uma exceção é lançada
    - A sigla usa até 2 iniciais significativas
    - O código final é incrementado até encontrar um valor livre no banco

    Args:
        nome (str): Nome da disciplina

    Returns:
        str:
            - Código gerado no formato ``SIGLA + 3 dígitos`` (ex: BD001)
    """

    if not nome.strip():
        raise ValueError("Nome da disciplina não pode ser vazio")

    # pega a str e transforma em uma lista de str separada
    # Ex.: Banco de dados -> palavras = ["Banco", "de", "Dados"]
    palavras = nome.split()

    # Filtra palavras irrelevantes 
    ignorar = ["de", "da","do", "das", "dos", "para", "e"]
    
    # Lista de iniciais que formarão a sigla
    iniciais = list()

    # Extrai iniciais das palavras relevantes
    for p in palavras:
        if p.lower() not in ignorar:
            iniciais.append(p[0].upper())
    
    # garante uma sigla de até 2 letras
    if len(iniciais) >= 2:
        sigla = "".join(iniciais[:2]) 
    else:
        # Caso tenha apenas uma palavra significativa
        sigla = palavras[0][:2].upper() 

    
    # Cria um contador para gerar o código da disciplina
    # Ex.: Banco de Dados Introdutorio -> BD001
    # Banco de Dados Avançado -> testa BD001, se existir,
    # passa para o próximo BD002
    with get_connection() as conn:
        cursor = conn.cursor()

        contador = 1
        
        while True:
            # Monta código final (ex: BD001)
            codigo = f"{sigla}{contador:03d}"

            # Verifica se já existe no banco
            cursor.execute(
                "SELECT 1 FROM disciplinas WHERE codigo = ?",
                (codigo,)
            )
            
            # Se não existir, retorna o código
            if not cursor.fetchone():
                return codigo

            contador += 1


def inserir_disciplina(nome: str) -> None:
    """
    Insere uma nova disciplina no banco de dados.

    O código da disciplina é gerado automaticamente com base no nome,
    utilizando a função ``gerar_codigo_disciplina``.

    Args:
        nome (str): Nome da disciplina

    Returns:
        None
    """

    # Gera código único para a disciplina
    codigo = gerar_codigo_disciplina(nome)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Insere disciplina na tabela
            cursor.execute(
                "INSERT INTO disciplinas (nome, codigo) VALUES (?, ?)",
                (nome, codigo)
            )

            print(f"Disciplina cadastrada! Código: {codigo}")

    except Exception as e:
        print(f"Erro ao inserir disciplina: {e}")


def editar_disciplina(novo_nome: str, codigo: str) -> None:
    """
    Atualiza o nome de uma disciplina com base no seu código.

    A busca é feita pelo código da disciplina, que deve ser único.

    Args:
        novo_nome (str): Novo nome da disciplina
        codigo (str): Código identificador da disciplina

    Returns:
        None
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Atualiza o nome da disciplina correspondente ao código informado
            cursor.execute(
                "UPDATE disciplinas SET nome = ? WHERE codigo = ?",
                (novo_nome, codigo)
            )

            # Verifica se algum registro foi alterado
            if cursor.rowcount > 0:
                print("Disciplina atualizada com sucesso!")
            else:
                print("Código não encontrado.")

    except Exception as e:
        print(f"Erro: {e}")


def deletar_disciplina(codigo: str) -> None:
    """
    Remove uma disciplina do banco de dados com base no código informado.

    Antes de excluir a disciplina, também são removidos todos os registros
    vinculados na tabela ``notas``, garantindo integridade dos dados.

    Args:
        codigo (str): Código identificador da disciplina

    Returns:
        None
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Remove espaços em branco extras do código informado
            codigo = codigo.strip().upper()

            # Busca o ID interno da disciplina a partir do código
            cursor.execute("""
                SELECT id
                FROM disciplinas
                WHERE codigo = ?
            """, (codigo,))

            resultado = cursor.fetchone()

             # Verifica se a disciplina existe
            if not resultado:
                print(f"Nenhuma disciplina encontrada com código {codigo}.")
                return

            disciplina_id = resultado[0]

            # Remove todos os registros de notas vinculados à disciplina
            cursor.execute("""
                DELETE FROM notas
                WHERE disciplina_id = ?
            """, (disciplina_id,))

            # Remove a disciplina da tabela principal
            cursor.execute("""
                DELETE FROM disciplinas
                WHERE id = ?
            """, (disciplina_id,))

            print(f"Disciplina {codigo} removida com sucesso.")

    except Exception as e:
        print(f"Erro: {e}")


def obter_disciplinas() -> list[tuple]:
    """
    Retorna todas as disciplinas cadastradas no banco de dados.

    A consulta retorna os principais dados da tabela ``disciplinas``.

    Returns:
        list[tuple]:
            Lista de disciplinas cadastradas, onde cada registro contém:
            - id (int)
            - nome (str)
            - codigo (str)
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, codigo FROM disciplinas")
        return cursor.fetchall()
