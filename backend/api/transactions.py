"""Módulo para manejar operaciones relacionadas con transacciones"""

import logging
import os
import sys
import tempfile
import math
import json
from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime

import pandas as pd
import numpy as np
from database.models import Transaction
from database.schemas import Transaction_Pydantic, TransactionIn_Pydantic
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Body, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import calendar

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("contable")


router = APIRouter(tags=["Transactions"])


@router.get("/transactions", response_model=List[Transaction_Pydantic])
async def get_all_transactions():
    """Obtiene todas las transacciones de la base de datos"""
    return await Transaction_Pydantic.from_queryset(Transaction.all())


@router.get("/transactions/{transaction_id}", response_model=Transaction_Pydantic)
async def get_transaction(transaction_id: int):
    """Obtiene una transacción por su ID"""
    transaction = await Transaction.get_or_none(id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return await Transaction_Pydantic.from_tortoise_orm(transaction)


@router.post("/transactions", response_model=Transaction_Pydantic)
async def create_transaction(transaction: TransactionIn_Pydantic):
    """Crea una nueva transacción"""
    transaction_obj = await Transaction.create(**transaction.dict(exclude_unset=True))
    return await Transaction_Pydantic.from_tortoise_orm(transaction_obj)


def sanitize_json_data(obj: Any) -> Any:
    """
    Convierte valores no serializables en JSON (como NaN, Infinity) a valores compatibles.
    También convierte numpy.int64/float64 a tipos Python nativos para serialización.
    """
    if isinstance(obj, dict):
        return {k: sanitize_json_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_data(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        num = float(obj)
        if math.isnan(num):
            return None
        elif math.isinf(num):
            return None  # o podrías usar str(num) para mantener "inf"/"-inf" como cadena
        else:
            return num
    elif isinstance(obj, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    else:
        return obj

@router.post("/upload-bank-report")
async def upload_bank_report(
    file: UploadFile = File(...),
    bank_id: str = Form(...),
):
    """
    Recibe y procesa un archivo Excel de banco.

    - **file**: Archivo Excel del banco
    - **bank_id**: ID del banco (bancoestado, bancochile, bancosantander, bancobci)

    Retorna el saldo contable y los movimientos extraídos del archivo, distinguiendo entre ingresos y gastos.
    """
    # Verificar que el archivo es un Excel
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(
            status_code=400, detail="El archivo debe ser un Excel (.xls o .xlsx)"
        )

    # Guardar el archivo temporalmente
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    )
    try:
        contents = await file.read()
        with open(temp_file.name, "wb") as f:
            f.write(contents)

        # Procesar el archivo según el ID del banco
        if bank_id == 'bancoestado':  # BancoEstado
            saldo, movimientos = extraer_datos_bancoestado(temp_file.name)
        elif bank_id == 'bancochile':  # BancoChile
            saldo, movimientos = extraer_datos_bancochile(temp_file.name)
        elif bank_id == 'bancosantander':  # Santander
            saldo, movimientos = extraer_datos_santander(temp_file.name)
        elif bank_id == 'bancobci':  # BCI
            saldo, movimientos = extraer_datos_bci(temp_file.name)
        else:
            raise HTTPException(
                status_code=400, detail=f"ID de banco no válido: {bank_id}"
            )
        
        # Sanitizar datos para evitar errores de serialización JSON
        response_data = {
            "bank_id": bank_id,
            "balance": saldo,
            "transactions": movimientos
        }
        
        sanitized_data = sanitize_json_data(response_data)
        return sanitized_data
        
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el archivo: {str(e)}"
        )
    finally:
        # Limpiar archivos temporales
        temp_file.close()
        os.unlink(temp_file.name)


def extraer_datos_bancoestado(archivo):
    """Extrae el saldo contable y movimientos de un archivo de BancoEstado."""
    # Cargar el archivo Excel
    xls = pd.ExcelFile(archivo)
    sheet_name = xls.sheet_names[0]  # Asume que la primera hoja es la correcta
    df = pd.read_excel(xls, sheet_name=sheet_name)
    # Extraer saldo contable
    saldo_contable = df.iloc[9, 3]
    
    # Extraer movimientos (a partir de la fila 13 en adelante)
    df_movimientos = df.iloc[
        13:, [0, 1, 2, 3]
    ]  # Fecha, N° Operación, Descripción, Cargo/Abono
    
    df_movimientos.columns = ["Fecha", "N° Operación", "Descripción", "Monto"]
    
    # Filtrar filas que corresponden a subtotales o totales
    df_movimientos = df_movimientos[
        ~df_movimientos["Descripción"].astype(str).str.contains("Subtotal|SUBTOTAL|Total|TOTAL", na=False)
    ]
    
    # Filtrar filas donde la fecha no es nula (elimina filas de subtotal adicionales)
    df_movimientos = df_movimientos[df_movimientos["Fecha"].notna()]
    
    # Convertir montos a numéricos
    df_movimientos["Monto"] = pd.to_numeric(df_movimientos["Monto"], errors="coerce")
    
    # Identificar ingresos y gastos
    df_movimientos["Tipo"] = df_movimientos["Monto"].apply(
        lambda x: "Ingreso" if x > 0 else "Gasto" if x < 0 else None
    )
    
    # Filtrar registros con montos válidos y tipos identificados
    df_movimientos = df_movimientos[df_movimientos["Tipo"].notna()]
    
    # Tomar el valor absoluto de los montos
    df_movimientos["Monto"] = df_movimientos["Monto"].abs()
    
    # Convertir DataFrame a lista de diccionarios
    movimientos_bancoestado = df_movimientos.to_dict(orient="records")
    return saldo_contable, movimientos_bancoestado


def extraer_datos_bancochile(archivo):
    """Extrae el saldo contable y movimientos de un archivo de Banco de Chile."""
    try:
        logger.info("Iniciando procesamiento de archivo Banco Chile: %s", archivo)
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        logger.info("Hojas encontradas en el archivo: %s", xls.sheet_names)

        sheet_name = xls.sheet_names[0]
        logger.info("Usando hoja: %s", sheet_name)
        df = pd.read_excel(xls, sheet_name=sheet_name)
        logger.debug("Dimensiones del DataFrame: %s", df.shape)
        
        # Variables para seguimiento
        saldo_disponible = None
        header_row = None
        
        # Buscar la fila que contiene "Saldo disponible" o similar
        logger.info("Buscando información de saldo disponible...")
        for i, row in df.iterrows():
            row_str = " ".join([str(cell) for cell in row if isinstance(cell, str)])
            if "Saldo disponible" in row_str or "Saldo" in row_str:
                # Buscar el valor numérico en esta fila o en la siguiente
                for j, cell in enumerate(row):
                    # Intentar detectar el saldo a la derecha de "Saldo disponible"
                    if isinstance(cell, (int, float)) and not pd.isna(cell):
                        saldo_disponible = cell
                        logger.info(f"Saldo encontrado: {saldo_disponible}")
                        break
                    elif isinstance(cell, str) and "Saldo" in cell:
                        # El saldo podría estar en la columna siguiente
                        if j + 1 < len(row) and isinstance(row[j + 1], (int, float)):
                            saldo_disponible = row[j + 1]
                            logger.info(f"Saldo encontrado en columna siguiente: {saldo_disponible}")
                            break
                
                # Si no se encontró en esta fila, buscar en la siguiente
                if saldo_disponible is None and i + 1 < len(df):
                    next_row = df.iloc[i + 1]
                    for cell in next_row:
                        if isinstance(cell, (int, float)) and not pd.isna(cell):
                            saldo_disponible = cell
                            logger.info(f"Saldo encontrado en fila siguiente: {saldo_disponible}")
                            break
                
                if saldo_disponible is not None:
                    break

        if saldo_disponible is None:
            logger.warning("No se encontró información de saldo en el archivo")
            saldo_disponible = 0

        # Identificar la tabla de movimientos
        # Buscar encabezados comunes en tablas de movimientos bancarios
        logger.info("Buscando tabla de movimientos...")
        encabezados_posibles = ["Fecha", "Descripción", "Monto", "Cargo", "Abono", "Débito", "Crédito"]
        
        for i, row in df.iterrows():
            row_str = " ".join([str(cell) for cell in row if isinstance(cell, str)]).lower()
            # Verificar si esta fila contiene al menos dos de los encabezados posibles
            encabezados_presentes = sum(1 for h in encabezados_posibles if h.lower() in row_str)
            
            if encabezados_presentes >= 2:
                logger.info(f"Posibles encabezados encontrados en fila {i}: {row_str}")
                header_row = i
                break
        
        # Si no se encontró mediante búsqueda directa, intentar otro enfoque
        if header_row is None:
            logger.info("Intentando localizar encabezados mediante análisis de estructura...")
            # Buscar patrones de estructura típicos de tablas bancarias
            for i in range(min(20, len(df) - 5)):  # Revisar las primeras 20 filas
                if df.iloc[i:i+5].notna().sum().mean() > 2:  # Si hay al menos 2 columnas con datos
                    for j, cell in enumerate(df.iloc[i]):
                        if isinstance(cell, str) and any(h.lower() in cell.lower() for h in encabezados_posibles):
                            header_row = i
                            logger.info(f"Encabezados encontrados en fila {i} mediante análisis estructural")
                            break
                    if header_row is not None:
                        break

        # Procesar los movimientos si se encontraron encabezados
        if header_row is not None:
            logger.info(f"Extrayendo movimientos desde la fila {header_row + 1}")
            # Extraer y nombrar columnas
            df_movimientos = df.iloc[header_row + 1:].copy()
            
            # Usar los encabezados encontrados como nombres de columna
            df_movimientos.columns = df.iloc[header_row]
            
            # Buscar columnas relevantes
            columnas_fecha = [col for col in df_movimientos.columns 
                             if isinstance(col, str) and any(x.lower() in col.lower() for x in ["fecha", "date"])]
            
            columnas_descripcion = [col for col in df_movimientos.columns 
                                   if isinstance(col, str) and any(x.lower() in col.lower() for x in ["descrip", "glosa", "concepto", "detalle"])]
            
            # Buscar columnas para montos (pueden ser cargo/débito o abono/crédito)
            columnas_cargo = [col for col in df_movimientos.columns 
                             if isinstance(col, str) and any(x.lower() in col.lower() for x in ["cargo", "débito", "debito", "monto", "valor"])]
            
            columnas_abono = [col for col in df_movimientos.columns 
                             if isinstance(col, str) and any(x.lower() in col.lower() for x in ["abono", "crédito", "credito"])]
            
            logger.info(f"Columnas identificadas - Fecha: {columnas_fecha}, Descripción: {columnas_descripcion}, Cargo: {columnas_cargo}, Abono: {columnas_abono}")
            
            # Verificar que se encontraron las columnas necesarias
            if columnas_fecha and columnas_descripcion and (columnas_cargo or columnas_abono):
                # Seleccionar las primeras columnas encontradas de cada tipo
                col_fecha = columnas_fecha[0]
                col_descripcion = columnas_descripcion[0]
                
                # Crear un DataFrame base con fecha y descripción
                df_final = pd.DataFrame({
                    "Fecha": df_movimientos[col_fecha],
                    "Descripción": df_movimientos[col_descripcion],
                })
                
                # Procesar cargos (gastos)
                if columnas_cargo:
                    col_cargo = columnas_cargo[0]
                    df_final["Cargo"] = pd.to_numeric(df_movimientos[col_cargo], errors="coerce")
                else:
                    df_final["Cargo"] = 0
                
                # Procesar abonos (ingresos)
                if columnas_abono:
                    col_abono = columnas_abono[0]
                    df_final["Abono"] = pd.to_numeric(df_movimientos[col_abono], errors="coerce")
                else:
                    df_final["Abono"] = 0
                
                # Si existe una columna de monto que puede tener valores positivos (abonos) y negativos (cargos)
                if "Monto" in df_movimientos.columns or any("monto" in str(col).lower() for col in df_movimientos.columns):
                    col_monto = next((col for col in df_movimientos.columns if "monto" in str(col).lower()), None)
                    if col_monto:
                        df_final["Monto"] = pd.to_numeric(df_movimientos[col_monto], errors="coerce")
                        # Los cargos son negativos, los abonos positivos
                        df_final["Cargo"] = df_final["Cargo"].fillna(0) + df_final["Monto"].apply(lambda x: abs(x) if x < 0 else 0)
                        df_final["Abono"] = df_final["Abono"].fillna(0) + df_final["Monto"].apply(lambda x: x if x > 0 else 0)
                
                # Determinar el tipo de movimiento (Gasto o Ingreso)
                df_final["Tipo"] = "Gasto"
                df_final.loc[df_final["Abono"] > 0, "Tipo"] = "Ingreso"
                df_final.loc[df_final["Cargo"] > 0, "Tipo"] = "Gasto"
                
                # Determinar el monto final
                df_final["Monto"] = df_final["Abono"].fillna(0) + df_final["Cargo"].fillna(0)
                
                # Eliminar filas con valores nulos en columnas críticas
                df_final = df_final.dropna(subset=["Fecha", "Monto"])
                
                # Filtrar solo transacciones con montos != 0
                df_final = df_final[(df_final["Monto"] != 0) & (df_final["Monto"].notna())]
                
                # Convertir a lista de diccionarios
                movimientos_bancochile = df_final[["Fecha", "Descripción", "Monto", "Tipo"]].to_dict(orient="records")
                
                if movimientos_bancochile:
                    logger.debug(f"Ejemplo de primer movimiento: {movimientos_bancochile[0]}")
                
                return saldo_disponible, movimientos_bancochile
            else:
                logger.warning("No se encontraron todas las columnas necesarias")
                return saldo_disponible, []
        else:
            logger.warning("No se pudo identificar la tabla de movimientos")
            return saldo_disponible, []
            
    except Exception as e:
        logger.error(f"Error al procesar archivo de Banco Chile: {str(e)}", exc_info=True)
        return 0, []


def extraer_datos_santander(archivo):
    """Extrae el saldo contable y movimientos de un archivo de Banco Santander."""
    try:
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)  # Corregido de readexcel a read_excel

        # Buscar la primera fila con información de saldo
        saldo_disponible = None
        for i, row in df.iterrows():
            if "Saldo" in str(row.to_string()):
                # Intentar encontrar la columna de saldo
                for j, col_name in enumerate(df.columns):
                    if "Saldo" in str(col_name):
                        saldo_disponible = df.iloc[i, j]
                        break
                if saldo_disponible is not None:
                    break

        # Buscar las columnas con información de movimientos
        df_movimientos = None
        for i, row in df.iterrows():
            row_str = str(row.to_string()).lower()
            if any(
                col.lower() in row_str
                for col in ["Fecha", "Detalle", "Monto", "Cargo", "Abono"]
            ):
                df_movimientos = df.iloc[i + 1:].copy()
                df_movimientos.columns = df.iloc[i]
                break

        if df_movimientos is not None:
            # Mapear nombres de columnas que podrían variar
            column_mapping = {
                "Fecha": ["Fecha", "FECHA", "Fecha Transacción"],
                "Detalle": ["Detalle", "DETALLE", "Descripción", "Glosa"],
                "Cargo": ["Cargo", "CARGO", "Monto Cargo", "Débitos", "Débito"],
                "Abono": ["Abono", "ABONO", "Monto Abono", "Créditos", "Crédito"]
            }

            # Crear diccionario para almacenar las columnas encontradas
            found_columns = {}
            
            for target_col, possible_names in column_mapping.items():
                for col_name in df_movimientos.columns:
                    if any(possible in str(col_name) for possible in possible_names):
                        found_columns[target_col] = col_name
                        break
            
            # Verificar que tengamos las columnas mínimas necesarias
            if "Fecha" in found_columns and "Detalle" in found_columns and ("Cargo" in found_columns or "Abono" in found_columns):
                # Crear DataFrame con columnas estándar
                df_final = pd.DataFrame()
                df_final["Fecha"] = df_movimientos[found_columns["Fecha"]]
                df_final["Descripción"] = df_movimientos[found_columns["Detalle"]]
                
                # Inicializar columnas de cargo y abono
                df_final["Cargo"] = 0
                df_final["Abono"] = 0
                
                # Llenar columnas de cargo y abono si existen
                if "Cargo" in found_columns:
                    df_final["Cargo"] = pd.to_numeric(df_movimientos[found_columns["Cargo"]], errors="coerce").fillna(0)
                
                if "Abono" in found_columns:
                    df_final["Abono"] = pd.to_numeric(df_movimientos[found_columns["Abono"]], errors="coerce").fillna(0)
                
                # Determinar tipo y monto final
                df_final["Tipo"] = "Gasto"
                df_final.loc[df_final["Abono"] > 0, "Tipo"] = "Ingreso"  # Corregido aquí: cambiado '(' por '['
                df_final["Monto"] = df_final["Cargo"] + df_final["Abono"]
                
                # Filtrar filas con valores nulos en fecha o monto
                df_final = df_final.dropna(subset=["Fecha", "Monto"])
                
                # Filtrar transacciones con monto != 0
                df_final = df_final[df_final["Monto"] != 0]
                
                # Convertir a lista de diccionarios
                movimientos_santander = df_final[["Fecha", "Descripción", "Monto", "Tipo"]].to_dict(orient="records")
                return saldo_disponible, movimientos_santander
            else:
                return saldo_disponible, []
        else:
            return saldo_disponible, []

    except Exception as e:
        logger.error(f"Error al procesar archivo de Banco Santander: {str(e)}", exc_info=True)
        return 0, []


def extraer_datos_bci(archivo):
    """Extrae el saldo contable y movimientos de un archivo de BCI."""
    try:
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # No hay saldo para BCI según requerimientos
        saldo_bci = 0

        # Buscar columnas con información de movimientos
        header_row = None
        for i, row in df.iterrows():
            row_str = row.to_string().lower()
            if (
                "fecha" in row_str
                and any(term in row_str for term in ["transacción", "transaccion", "detalle", "descripción"])
                and any(term in row_str for term in ["cargo", "débito", "abono", "crédito", "monto"])
            ):
                header_row = i
                break

        if header_row is not None:
            df_movimientos = df.iloc[header_row + 1:].copy()
            df_movimientos.columns = df.iloc[header_row]
            
            # Mapear las columnas necesarias
            column_mapping = {
                "Fecha": ["Fecha", "Fecha Transacción", "FECHA"],
                "Descripción": ["Descripción", "DESCRIPCION", "Detalle", "Glosa"],
                "Cargo": ["Cargo", "CARGO", "Débito", "Monto Débito"],
                "Abono": ["Abono", "ABONO", "Crédito", "Monto Crédito"],
                "Monto": ["Monto", "MONTO", "Valor"]
            }
            
            # Buscar las columnas en el dataframe
            found_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col_name in df_movimientos.columns:
                    col_str = str(col_name).lower()
                    if any(possible.lower() in col_str for possible in possible_names):
                        found_columns[target_col] = col_name
                        break
            
            # Verificar que tenemos las columnas mínimas necesarias
            if "Fecha" in found_columns and "Descripción" in found_columns and any(k in found_columns for k in ["Cargo", "Abono", "Monto"]):
                # Crear DataFrame con columnas estandarizadas
                df_final = pd.DataFrame()
                df_final["Fecha"] = df_movimientos[found_columns["Fecha"]]
                df_final["Descripción"] = df_movimientos[found_columns["Descripción"]]
                
                # Inicializar columnas numéricas
                df_final["Cargo"] = 0
                df_final["Abono"] = 0
                
                # Función para convertir strings con formato de moneda chilena a números
                def parse_chilean_amount(value):
                    if pd.isna(value):
                        return 0
                    
                    # Si ya es un número, devolverlo directamente
                    if isinstance(value, (int, float)):
                        return value
                    
                    # Convertir a string si no lo es
                    value_str = str(value)
                    
                    # Reemplazar puntos (separadores de miles) y comas (separadores decimales)
                    # En Chile: 1.234,56 = 1234.56 en formato inglés
                    cleaned_value = value_str.replace('.', '').replace(',', '.')
                    
                    try:
                        return float(cleaned_value)
                    except ValueError:
                        # Si hay error, intentar extraer solo dígitos y puntos/comas
                        import re
                        numeric_chars = re.sub(r'[^\d,.]', '', value_str)
                        if numeric_chars:
                            numeric_chars = numeric_chars.replace('.', '').replace(',', '.')
                            try:
                                return float(numeric_chars)
                            except ValueError:
                                return 0
                        return 0
                
                # Procesar columnas de montos con la nueva función
                if "Cargo" in found_columns:
                    df_final["Cargo"] = df_movimientos[found_columns["Cargo"]].apply(parse_chilean_amount)
                
                if "Abono" in found_columns:
                    df_final["Abono"] = df_movimientos[found_columns["Abono"]].apply(parse_chilean_amount)
                
                # Si hay una columna de monto que puede contener valores positivos y negativos
                if "Monto" in found_columns:
                    montos = df_movimientos[found_columns["Monto"]].apply(parse_chilean_amount)
                    df_final["Cargo"] += montos.apply(lambda x: abs(x) if x < 0 else 0)
                    df_final["Abono"] += montos.apply(lambda x: x if x > 0 else 0)
                
                # Determinar el tipo de transacción
                df_final["Tipo"] = "Gasto"
                df_final.loc[df_final["Abono"] > 0, "Tipo"] = "Ingreso"
                
                # Calcular el monto final (positivo para ambos tipos)
                df_final["Monto"] = df_final["Cargo"] + df_final["Abono"]
                
                # Registrar algunos montos para verificación
                logger.debug(f"Ejemplos de montos procesados: {df_final['Monto'].head().tolist()}")
                
                # Filtrar filas con valores nulos y montos cero
                df_final = df_final.dropna(subset=["Fecha", "Monto"])
                df_final = df_final[df_final["Monto"] != 0]
                
                # Convertir a lista de diccionarios
                movimientos_bci = df_final[["Fecha", "Descripción", "Monto", "Tipo"]].to_dict(orient="records")
                return saldo_bci, movimientos_bci
            else:
                return saldo_bci, []
        else:
            return saldo_bci, []
    except Exception as e:
        logger.error(f"Error al procesar archivo de BCI: {str(e)}", exc_info=True)
        return 0, []


# Modelo para recibir transacciones en masa
class TransactionInput(BaseModel):
    fecha: Union[str, date, datetime]
    descripcion: str
    monto: float
    categoria: Optional[str] = "Sin clasificar"
    banco_id: Optional[int] = None
    tipo: Optional[str] = None  # Agregamos el campo tipo como opcional

class BulkTransactionResponse(BaseModel):
    total_recibidas: int
    insertadas: int
    duplicadas: int
    transacciones_insertadas: List[Transaction_Pydantic]

@router.post("/bulk-transactions", response_model=BulkTransactionResponse)
async def create_bulk_transactions(transactions: List[TransactionInput] = Body(...)):
    """
    Inserta múltiples transacciones evitando duplicados.
    
    Recibe un array de transacciones y las inserta en la base de datos,
    verificando que no existan duplicados por fecha, descripción y monto.
    
    Returns:
        Un resumen con el total de transacciones recibidas, insertadas y duplicadas.
    """
    if not transactions:
        raise HTTPException(status_code=400, detail="No se recibieron transacciones")
    
    # Convertimos todas las fechas al formato de la base de datos
    processed_transactions = []
    for t in transactions:
        # Convertir la fecha si viene como string
        if isinstance(t.fecha, str):
            try:
                # Intentar varios formatos de fecha comunes
                for date_format in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        parsed_date = datetime.strptime(t.fecha, date_format).date()
                        break
                    except ValueError:
                        continue
                else:  # Si ningún formato funciona
                    raise ValueError(f"Formato de fecha no reconocido: {t.fecha}")
            except Exception as e:
                logger.error(f"Error al procesar fecha {t.fecha}: {str(e)}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error en formato de fecha: {t.fecha}. Use formato YYYY-MM-DD."
                )
        else:
            # Si es datetime, convertir a date
            if isinstance(t.fecha, datetime):
                parsed_date = t.fecha.date()
            else:
                parsed_date = t.fecha
        
        # Asegurar que el monto sea un valor decimal, respetando el signo
        # Valores negativos para gastos, siguiendo la convención establecida
        monto = float(t.monto)
        
        # Determinar el tipo basado en el monto si no viene especificado
        tipo = t.tipo or ("Gasto" if monto < 0 else "Ingreso")
                
        processed_transactions.append({
            "transaction_date": parsed_date,
            "description": t.descripcion,
            "amount": monto,  # Preservamos el signo y valor original
            "category": t.categoria,
            "bank_id": t.banco_id,
            "tipo": tipo  # Usamos el tipo determinado
        })
    
    # Verificar duplicados y crear nuevas transacciones
    inserted_transactions = []
    duplicates_count = 0
    
    for trans_data in processed_transactions:
        # Buscar si ya existe una transacción igual por fecha, descripción y monto
        existing = await Transaction.filter(
            transaction_date=trans_data["transaction_date"],
            description=trans_data["description"],
            amount=trans_data["amount"]
        ).first()
        
        if existing:
            duplicates_count += 1
            logger.info(f"Transacción duplicada: {trans_data}")
            continue
        
        # Si no existe, crear nueva transacción
        transaction_obj = await Transaction.create(**trans_data)
        trans_pydantic = await Transaction_Pydantic.from_tortoise_orm(transaction_obj)
        inserted_transactions.append(trans_pydantic)
        
    return {
        "total_recibidas": len(transactions),
        "insertadas": len(inserted_transactions),
        "duplicadas": duplicates_count,
        "transacciones_insertadas": inserted_transactions
    }

# Agregar este nuevo modelo para la respuesta de transacciones mensuales con tipo
class TransactionWithType(BaseModel):
    id: int
    transaction_date: date
    description: str
    amount: float
    category: Optional[str] = None
    bank_id: Optional[int] = None
    tipo: str  # Campo adicional para el tipo (Ingreso/Gasto)

@router.get("/transactions-by-month", response_model=List[TransactionWithType])
async def get_transactions_by_month(
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., ge=2000, le=2100, description="Año (2000-2100)")
):
    """
    Obtiene las transacciones de un mes específico.
    
    - **month**: Número del mes (1-12)
    - **year**: Año (formato YYYY)
    
    Returns:
        Lista de transacciones correspondientes al mes y año especificados.
    """
    try:
        # Calcular el último día del mes
        last_day = calendar.monthrange(year, month)[1]
        
        # Crear fechas de inicio y fin para el filtro
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # Filtrar transacciones por el rango de fechas
        query = Transaction.filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).order_by('transaction_date')
        
        # Obtener transacciones
        transactions = await Transaction_Pydantic.from_queryset(query)
        
        # Procesar las transacciones para agregar el campo tipo y formatear los montos
        processed_transactions = []
        for transaction in transactions:
            # Convertir a diccionario para manipulación
            trans_dict = transaction.dict()
            
            # Eliminar decimales en el campo amount
            trans_dict["amount"] = int(trans_dict["amount"])
            
            # Agregar campo tipo basado en el monto
            trans_dict["tipo"] = "Gasto" if trans_dict["amount"] < 0 else "Ingreso"
            
            # Agregar a la lista como instancia del nuevo modelo
            processed_transactions.append(TransactionWithType(**trans_dict))
        
        return processed_transactions
    
    except Exception as e:
        logger.error(f"Error al obtener transacciones por mes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener transacciones: {str(e)}"
        )

# Agregar este nuevo modelo para la respuesta agrupada
class TransactionGroup(BaseModel):
    description: str
    total_amount: int
    count: int

@router.get("/transactions-grouped-by-month", response_model=List[TransactionGroup])
async def get_transactions_grouped_by_month(
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., ge=2000, le=2100, description="Año (2000-2100)")
):
    """
    Obtiene las transacciones de un mes específico agrupadas por descripción.
    
    - **month**: Número del mes (1-12)
    - **year**: Año (formato YYYY)
    
    Returns:
        Lista de transacciones agrupadas por descripción con el total y conteo de cada grupo.
    """
    try:
        # Calcular el último día del mes
        last_day = calendar.monthrange(year, month)[1]
        
        # Crear fechas de inicio y fin para el filtro
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # Filtrar transacciones por el rango de fechas
        transactions = await Transaction.filter(
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).values('description', 'amount')
        
        # Agrupar por descripción
        grouped_data = {}
        for trans in transactions:
            description = trans['description']
            amount = trans['amount']
            
            if description not in grouped_data:
                grouped_data[description] = {
                    'total_amount': 0,
                    'count': 0
                }
            
            grouped_data[description]['total_amount'] += amount
            grouped_data[description]['count'] += 1
        
        # Formatear los resultados como una lista de objetos
        result = [
            {
                'description': desc,
                'total_amount': int(data['total_amount']),  # Eliminar decimales
                'count': data['count']
            }
            for desc, data in grouped_data.items()
        ]
        
        # Ordenar por monto total (mayor a menor)
        result.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return result
    
    except Exception as e:
        logger.error(f"Error al obtener transacciones agrupadas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener transacciones agrupadas: {str(e)}"
        )
