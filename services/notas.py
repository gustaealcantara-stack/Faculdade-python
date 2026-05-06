import sqlite3
from database import get_connection


def buscar_professor_por_registro(registro_professor: int):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, sobrenome
            FROM professores
            WHERE registro_professor = ?
        """, (registro_professor,))

        return cursor.fetchone()


def buscar_aluno_por_rgm(rgm: int):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, sobrenome
            FROM alunos
            WHERE rgm = ?
        """, (rgm,))

        return cursor.fetchone()


def buscar_disciplina_por_codigo(codigo: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, codigo
            FROM disciplinas
            WHERE codigo = ?
        """, (codigo,))

        return cursor.fetchone()


def calcular_media(a1=None, a2=None, af=None):

    if a1 is None or a2 is None:
        return None, "Notas incompletas"


    # média da faculdade = soma
    media = a1 + a2

    # aprovado direto
    if media >= 6:
        return media, "Aprovado"

    # Caso ainda não fez AF
    if af is None:
        return media, "AF"

    # AF substitui a menor nota
    if a1 <= a2:
        a1 = af
    else:
        a2 = af


    media_final = a1 + a2


    if media_final >= 6:
        return media_final, "Aprovado após AF"

    return media_final, "Reprovado"


def matricular_aluno(rgm: int, codigo_disciplina: str, registro_professor: int):
    """
    Matricula o aluno em uma disciplina vinculada a um professor.
    """

    try:
        aluno = buscar_aluno_por_rgm(rgm)
        if not aluno:
            print(f"Nenhum aluno encontrado com RGM: {rgm}")
            return

        disciplina = buscar_disciplina_por_codigo(codigo_disciplina)
        if not disciplina:
            print(f"Nenhuma disciplina encontrada com código: {codigo_disciplina}")
            return

        professor = buscar_professor_por_registro(registro_professor)
        if not professor:
            print(f"Nenhum professor encontrado com registro: {registro_professor}")
            return

        aluno_id, nome_aluno, sobrenome_aluno = aluno
        disciplina_id, nome_disciplina, codigo = disciplina
        professor_id, nome_professor, sobrenome_professor = professor

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 1 FROM notas
                WHERE aluno_id = ?
                AND disciplina_id = ?
                AND professor_id = ?
            """, (aluno_id, disciplina_id, professor_id))

            if cursor.fetchone():
                print("Este aluno já está matriculado nessa disciplina com esse professor.")
                return

            cursor.execute("""
                INSERT INTO notas (
                    aluno_id,
                    professor_id,
                    disciplina_id,
                    a1,
                    a2,
                    af,
                    media,
                    faltas
                )
                VALUES (?, ?, ?, NULL, NULL, NULL, NULL, 0)
            """, (aluno_id, professor_id, disciplina_id))

            print("Aluno matriculado com sucesso!")
            print(f"Aluno: {nome_aluno} {sobrenome_aluno}")
            print(f"Disciplina: {nome_disciplina} ({codigo})")
            print(f"Professor: {nome_professor} {sobrenome_professor}")

    except sqlite3.Error as e:
        print(f"Erro ao matricular aluno: {e}")


def inserir_ou_atualizar_notas(
    registro_professor: int,
    rgm: int,
    codigo_disciplina: str,
    a1=None,
    a2=None,
    af=None,
    faltas=None
):
    """
    Apenas o professor responsável pela matrícula pode atualizar as notas.
    """

    try:
        professor = buscar_professor_por_registro(registro_professor)
        if not professor:
            print("Acesso negado: professor não encontrado.")
            return

        aluno = buscar_aluno_por_rgm(rgm)
        if not aluno:
            print(f"Nenhum aluno encontrado com RGM: {rgm}")
            return

        disciplina = buscar_disciplina_por_codigo(codigo_disciplina)
        if not disciplina:
            print(f"Nenhuma disciplina encontrada com código: {codigo_disciplina}")
            return

        professor_id = professor[0]
        aluno_id = aluno[0]
        disciplina_id = disciplina[0]

        media, status = calcular_media(a1, a2, af)
        
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id FROM notas
                WHERE aluno_id = ?
                AND disciplina_id = ?
                AND professor_id = ?
            """, (aluno_id, disciplina_id, professor_id))

            resultado = cursor.fetchone()

            if not resultado:
                print("Este professor não tem permissão para lançar notas desse aluno nessa disciplina.")
                return

            nota_id = resultado[0]

            cursor.execute("""
                UPDATE notas
                SET a1 = ?,
                    a2 = ?,
                    af = ?,
                    media = ?,
                    faltas = COALESCE(?, faltas)
                WHERE id = ?
            """, (a1, a2, af, media, faltas, nota_id))

            print("Notas atualizadas com sucesso!")

            if media is not None:
                print(f"Média: {media:.1f}")
                print(f"Status: {status}")

    except sqlite3.Error as e:
        print(f"Erro ao inserir notas: {e}")


def consultar_notas_professor(registro_professor: int):
    """
    Professor consulta apenas as notas dos alunos vinculados a ele.
    """

    try:
        professor = buscar_professor_por_registro(registro_professor)
        if not professor:
            print("Professor não encontrado.")
            return

        professor_id = professor[0]

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    alunos.rgm,
                    alunos.nome,
                    alunos.sobrenome,
                    disciplinas.nome,
                    disciplinas.codigo,
                    notas.a1,
                    notas.a2,
                    notas.af,
                    notas.media,
                    notas.faltas
                FROM notas
                INNER JOIN alunos ON notas.aluno_id = alunos.id
                INNER JOIN disciplinas ON notas.disciplina_id = disciplinas.id
                WHERE notas.professor_id = ?
            """, (professor_id,))

            dados = cursor.fetchall()

            print("\n---- NOTAS DOS ALUNOS ----\n")

            if not dados:
                print("Nenhuma nota encontrada para este professor.")
                return

            for rgm, nome, sobrenome, disciplina, codigo, a1, a2, af, media, faltas in dados:
                status = obter_status(a1, a2, af)

                if faltas > 23:
                    status = "Reprovado por falta"

                print('')
                print(f"Aluno: {nome} {sobrenome} | RGM: {rgm}")
                print(f"Disciplina: {disciplina} ({codigo})")
                print(f"A1: {a1} | A2: {a2} | AF: {af}")
                print(f"Média: {media:.1f} | Faltas: {faltas} | Status: {status}")
                print("-" * 30)
                print('')

    except Exception as e:
        # print({e})
        print(f"Erro ao consultar notas: Notas ainda não lançadas")


def consultar_notas_aluno(rgm: int):
    """
    Aluno consulta apenas suas próprias notas.
    """

    try:
        aluno = buscar_aluno_por_rgm(rgm)
        if not aluno:
            print(f"Nenhum aluno encontrado com RGM: {rgm}")
            return

        aluno_id = aluno[0]

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    disciplinas.nome,
                    disciplinas.codigo,
                    professores.nome,
                    professores.sobrenome,
                    notas.a1,
                    notas.a2,
                    notas.af,
                    notas.media,
                    notas.faltas
                FROM notas
                INNER JOIN disciplinas ON notas.disciplina_id = disciplinas.id
                INNER JOIN professores ON notas.professor_id = professores.id
                WHERE notas.aluno_id = ?
            """, (aluno_id,))

            dados = cursor.fetchall()

            print("\n---- MINHAS NOTAS ----\n")

            if not dados:
                print("Nenhuma nota encontrada.")
                return
            
            for disciplina, codigo, prof_nome, prof_sobrenome, a1, a2, af, media, faltas in dados:
                status = None
                if a1 and a2:
                    status = obter_status(a1, a2, af)

                if faltas > 23:
                    status = "Reprovado por falta"

                print(f"Disciplina: {disciplina} ({codigo})")
                print(f"Professor: {prof_nome} {prof_sobrenome}")
                if a1 and a2 and media:
                    if af:
                        print(f"A1: {a1} | A2: {a2} | AF: {af}")
                    else:
                        print(f"A1: {a1} | A2: {a2}")
                    print(f"Média: {media:.1f} | Faltas: {faltas} | Status: {status}")
                else:
                    print('Notas indisponíveis nesta disciplina.')
                    print(f'Faltas: {faltas if faltas else 0} | Status: {status if status else ""}')
                print("-" * 30)

    except sqlite3.Error as e:
        # print({e})
        print(f"Erro ao consultar notas do aluno:Notas ainda não lançadas")

 
def obter_status(a1=None, a2=None, af=None):
    media, status = calcular_media(a1, a2, af)
    return status

