import random
from database import get_connection


from interface.utils import pausar, limpar_terminal, remover_acentos
from interface.menus import menu_professor

from services.notas import inserir_ou_atualizar_notas, consultar_notas_professor, calcular_media


def gerar_registro_professor() -> int:
    """
    Gera um número de registro único para um professor.

    O registro é composto por 5 dígitos aleatórios, no intervalo
    de 10000 a 99999. Antes de retornar o valor, a função consulta
    a tabela ``professores`` para garantir que o número ainda não
    esteja em uso.

    O processo é repetido até que um registro exclusivo seja
    encontrado.

    Returns:
        int: Número de registro do professor.
    """
    while True:
        # Gera um número aleatório de 5 dígitos.
        registro_professor = random.randint(10_000, 99_999)

        with get_connection() as conn:
            cursor = conn.cursor()

             # Verifica se já existe um professor com esse registro.
            cursor.execute("""
                    SELECT 1 
                    FROM professores 
                    WHERE registro_professor = ?
                    """, (registro_professor,))

            # Se nenhum registro for encontrado, o número é único.
            if not cursor.fetchone():
                return registro_professor


def gerar_email_professor(
    nome: str, 
    sobrenome: str, 
    registro_professor: int
    ) -> str:
    """
    Gera o e-mail institucional de um professor

    O formato utilizado é:
        nome.sobrenomeXXX@prof.cruzeirodosul.edu.br

    Onde:
    - nome e sobrenome são convertidos para minúsculas
    - acentos são removidos
    - XXX corresponde aos 3 últimos dígitos do registro do professor

    O uso dos 3 últimos dígitos do registro ajuda a evitar conflitos
    quando dois professores possuem o mesmo nome e sobrenome

    Exemplo:
        nome = "João"
        sobrenome = "Silva"
        registro_professor = 12345

        Resultado:
        joao.silva345@prof.cruzeirodosul.edu.br

    Args:
        nome (str): Primeiro nome do professor
        sobrenome (str): Sobrenome principal do professor
        registro_professor (int): Número de registro do professor

    Returns:
        str: E-mail institucional gerado
    """

    # Monta o e-mail no formato:
    # nome.sobrenomeXXX@prof.cruzeirodosul.edu.br
    # onde XXX são os 3 últimos dígitos do registro.
    email = (
        f"{remover_acentos(nome)}."
        f"{remover_acentos(sobrenome)}"
        f"{str(registro_professor)[-3:]}"
        "@prof.cruzeirodosul.edu.br"
        ).lower()
    
    return email


def inserir_professor(nome: str, sobrenome: str) -> None:
    """
    Cadastra um novo professor no sistema e cria seu usuário de acesso.

    O processo de cadastro realiza as seguintes etapas:
    1. Gera um número de registro único para o professor.
    2. Gera automaticamente o e-mail institucional.
    3. Define a senha inicial com os 4 primeiros dígitos do registro.
    4. Insere o professor na tabela ``professores``.
    5. Cria um usuário na tabela ``usuarios`` com o perfil
       ``"professor"`` e vincula esse usuário ao professor cadastrado.

    Ao final, são exibidos na tela:
    - número de registro;
    - e-mail institucional;
    - senha inicial.

    Args:
        nome (str): Primeiro nome do professor.
        sobrenome (str): Sobrenome principal do professor.

    Returns:
        None
    """

    # Gera um número de registro único para o professor
    registro_professor = gerar_registro_professor()

    # Gera automaticamente o e-mail institucional
    email = gerar_email_professor(nome, sobrenome, registro_professor)

    # Define a senha utilizando os 4 primeiros dígitos do registro
    senha = str(registro_professor)[:4]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            dados_professor = (registro_professor, nome, sobrenome, email)

            # Insere professores na tabela de professores
            cursor.execute(
                """INSERT INTO professores (
                    registro_professor, 
                    nome, 
                    sobrenome, 
                    email
                    ) 
                    VALUES (?, ?, ?, ?)
                    """, dados_professor
                )

            # Recupera o ID gerado automaticamente para 
            # relacionar com a tabela de usuários
            professor_id = cursor.lastrowid

            # Cria o usuário com perfil "professor"
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


def editar_professor(
    novo_nome: str, 
    novo_sobrenome: str, 
    registro_professor: int
    ) -> None:
    """
    Atualiza os dados cadastrais de um professor no sistema.

    A função realiza a atualização das seguintes informações:
    - nome;
    - sobrenome;
    - e-mail institucional (recalculado com base no novo nome).

    O e-mail é automaticamente regenerado seguindo o padrão institucional
    da aplicação, utilizando o registro do professor para manter
    consistência e evitar duplicidades.

    A atualização é feita com base no ``registro_professor``.

    Args:
        novo_nome (str): Novo primeiro nome do professor.
        novo_sobrenome (str): Novo sobrenome do professor.
        registro_professor (int): Número de registro do professor.

    Returns:
        None
    """
    # Gera novo e-mail com base nos dados atualizados.
    novo_email = gerar_email_professor(
        novo_nome, 
        novo_sobrenome, 
        registro_professor
    )

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Atualiza os dados do professor com base no registro
            cursor.execute("""
            UPDATE professores
            SET nome = ?,
                sobrenome = ?,
                email = ?
            WHERE registro_professor = ?
            """, (
                novo_nome, 
                novo_sobrenome, 
                novo_email, 
                registro_professor
            ))
           
            if cursor.rowcount > 0:
                print("Professor atualizado com sucesso!")
            else:
                print("Registro não encontrado.")

    except Exception as e:
        print(f"Erro: {e}")


def deletar_professor(registro_professor: int) -> None:
    """
    Remove um professor do sistema e todos os registros associados a ele.

    A exclusão é feita de forma encadeada para garantir a integridade
    referencial do banco de dados, removendo primeiro os registros
    dependentes antes do professor principal

    Ordem de remoção:
    1. Registros da tabela ``notas`` vinculados ao professor
       (inclui alunos, disciplinas, notas e faltas).
    2. Usuário associado na tabela ``usuarios``.
    3. Registro do professor na tabela ``professores``.

    A operação é baseada no ``registro_professor``, que é convertido
    internamente para o ID primário da tabela.

    Args:
        registro_professor (int): Número de registro do professor.

    Returns:
        None
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Localiza o ID interno do professor a partir do registro
            cursor.execute("""
                SELECT id
                FROM professores
                WHERE registro_professor = ?
            """, (registro_professor,))
            resultado = cursor.fetchone()

            # Verifica se o professor existe no banco
            if not resultado:
                print(
                    f"Nenhum professor encontrado com registro "
                    f"{registro_professor}."
                )
                return

            professor_id = resultado[0]

            # Remove os registros de notas vinculados ao professor
            cursor.execute("""
                DELETE FROM notas
                WHERE professor_id = ?
            """, (professor_id,))

            # Remove o usuário associado ao professor
            cursor.execute("""
                DELETE FROM usuarios
                WHERE professor_id = ?
            """, (professor_id,))

            # Remove o professor da tabela principal
            cursor.execute("""
                DELETE FROM professores
                WHERE id = ?
            """, (professor_id,))

            print(
                f"Professor de registro {registro_professor} e todos os "
                "registros relacionados foram removidos com sucesso."
            )

    except Exception as e:
        print(f"Erro: {e}")


def obter_professores() -> list[tuple]:
    """
    Recupera todos os registros da tabela de professores.

    Esta função realiza uma consulta simples no banco de dados
    e retorna todos os professores cadastrados no sistema,
    incluindo todas as colunas da tabela.

    Returns:
        list[tuple]:
            Lista de tuplas contendo os dados dos professores.
            Cada tupla representa um professor no formato da tabela
            ``professores``.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professores')
        
        # Retorna todos os resultados encontrados.
        return cursor.fetchall()


def obter_registro_por_id(professor_id) -> int | None:
    """
    Busca o registro do professor a partir do ID interno.

    Esta função realiza uma consulta na tabela ``professores`` para
    recuperar o ``registro_professor`` correspondente ao ID informado.

    Caso o professor exista, retorna apenas o número de registro.
    Caso contrário, retorna ``None``.

    Args:
        professor_id (int): ID interno do professor na base de dados.

    Returns:
        int | None:
            - int: número de registro do professor encontrado
            - None: caso não exista professor com o ID informado
    """

    with get_connection() as conn:
        cursor = conn.cursor()

        # Busca o registro do professor pelo ID interno
        cursor.execute("""
            SELECT registro_professor
            FROM professores
            WHERE id = ?
        """, (professor_id,))

        # Executa a consulta e tenta obter um único resultado
        resultado = cursor.fetchone()
        
        # Retorna o registro se encontrado, senão None
        if resultado:
            return resultado[0]

        return None
    

def area_professor(usuario) -> None:
    """
    Área principal do professor no sistema.

    Responsável pelo menu interativo do professor, permitindo:
    - Lançamento de notas
    - Consulta de notas
    - Encerramento da sessão

    Args:
        usuario (dict): Dados do usuário autenticado,
                        contendo pelo menos "professor_id".

    Returns:
        None
    """

    # Obtém o registro do professor a partir do ID interno do usuário
    registro = obter_registro_por_id(
        usuario["professor_id"]
    )

    
    while True:
        menu_professor()
        opcao = input("Escolha uma opção: ")

        # -----------------------------
        # Lançamento ou atualização de notas
        # -----------------------------
        if opcao == "1":

            rgm = int(input("RGM aluno: "))
            codigo = input("Código disciplina: ")

            # Loop de validação das notas A1 e A2
            while True:
                try:
                    # Entrada opcional: ENTER = 0
                    entrada_a1 = input("Nota A1: ").strip()
                    entrada_a2 = input("Nota A2: ").strip()

                    # Conversão segura para float
                    a1 = float(entrada_a1) if entrada_a1 != "" else 0.0
                    a2 = float(entrada_a2) if entrada_a2 != "" else 0.0

                    # Verifica se ambas as notas estão no intervalo permitido
                    if 0 <= a1 <= 5 and 0 <= a2 <= 5:
                        break

                    print("Nota inválida! As notas A1 e A2 devem estar entre 0 e 5.")

                except ValueError:
                    # Caso entrada inválida, zera as notas
                    a1 = 0.0
                    a2 = 0.0
                    print("Entrada inválida detectada. As notas foram consideradas como 0.")
                    break

            # Verifica se o aluno precisa de Avaliação Final (AF)
            # underscore = media
            _, status = calcular_media(a1, a2)

            if status == "AF":
                # Solicita AF somente se a soma de A1 + A2 for menor que 6
                while True:
                    af_input = input("Nota AF (aperte ENTER se não houver): ")

                    # Sem AF
                    if af_input.strip() == "":
                        af = None
                        break
                    
                    # Converte a entrada para float
                    af = float(af_input)

                    # Valida se a nota está entre 0 e 5
                    if 0 <= af <= 5:
                        break

                    print("Nota inválida! A nota AF deve estar entre 0 e 5.")
            else:
               # Aluno aprovado sem necessidade de AF
               af = None 

            # Faltas > 25 retorna status: Reprovado
            # Entrada de faltas do aluno 
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

        # -----------------------------
        # Consulta de notas
        # -----------------------------
        elif opcao == "2":
            limpar_terminal()
            consultar_notas_professor(registro)
            pausar()

        # -----------------------------
        # Encerrar área do professor
        # -----------------------------
        elif opcao == "0":
            break
