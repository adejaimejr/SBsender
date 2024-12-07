import os
import logging
from datetime import datetime
import sys

def setup_logger():
    # Configura o logger
    logger = logging.getLogger('SBsender')
    logger.setLevel(logging.CRITICAL)  # Define o nível para CRITICAL para suprimir logs de menor nível
    
    # Cria um formatter que inclui timestamp
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para console
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.DEBUG)
    # console_handler.setFormatter(formatter)
    
    # Ensure the logs directory exists
    # log_directory = 'logs'
    # if not os.path.exists(log_directory):
    #     print(f"Creating log directory at: {log_directory}")
    #     os.makedirs(log_directory)
    # else:
    #     print(f"Log directory already exists at: {log_directory}")
    
    # Handler para arquivo
    # log_file_path = f'{log_directory}/sbsender_{datetime.now().strftime("%Y%m%d")}.log'
    # print(f"Log file path: {log_file_path}")
    # file_handler = logging.FileHandler(log_file_path)
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(formatter)
    
    # Adiciona os handlers ao logger
    # logger.addHandler(console_handler)
    # logger.addHandler(file_handler)
    
    return logger

# Cria uma instância global do logger
logger = setup_logger()