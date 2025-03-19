import logging
import os
import sys
from datetime import datetime

def setup_logger(name='contable', log_dir=None, level=logging.INFO, console=True):
    """
    Configura un logger con salida a consola y archivo opcional
    
    Args:
        name (str): Nombre del logger
        log_dir (str): Directorio para almacenar logs. Si es None, no crea archivo
        level (int): Nivel de logging (DEBUG, INFO, etc.)
        console (bool): Si se debe mostrar salida por consola
    
    Returns:
        logging.Logger: El objeto logger configurado
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = []  # Limpiar handlers existentes
    
    # Formato para los mensajesx
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Agregar handler de consola si se solicita
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Agregar handler de archivo si se proporciona un directorio
    if log_dir:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"contable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Crear logger por defecto
default_logger = setup_logger()

def get_logger():
    """Obtiene el logger por defecto"""
    return default_logger

def enable_debug():
    """Activa el nivel DEBUG en el logger por defecto"""
    default_logger.setLevel(logging.DEBUG)
    for handler in default_logger.handlers:
        handler.setLevel(logging.DEBUG)
    default_logger.debug("Modo DEBUG activado")
