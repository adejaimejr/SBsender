import pandas as pd
from typing import List, Tuple
from src.utils.phone_utils import validate_phone_list

def process_text_input(text: str) -> Tuple[List[str], List[str]]:
    """
    Processa números de telefone inseridos como texto.
    Retorna uma tupla com (números válidos, números inválidos).
    """
    # Divide o texto por vírgulas e quebras de linha
    numbers = [n.strip() for n in text.replace('\n', ',').split(',')]
    # Remove números vazios
    numbers = [n for n in numbers if n]
    
    return validate_phone_list(numbers)

def process_csv_file(file) -> Tuple[List[str], List[str]]:
    """
    Processa números de telefone de um arquivo CSV.
    Retorna uma tupla com (números válidos, números inválidos).
    """
    try:
        df = pd.read_csv(file)
        # Assume que a primeira coluna contém os números
        numbers = df.iloc[:, 0].astype(str).tolist()
        return validate_phone_list(numbers)
    except Exception as e:
        # Em caso de erro, retorna listas vazias
        return [], []
