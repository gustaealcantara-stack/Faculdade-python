import os
import unicodedata

from models.usuario import autenticar_usuario


def limpar_terminal() -> None:
    """
    Limpa o terminal dependendo do sistema operacional.

    - Windows: usa 'cls'
    - Linux/Mac: usa 'clear'

    Returns:
        None:
            Apenas executa um comando no sistema operacional.
    """

    os.system("cls" if os.name == "nt" else "clear")


def pausar() -> None:
    """
    Pausa a execução do programa até o usuário pressionar ENTER.

    Usada para manter mensagens ou menus visíveis no terminal.

    Returns:
        None
    """

    input("\nPressione ENTER para continuar...")


def tela_login() -> dict | None:
    """
    Realiza o processo de autenticação do usuário.

    Solicita email e senha, valida no banco de dados e,
    se for bem-sucedido, retorna os dados estruturados do usuário.

    Returns:
        dict | None:
            - dict: dados do usuário autenticado contendo:
                - id (int)
                - email (str)
                - perfil (str)
                - aluno_id (int | None)
                - professor_id (int | None)

            - None: caso o login seja inválido
    """

    print("\n===== LOGIN =====")
    email = input("Email: ")
    senha = input("Senha: ")

    usuario = autenticar_usuario(email, senha)

    if usuario:
        return {
            "id": usuario[0],
            "email": usuario[1],
            "perfil": usuario[2],
            "aluno_id": usuario[3],
            "professor_id": usuario[4]
        }

    return None


def remover_acentos(texto: str) -> str:
    """
    Remove acentos e caracteres diacríticos de uma string.

    A função normaliza o texto para o formato NFD (Normalization Form Decomposition)
    e remove todos os caracteres classificados como marcas não espaçadas (Mn),
    que representam acentos e sinais diacríticos.

    Exemplo:
       "João"  -> "Joa\u0303o" (NFD: a letra 'a' e o til combinando se separam)
        "Joao"  <- (Filtro Mn: o caractere de acento é removido)

    Args:
        texto (str): Texto de entrada que pode conter acentos.

    Returns:
        str:
            Texto sem acentos ou caracteres diacríticos.
    """

    # Normaliza o texto para decompor caracteres acentuados
    texto_normalizado = unicodedata.normalize("NFD", texto)

    # Remove caracteres de marca (acentos, til, cedilha, etc.)
    return "".join(
        caractere
        for caractere in texto_normalizado
        if unicodedata.category(caractere) != "Mn"
    )


def extrair_primeiro_nome(nome_completo: str) -> str:
    """
    Extrai o primeiro nome de uma string de nome completo.

    A função remove espaços extras e retorna apenas a primeira palavra,
    formatando-a com a primeira letra maiúscula.

    Exemplo:
        "joão silva" → "João"
        "  maria  de souza " → "Maria"

    Args:
        nome_completo (str): Nome completo informado pelo usuário.

    Returns:
        str:
            Primeiro nome formatado (capitalizado).
    """
    if not nome_completo.strip():
        return ""

    return nome_completo.strip().split()[0].capitalize()


def extrair_sobrenome(sobrenome_completo: str) -> str:
    """
      Extrai o último sobrenome relevante de uma string,
    ignorando preposições comuns 

    A função remove palavras como:
    - de, da, do, das, dos

    e retorna o último sobrenome válido encontrado.

    Exemplos:
        "da Silva" → "Silva"
        "dos Santos" → "Santos"
        "de Oliveira" → "Oliveira"
        "Silva Souza" → "Souza"

    Args:
        sobrenome_completo (str): Sobrenome completo informado.

    Returns:
        str:
            Último sobrenome relevante capitalizado.
            Retorna string vazia ("") caso não haja sobrenome válido.
    """

    # Palavras que não devem ser consideradas como sobrenome
    palavras_ignorar = {
        "de",
        "da",
        "do",
        "das",
        "dos"
    }

    # Normaliza entrada e separa em palavras
    palavras = sobrenome_completo.strip().lower().split()

    # Filtra apenas palavras válidas (remove preposições)
    sobrenomes_validos = [
        palavra
        for palavra in palavras
        if palavra not in palavras_ignorar
    ]

    if not sobrenomes_validos:
        return ""

    # Retorna o último sobrenome com primeira letra maiúscula
    return sobrenomes_validos[-1].capitalize()
