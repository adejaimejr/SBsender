import re

def clean_phone_number(phone: str) -> str:
    """
    Remove caracteres especiais e espaços do número de telefone.
    """
    return re.sub(r'[^\d+]', '', phone)

def format_phone_number(phone: str) -> str:
    """
    Formata um número de telefone para o padrão WhatsApp BR.
    Retorna None se o número for inválido.
    
    Args:
        phone (str): Número de telefone a ser formatado
        
    Returns:
        str: Número formatado ou None se inválido
    """
    # Remove todos os caracteres não numéricos
    numbers_only = re.sub(r'\D', '', str(phone))
    
    # Verifica se é um número válido
    if not numbers_only:
        return None
        
    # Se começar com 0, remove
    if numbers_only.startswith('0'):
        numbers_only = numbers_only[1:]
    
    # Adiciona o código do país se não tiver
    if not numbers_only.startswith('55'):
        numbers_only = '55' + numbers_only
    
    # Verifica o tamanho após adicionar o código do país
    if len(numbers_only) < 12 or len(numbers_only) > 13:
        return None
    
    # Se tiver 12 dígitos (sem o 9), adiciona o 9
    if len(numbers_only) == 12:
        area_code = numbers_only[2:4]
        number = numbers_only[4:]
        numbers_only = f"55{area_code}9{number}"
    
    # Verifica o formato final
    if not re.match(r'^55\d{2}9\d{8}$', numbers_only):
        return None
    
    return numbers_only

def validate_phone_list(numbers: list) -> tuple:
    """
    Valida uma lista de números de telefone.
    
    Args:
        numbers (list): Lista de números para validar
        
    Returns:
        tuple: (números válidos, números inválidos)
    """
    valid_numbers = []
    invalid_numbers = []
    
    for number in numbers:
        formatted = format_phone_number(number)
        if formatted:
            valid_numbers.append(formatted)
        else:
            invalid_numbers.append(number)
    
    return valid_numbers, invalid_numbers
