import os
import sys
import logging
import platform
from enum import Enum
from datetime import datetime
from time import sleep


# ao chamar a função, passar '__file__'(sem aspas) como parâmetro, ou a string que queira usar no log
def logging_config(nomeArquivo):
    """
    Configura o logging para o script atual.

    Parâmetros:
      nomeArquivo (str): o caminho ou nome do arquivo (geralmente passe __file__ ao chamar).

    Comportamento:
      - Cria um diretório `logs` no diretório do script (se não existir).
      - Gera um arquivo de log com nome baseado no script e timestamp.
      - Configura logging com FileHandler (UTF-8) e StreamHandler para stdout.

    Retorna:
      None
    """
    # Configurar logging
    script_name = os.path.splitext(os.path.basename(nomeArquivo))[0]
    data_hora = datetime.now().strftime("%d-%m-%Y_%Hh-%Mm-%Ss")
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    log_dir = os.path.join(script_dir, "logs")

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{script_name}_{data_hora}.log")

    print(f"Log file: {log_file}")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


class Cores(Enum):
    PRETO = 30
    VERMELHO = 31
    VERDE = 32
    AMARELO = 33
    AZUL = 34
    MAGENTA = 35
    CIANO = 36
    BRANCO = 37
    CINZA = 90
    VERMELHO_CLARO = 91
    VERDE_CLARO = 92
    AMARELO_CLARO = 93
    AZUL_CLARO = 94
    MAGENTA_CLARO = 95
    CIANO_CLARO = 96
    BRANCO_CLARO = 97
    FUNDO_PRETO = 40
    FUNDO_VERMELHO = 41
    FUNDO_VERDE = 42
    FUNDO_AMARELO = 43
    FUNDO_AZUL = 44
    FUNDO_MAGENTA = 45
    FUNDO_CIANO = 46
    FUNDO_BRANCO = 47
    FUNDO_CINZA = 100
    FUNDO_VERMELHO_CLARO = 101
    FUNDO_VERDE_CLARO = 102
    FUNDO_AMARELO_CLARO = 103
    FUNDO_AZUL_CLARO = 104
    FUNDO_MAGENTA_CLARO = 105
    FUNDO_CIANO_CLARO = 106
    FUNDO_BRANCO_CLARO = 107


def textoCor(texto: str, cor_texto: Cores = None, cor_fundo: Cores = None) -> str:
    """
    Pinta o texto com cores ANSI.

    Parâmetros:
      texto (str): o texto a ser colorido.
      cor_texto (Cores, opcional): cor do texto (enum Cores).
      cor_fundo (Cores, opcional): cor de fundo (enum Cores).

    Retorna:
      str: texto com códigos ANSI aplicados.
    """
    codigos = []
    if cor_texto is not None:
        codigos.append(str(cor_texto.value))

    if cor_fundo is not None:
        codigos.append(str(cor_fundo.value))
        
    if codigos:
        return f"\033[{';'.join(codigos)}m{texto}\033[0m"
    else:
        return texto


# funcao para limpar o terminal
def limpar():
    """
    Limpa o terminal de acordo com o sistema operacional.

    Comportamento:
        - No Windows executa o comando `cls`.
        - Em outros sistemas executa `clear`.

    Retorna:
        None
    """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# funcao para fazer sleep no codigo
def pausa(time: float = 0.5):
    """
    Pausa a execução do programa por um tempo especificado.

    Parâmetros:
        time (float): número de segundos para pausar (padrão 0.5).

    Retorna:
        None
    """
    sleep(time)
    