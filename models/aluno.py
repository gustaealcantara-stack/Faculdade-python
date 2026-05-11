import sqlite3
import random

from database import get_connection

from interface.menus import menu_aluno
from interface.utils import pausar, remover_acentos

from services.notas import consultar_notas_aluno


def gerar_rgm() -> int:
    """
    Gera um RGM único para alunos.

    O RGM é um número aleatório de 8 dígitos, validado no banco
    para garantir que não haja duplicidade.

    Returns:
        int: RGM único gerado
    """
    while True:
        # gera um numero de 8 digitos
        rgm = random.randint(10_000_000, 99_999_999)

        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se o RGM já existe no banco
            cursor.execute("SELECT 1 FROM alunos WHERE rgm = ?", (rgm,))

            # Se não existir, retorna o RGM gerado
            if not cursor.fetchone():
                return rgm


def gerar_email_aluno(nome:str, sobrenome:str, rgm:int) -> str:
    """
    Gera o e-mail institucional de um aluno

    O formato utilizado é:
        nome.sobrenomeXXX@cs.cruzeirodosul.edu.br

    Onde:
    - nome e sobrenome são convertidos para minúsculas
    - acentos são removidos
    - XXX corresponde aos 3 últimos dígitos do RGM

    O uso dos 3 últimos dígitos do RGM ajuda a evitar conflitos
    quando dois alunos possuem o mesmo nome e sobrenome

    Exemplo:
        nome = "João"
        sobrenome = "Silva"
        rgm = 12345678

        Resultado:
        joao.silva678@cs.cruzeirodosul.edu.br

    Args:
        nome (str): Primeiro nome do aluno
        sobrenome (str): Sobrenome principal do aluno
        rgm (int): Registro Geral de Matrícula do aluno

    Returns:
        str: E-mail institucional gerado.
    """

    # monta o e-mail com identificador único (últimos 3 dígitos do RGM)
    email = (
        f"{remover_acentos(nome)}."
        f"{remover_acentos(sobrenome)}"
        f"{str(rgm)[-3:]}"
        "@cs.cruzeirodosul.edu.br"
        ).lower()
    
    return email


def inserir_aluno(nome:str, sobrenome:str, curso:str):
    """
    Insere um novo aluno no sistema e cria automaticamente seu usuário.

    O processo inclui:
    - geração de um RGM único;
    - geração de e-mail institucional;
    - criação de senha inicial baseada no RGM;
    - inserção na tabela `alunos`;
    - criação do usuário correspondente na tabela `usuarios`.

    Args:
        nome (str): Primeiro nome do aluno.
        sobrenome (str): Sobrenome do aluno.
        curso (str): Curso em que o aluno está matriculado.

    Returns:
        None
    """
    
    # Gera um RGM único para o aluno
    rgm = gerar_rgm()

    # Gera o e-mail institucional baseado no nome e RGM
    email = gerar_email_aluno(nome, sobrenome, rgm)

    # Senha inicial definida pelos 4 primeiros dígitos do RGM
    senha = str(rgm)[:4]
    
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()  
            
            # Dados principais do aluno para inserção
            dados_aluno = (rgm, nome, sobrenome, email, curso)

            # Insere alunos no banco de dados
            cursor.execute("""INSERT INTO alunos (rgm, nome, sobrenome, email, curso) 
                           VALUES (?, ?, ?, ?, ?)
                           """,
                           dados_aluno)

            aluno_id = cursor.lastrowid

            # cria o usuário vinculado ao aluno
            cursor.execute("""
                INSERT INTO usuarios (
                    email,
                    senha,
                    perfil,
                    aluno_id
                )
                VALUES (?, ?, ?, ?)
            """, (
                email,
                senha,
                "aluno",
                aluno_id
            ))

            print("Aluno cadastrado com sucesso!")
            print(f"RGM: {rgm}")
            print(f"Email: {email}")
            print(f"Senha inicial: {senha}")

    except Exception as e:
        print(f"Erro: {e}")


def editar_aluno(
    novo_nome:str, 
    novo_sobrenome:str, 
    novo_curso:str, 
    rgm: int
    ) -> None:
    """
    Atualiza os dados de um aluno e recria seu e-mail institucional.

    A atualização inclui:
    - nome;
    - sobrenome;
    - curso;
    - e-mail (regerado com base no novo nome e sobrenome).

    O RGM é utilizado como identificador único e não pode ser alterado.

    Args:
        novo_nome (str): Novo primeiro nome do aluno.
        novo_sobrenome (str): Novo sobrenome do aluno.
        novo_curso (str): Novo curso do aluno.
        rgm (int): Registro Geral de Matrícula do aluno.

    Returns:
        None
    """
    
    # Recria o e-mail com base nos novos dados
    novo_email = gerar_email_aluno(novo_nome, novo_sobrenome, rgm)
    print(novo_email)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # 1. Buscar ID interno do aluno
            cursor.execute("""
                SELECT id
                FROM alunos
                WHERE rgm = ?
            """, (rgm,))

            resultado = cursor.fetchone()

            if not resultado:
                print(f"Aviso: RGM {rgm} não encontrado para edição.")
                return

            aluno_id = resultado[0]
            
            # 2. Atualizar tabela alunos
            cursor.execute("""
                UPDATE alunos
                SET nome = ?,
                    sobrenome = ?,
                    email = ?,
                    curso = ?
                WHERE rgm = ?
            """, (
                novo_nome,
                novo_sobrenome,
                novo_email,
                novo_curso,
                rgm
            ))

            # 3. Atualizar tabela usuarios
            cursor.execute("""
                UPDATE usuarios
                SET email = ?
                WHERE aluno_id = ?
            """, (novo_email, aluno_id))

            print(f"Sucesso: Aluno do RGM {rgm} atualizado!")
                
    except sqlite3.Error as e:
        print(f"Erro ao editar banco de dados: {e}")


def deletar_aluno(rgm: int) -> None:
    """
    Remove um aluno e todos os registros vinculados a ele.

    Antes de excluir o aluno, a função remove:
    1. Os registros da tabela ``notas`` (vínculos com disciplinas,
       professores, notas e faltas).
    2. O usuário associado na tabela ``usuarios``.
    3. O próprio aluno na tabela ``alunos``.

    Args:
        rgm (int): Registro Geral de Matrícula do aluno.

    Returns:
        None
    """

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Busca o ID interno do aluno a partir do RGM
            cursor.execute("""
                SELECT id
                FROM alunos
                WHERE rgm = ?
            """, (rgm,))

            resultado = cursor.fetchone()

            # Caso o aluno não exista
            if not resultado:
                print(f"Nenhum aluno encontrado com RGM {rgm}.")
                return

            aluno_id = resultado[0]

            # Remove vínculos na tabela de notas
            cursor.execute("""
                DELETE FROM notas
                WHERE aluno_id = ?
            """, (aluno_id,))

            # Remove o usuário vinculado ao aluno
            cursor.execute("""
                DELETE FROM usuarios
                WHERE aluno_id = ?
            """, (aluno_id,))

            # Remove o aluno
            cursor.execute("""
                DELETE FROM alunos
                WHERE id = ?
            """, (aluno_id,))

            print(
                f"Aluno de RGM {rgm} e todos os registros "
                f"relacionados foram removidos com sucesso."
            )

    except Exception as e:
        print(f"Erro: {e}")


def obter_alunos() -> list[tuple]:
    """
     Recupera todos os alunos cadastrados no sistema.

    A consulta retorna todos os registros da tabela `alunos`,
    incluindo dados como id, RGM, nome, sobrenome, email e curso.

    Returns:
        list[tuple]:
            Lista de tuplas contendo os dados dos alunos.
            Cada tupla representa um aluno no formato retornado pelo SQLite.
            Retorna uma lista vazia caso não existam registros.
    """

    with get_connection() as conn:
        cursor = conn.cursor()

        # Busca todos os registros da tabela alunos
        cursor.execute('SELECT * FROM alunos')

        return cursor.fetchall()


def obter_rgm_por_id(aluno_id)-> int | None:
    """
    Busca o RGM de um aluno a partir do seu ID interno.

    Args:
        aluno_id (int): ID interno do aluno no banco de dados.

    Returns:
        int | None:
            - int: RGM do aluno encontrado
            - None: caso o aluno não exista
    """

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT rgm
        FROM alunos
        WHERE id = ?
        """, (aluno_id,))

        resultado = cursor.fetchone()

        # Retorna o RGM se existir
        if resultado:
            return resultado[0]
        
        # Caso não exista aluno com esse ID
        return None


def area_aluno(usuario)-> None:
    """
    Área de interação do aluno no sistema.

    Permite que o aluno:
    - consulte suas notas;
    - navegue pelo menu de opções;
    - saia do sistema.

    O RGM é obtido a partir do ID do aluno vinculado ao usuário.

    Args:
        usuario (dict): Dados do usuário autenticado, contendo pelo
        menos o campo `aluno_id`.

    Returns:
        None
    """

    # Recupera o RGM do aluno a partir do ID interno
    rgm = obter_rgm_por_id(
        usuario["aluno_id"]
    )

    while True:
        menu_aluno()
        opcao = input("Escolha: ")

        if opcao == "1":
            consultar_notas_aluno(rgm)
            pausar()

        elif opcao == "0":
            break
        
        else:
            print("Opção inválida, tente novamente.")
