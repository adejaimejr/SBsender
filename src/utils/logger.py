import logging
import sys
from datetime import datetime

def setup_logger():
    # Configura o logger
    logger = logging.getLogger('SBsender')
    logger.setLevel(logging.DEBUG)
    
    # Cria um formatter que inclui timestamp
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo
    file_handler = logging.FileHandler(f'logs/sbsender_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Adiciona os handlers ao logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Cria uma instância global do logger
logger = setup_logger()