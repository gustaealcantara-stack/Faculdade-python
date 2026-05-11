import sqlite3
from database import get_connection


def buscar_professor_por_registro(registro_professor: int):
    """
    Busca um professor pelo número de registro.

    Args:
        registro_professor (int): Número de registro do professor

    Returns:
        tuple | None:
            Uma tupla no formato (id, nome, sobrenome) se o professor
            for encontrado ou None caso não exista
    """

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, sobrenome
            FROM professores
            WHERE registro_professor = ?
        """, (registro_professor,))

        return cursor.fetchone()


def buscar_aluno_por_rgm(rgm: int):
    """
    Busca um aluno pelo RGM

    Args:
        rgm (int): Registro Geral de Matricula do aluno

    Returns:
        tuple | None:
            Uma tupla no formato (id, nome, sobrenome) se o aluno
            for encontrado ou None caso não exista

    """

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, sobrenome
            FROM alunos
            WHERE rgm = ?
        """, (rgm,))

        return cursor.fetchone()


def buscar_disciplina_por_codigo(codigo: str):
    """
    Busca uma disciplina pelo código.

    Args:
        codigo (str): Código identificador da disciplina

    Returns:
        tuple | None:
            Uma tupla no formato (id, nome, codigo) se a disciplina
            for encotrada ou None caso não exista
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, codigo
            FROM disciplinas
            WHERE codigo = ?
        """, (codigo,))

        return cursor.fetchone()


def calcular_media(a1=None, a2=None, af=None):
    """
    Calcula a média final e o status acadêmico do aluno.

    Regras:
    - A média é obtida pela soma da A1 e A2
    - Se a soma for maior ou igual a 6, o aluno é aprovado diretamente
    - Se a soma for menor que 6 e a AF não tiver sido informada,
      o status será "AF"
    - Caso exista AF, ela substitui a menor nota entre A1 e A2
    - A nova soma define se o aluno foi aprovado após AF ou reprovado

    Args:
        a1 (float | None): Nota da A1 (SEGUNDA avaliação do semestre)
        a2 (float | None): Nota da A2 (PRIMEIRA avaliação do semestre)
        af (float | None): Nota da avaliação final
    
    Returns:
        tuple:
            - media (float | None): Média calculada
            - status (str): Situação acadêmica do aluno
    """
    
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


def vincular_aluno_disciplina(rgm: int, codigo_disciplina: str, registro_professor: int):
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
    Insere ou atualiza as notas de um aluno em uma disciplina.

    Apenas o professor responsável pelo vínculo entre aluno e
    disciplina tem permissão para lançar ou alterar as notas.

    Args:
        registro_professor (int): Registro do professor.
        rgm (int): RGM do aluno.
        codigo_disciplina (str): Código da disciplina.
        a1 (float | None): Nota da A1.
        a2 (float | None): Nota da A2.
        af (float | None): Nota da Avaliação Final.
        faltas (int | None): Quantidade de faltas do aluno.

    Returns:
        None
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
            print(
                f"Nenhuma disciplina encontrada com código: "
                f"{codigo_disciplina}"
            )
            return

        professor_id = professor[0]
        aluno_id = aluno[0]
        disciplina_id = disciplina[0]

        # Calcula a média numérica.
        media, _ = calcular_media(a1, a2, af)

        # Determina o status final considerando também as faltas.
        status = obter_status(a1, a2, af, faltas or 0)

        with get_connection() as conn:
            cursor = conn.cursor()

            # Verifica se o professor possui vínculo com este
            # aluno e disciplina.
            cursor.execute("""
                SELECT id
                FROM notas
                WHERE aluno_id = ?
                  AND disciplina_id = ?
                  AND professor_id = ?
            """, (aluno_id, disciplina_id, professor_id))

            resultado = cursor.fetchone()

            if not resultado:
                print(
                    "Este professor não tem permissão para "
                    "lançar notas desse aluno nessa disciplina."
                )
                return

            nota_id = resultado[0]

            # Atualiza notas, média e faltas.
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

            # Exibe o resultado final.
            if media is not None:
                print(f"Média: {media:.1f}")
                print(f"Status: {status}")

    except sqlite3.Error as e:
        print(f"Erro ao inserir notas: {e}")


def consultar_notas_professor(registro_professor: int):
    """
    Exibe as notas dos alunos vinculados ao professor informado.

    A consulta apresenta, para cada aluno:
    - RGM e nome completo;
    - disciplina e código;
    - notas A1, A2 e AF;
    - média final;
    - quantidade de faltas;
    - status acadêmico.

    O status é calculado com base nas notas utilizando a função
    ``obter_status()``. Caso o aluno possua mais de 25 faltas,
    o status é sobrescrito para ``"Reprovado por falta"``,
    independentemente da média obtida.

    Args:
        registro_professor (int): Número de registro do professor.

    Returns:
        None
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
                INNER JOIN alunos
                    ON notas.aluno_id = alunos.id
                INNER JOIN disciplinas
                    ON notas.disciplina_id = disciplinas.id
                WHERE notas.professor_id = ?
            """, (professor_id,))

            dados = cursor.fetchall()

            print("\n---- NOTAS DOS ALUNOS ----\n")

            if not dados:
                print("Nenhuma nota encontrada para este professor.")
                return

            for (
                rgm,
                nome,
                sobrenome,
                disciplina,
                codigo,
                a1,
                a2,
                af,
                media,
                faltas
            ) in dados:

                # Calcula o status com base nas notas e faltas.
                status = obter_status(a1, a2, af)

                if faltas > 25:
                    status = "Reprovado por falta"

                print()
                print(f"Aluno: {nome} {sobrenome} | RGM: {rgm}")
                print(f"Disciplina: {disciplina} ({codigo})")
                print(f"A1: {a1} | A2: {a2} | AF: {af}")

                # Exibe a média somente quando já tiver sido calculada.
                if media is not None:
                    print(
                        f"Média: {media:.1f} | "
                        f"Faltas: {faltas} | "
                        f"Status: {status}"
                    )
                else:
                    print(
                        f"Média: Não calculada | "
                        f"Faltas: {faltas} | "
                        f"Status: {status}"
                    )

                print("-" * 30)
                print()

    except Exception:
        print("Erro ao consultar notas: Notas ainda não lançadas")


def consultar_notas_aluno(rgm: int):
    """
    Exibe as notas e a situação acadêmica do aluno informado.

    A consulta apresenta, para cada disciplina em que o aluno estiver
    matriculado:
    - nome da disciplina e código;
    - nome do professor responsável;
    - notas A1, A2 e AF (quando houver);
    - média final;
    - quantidade de faltas;
    - status acadêmico.

    O status é calculado pela função ``obter_status()``, que considera
    tanto as notas quanto a quantidade de faltas. Se o aluno possuir
    mais de 25 faltas, o status será ``"Reprovado por falta"``,
    independentemente da média obtida.

    Args:
        rgm (int): Registro Geral de Matrícula do aluno.

    Returns:
        None
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
                INNER JOIN disciplinas
                    ON notas.disciplina_id = disciplinas.id
                INNER JOIN professores
                    ON notas.professor_id = professores.id
                WHERE notas.aluno_id = ?
            """, (aluno_id,))

            dados = cursor.fetchall()

            print("\n---- MINHAS NOTAS ----\n")

            if not dados:
                print("Nenhuma nota encontrada.")
                return

            for (
                disciplina,
                codigo,
                prof_nome,
                prof_sobrenome,
                a1,
                a2,
                af,
                media,
                faltas
            ) in dados:

                # Calcula o status considerando notas e faltas.
                status = obter_status(a1, a2, af, faltas or 0)

                print(f"Disciplina: {disciplina} ({codigo})")
                print(f"Professor: {prof_nome} {prof_sobrenome}")

                # Exibe as notas, quando já tiverem sido lançadas.
                if a1 is not None and a2 is not None:
                    if af is not None:
                        print(f"A1: {a1} | A2: {a2} | AF: {af}")
                    else:
                        print(f"A1: {a1} | A2: {a2}")
                else:
                    print("Notas indisponíveis nesta disciplina.")

                # Exibe média e status, quando a média já tiver sido calculada.
                if media is not None:
                    print(
                        f"Média: {media:.1f} | "
                        f"Faltas: {faltas} | "
                        f"Status: {status}"
                    )
                else:
                    print(
                        f"Média: Não calculada | "
                        f"Faltas: {faltas or 0} | "
                        f"Status: {status}"
                    )

                print("-" * 30)

    except sqlite3.Error:
        print("Erro ao consultar notas do aluno: Notas ainda não lançadas")


def obter_status(a1=None, a2=None, af=None, faltas=0):
    """
    Determina a situação acadêmica final do aluno.

    A função considera:
    - o resultado de ``calcular_media()``;
    - a quantidade de faltas.

    Regras:
    - Se o aluno possuir mais de 25 faltas, o status será
      "Reprovado por falta", independentemente da média.
    - Caso contrário, o status será o retornado por
      ``calcular_media()``.

    Args:
        a1 (float | None): Nota da A1.
        a2 (float | None): Nota da A2.
        af (float | None): Nota da Avaliação Final.
        faltas (int): Quantidade de faltas do aluno.

    Returns:
        str: Situação acadêmica final do aluno.
    """
    _, status = calcular_media(a1, a2, af)

    if faltas > 25:
        return "Reprovado por falta"

    return status
