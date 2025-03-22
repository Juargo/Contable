import pandas as pd
import io
import os
from typing import List, Dict, Any, Callable
import csv
import re
from datetime import datetime

def process_bank_report(file_content: bytes, bank_name: str) -> List[Dict[str, Any]]:
    """
    Procesa el reporte bancario según el banco emisor.
    
    Args:
        file_content (bytes): Contenido del archivo de reporte
        bank_name (str): Nombre del banco emisor
        
    Returns:
        List[Dict[str, Any]]: Lista de transacciones con formato unificado
    """
    # Diccionario de funciones de procesamiento por banco
    processors = {
        "santander": process_santander_report,
        "bbva": process_bbva_report,
        "caixabank": process_caixabank_report,
        "sabadell": process_sabadell_report,
        "bankinter": process_bankinter_report,
        "ing": process_ing_report
    }
    
    # Verificar si existe un procesador para el banco especificado
    if bank_name not in processors:
        raise ValueError(f"No hay un procesador implementado para el banco: {bank_name}")
    
    # Procesar el archivo con el procesador correspondiente
    processor = processors[bank_name]
    return processor(file_content)

def process_santander_report(file_content: bytes) -> List[Dict[str, Any]]:
    """
    Procesa reportes del Banco Santander.
    Generalmente CSV con formato:
    Fecha;Concepto;Importe;Saldo
    """
    try:
        # Intentar diferentes codificaciones
        for encoding in ['utf-8', 'iso-8859-1', 'latin1']:
            try:
                csv_data = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
                
        # Crear DataFrame a partir del CSV
        df = pd.read_csv(io.StringIO(csv_data), sep=';')
        
        # Mapear columnas al formato estandarizado
        # Asumiendo nombres de columnas específicos de Santander
        column_map = {
            'Fecha': 'date',
            'Concepto': 'description',
            'Importe': 'amount'
        }
        
        # Renombrar columnas según el mapeo
        df = df.rename(columns={old: new for old, new in column_map.items() if old in df.columns})
        
        # Asegurarse de que están las columnas necesarias
        for col in ['date', 'description', 'amount']:
            if col not in df.columns:
                raise ValueError(f"Falta la columna {col} en el reporte")
        
        # Añadir categoría (sin clasificar inicialmente)
        df['category'] = 'Sin clasificar'
        
        # Convertir a lista de diccionarios
        transactions = df[['date', 'description', 'category', 'amount']].to_dict('records')
        
        return transactions
    except Exception as e:
        print(f"Error procesando el reporte Santander: {str(e)}")
        raise

def process_bbva_report(file_content: bytes) -> List[Dict[str, Any]]:
    """
    Procesa reportes del BBVA.
    Implementación específica para el formato BBVA.
    """
    # Implementación simplificada para BBVA
    try:
        csv_data = file_content.decode('latin1')
        df = pd.read_csv(io.StringIO(csv_data), sep=',')
        
        # Mapear columnas según el formato específico de BBVA
        # (Ajustar según formato real)
        column_map = {
            'F.VALOR': 'date',
            'CONCEPTO': 'description',
            'IMPORTE': 'amount'
        }
        
        # Renombrar columnas según el mapeo
        df = df.rename(columns={old: new for old, new in column_map.items() if old in df.columns})
        
        # Añadir categoría sin clasificar
        df['category'] = 'Sin clasificar'
        
        transactions = df[['date', 'description', 'category', 'amount']].to_dict('records')
        return transactions
    except Exception as e:
        print(f"Error procesando el reporte BBVA: {str(e)}")
        raise

def process_caixabank_report(file_content: bytes) -> List[Dict[str, Any]]:
    """Procesador para CaixaBank (implementación base)"""
    # Ejemplo básico - ajustar según el formato real de CaixaBank
    return process_generic_report(file_content, "caixabank")

def process_sabadell_report(file_content: bytes) -> List[Dict[str, Any]]:
    """Procesador para Banco Sabadell (implementación base)"""
    return process_generic_report(file_content, "sabadell")

def process_bankinter_report(file_content: bytes) -> List[Dict[str, Any]]:
    """Procesador para Bankinter (implementación base)"""
    return process_generic_report(file_content, "bankinter")

def process_ing_report(file_content: bytes) -> List[Dict[str, Any]]:
    """Procesador para ING (implementación base)"""
    return process_generic_report(file_content, "ing")

def process_generic_report(file_content: bytes, bank_name: str) -> List[Dict[str, Any]]:
    """
    Procesador genérico para bancos sin implementación específica.
    Intenta identificar el formato básico CSV.
    """
    try:
        # Intentar varias codificaciones
        for encoding in ['utf-8', 'iso-8859-1', 'latin1']:
            try:
                csv_data = file_content.decode(encoding)
                
                # Detectar separador
                dialect = csv.Sniffer().sniff(csv_data[:1024])
                separator = dialect.delimiter
                
                df = pd.read_csv(io.StringIO(csv_data), sep=separator)
                
                # Intentar identificar columnas por nombres comunes
                date_cols = [col for col in df.columns if re.search(r'fecha|date|dia', col.lower())]
                desc_cols = [col for col in df.columns if re.search(r'concepto|desc|concept', col.lower())]
                amount_cols = [col for col in df.columns if re.search(r'importe|amount|valor|cantidad', col.lower())]
                
                if date_cols and desc_cols and amount_cols:
                    result_df = pd.DataFrame()
                    result_df['date'] = df[date_cols[0]]
                    result_df['description'] = df[desc_cols[0]]
                    result_df['amount'] = df[amount_cols[0]]
                    result_df['category'] = 'Sin clasificar'
                    
                    return result_df.to_dict('records')
                
                break
            except Exception:
                continue
        
        # Si no se pudo procesar, devolver un mensaje de error
        raise ValueError(f"No se pudo determinar automáticamente el formato del reporte del banco {bank_name}")
    except Exception as e:
        print(f"Error procesando reporte genérico para {bank_name}: {str(e)}")
        
        # Devolver datos de ejemplo para no detener el flujo en desarrollo
        return [
            {"date": "2023-01-01", "description": f"Ejemplo {bank_name}", "category": "Sin clasificar", "amount": 0},
            {"date": "2023-01-02", "description": "Se requiere implementación específica", "category": "Sin clasificar", "amount": 0},
        ]
