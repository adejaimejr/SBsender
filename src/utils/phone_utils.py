import re

def clean_phone_number(phone: str) -> str:
    """
    Remove caracteres especiais e espaços do número de telefone.
    """
    return re.sub(r'[^\d+]', '', phone)

def format_brazilian_number(phone: str) -> str:
    """
    Formata um número de telefone brasileiro para o padrão WhatsApp.
    Retorna None se o número for inválido.
    """
    # Limpa o número
    clean_number = clean_phone_number(phone)
    
    # Remove o '+' inicial se existir
    if clean_number.startswith('+'):
        clean_number = clean_number[1:]
    
    # Remove o '0' inicial do DDD se existir
    if len(clean_number) > 2 and clean_number[2] == '0':
        clean_number = clean_number[:2] + clean_number[3:]
    
    # Adiciona o código do país (55) se não existir
    if not clean_number.startswith('55'):
        clean_number = '55' + clean_number
    
    # Valida o tamanho do número (considerando 55 + DDD + número)
    if len(clean_number) != 13:  # 55 + 11 + 999999999
        return None
    
    return clean_number

def validate_phone_list(phones: list) -> tuple:
    """
    Valida e formata uma lista de números de telefone.
    Retorna uma tupla com (números válidos, números inválidos).
    """
    valid_numbers = []
    invalid_numbers = []
    
    for phone in phones:
        formatted = format_brazilian_number(phone)
        if formatted:
            valid_numbers.append(formatted)
        else:
            invalid_numbers.append(phone)
    
    return valid_numbers, invalid_numbers
