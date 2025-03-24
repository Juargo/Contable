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
    bank_id: int = Form(...),
):
    """
    Recibe y procesa un archivo Excel de banco.

    - **file**: Archivo Excel del banco
    - **bank_id**: ID del banco (1: BancoEstado, 2: BancoChile, 3: Santander, 4: BCI)

    Retorna el saldo contable y los movimientos extraídos del archivo.
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
        if bank_id == 2:  # BancoEstado
            saldo, movimientos = extraer_datos_bancoestado(temp_file.name)
        elif bank_id == 11:  # BancoChile
            saldo, movimientos = extraer_datos_bancochile(temp_file.name)
        elif bank_id == 1:  # Santander
            saldo, movimientos = extraer_datos_santander(temp_file.name)
        elif bank_id == 3:  # BCI
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
    ]  # Fecha, N° Operación, Descripción, Cargo
    df_movimientos.columns = ["Fecha", "N° Operación", "Descripción", "Cargo"]
    
    # Filtrar filas que corresponden a subtotales o totales
    # Típicamente estas filas tienen la palabra "Subtotal", "Total" o están vacías en la columna Fecha
    df_movimientos = df_movimientos[
        ~df_movimientos["Descripción"].astype(str).str.contains("Subtotal|SUBTOTAL|Total|TOTAL", na=False)
    ]
    
    # Filtrar solo los cargos (valores negativos) y eliminar cargos nulos o cero
    df_movimientos = df_movimientos[
        (pd.to_numeric(df_movimientos["Cargo"], errors="coerce") < 0)
        & (pd.to_numeric(df_movimientos["Cargo"], errors="coerce").notnull())
        & (pd.to_numeric(df_movimientos["Cargo"], errors="coerce") != 0)
    ]
    
    # Convertir los cargos a valores positivos
    df_movimientos["Cargo"] = pd.to_numeric(df_movimientos["Cargo"], errors="coerce").abs()
    
    # Filtrar filas donde la fecha no es nula (elimina filas de subtotal adicionales)
    df_movimientos = df_movimientos[df_movimientos["Fecha"].notna()]
    
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
        encabezados_posibles = ["Fecha", "Descripción", "Monto", "Cargo", "Débito"]
        
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
            
            # Buscar columnas relevantes: fecha, descripción, y monto negativo (cargo/débito)
            columnas_fecha = [col for col in df_movimientos.columns 
                             if isinstance(col, str) and any(x.lower() in col.lower() for x in ["fecha", "date"])]
            
            columnas_descripcion = [col for col in df_movimientos.columns 
                                   if isinstance(col, str) and any(x.lower() in col.lower() for x in ["descrip", "glosa", "concepto", "detalle"])]
            
            columnas_cargo = [col for col in df_movimientos.columns 
                             if isinstance(col, str) and any(x.lower() in col.lower() for x in ["cargo", "débito", "debito", "monto", "valor"])]
            
            logger.info(f"Columnas identificadas - Fecha: {columnas_fecha}, Descripción: {columnas_descripcion}, Cargo: {columnas_cargo}")
            
            # Verificar que se encontraron las columnas necesarias
            if columnas_fecha and columnas_descripcion and columnas_cargo:
                # Seleccionar las primeras columnas encontradas de cada tipo
                col_fecha = columnas_fecha[0]
                col_descripcion = columnas_descripcion[0]
                col_cargo = columnas_cargo[0]
                
                # Crear un DataFrame con las columnas de interés y nombres estandarizados
                df_final = pd.DataFrame({
                    "Fecha": df_movimientos[col_fecha],
                    "Descripción": df_movimientos[col_descripcion],
                    "Cargo": df_movimientos[col_cargo]
                })
                
                # Eliminar filas con valores nulos en columnas críticas
                df_final = df_final.dropna(subset=["Fecha", "Cargo"])
                
                # Convertir la columna "Cargo" a numérico
                df_final["Cargo"] = pd.to_numeric(df_final["Cargo"], errors="coerce")
                
                # Filtrar solo cargos negativos (gastos)
                df_cargos = df_final[(df_final["Cargo"] < 0) & (df_final["Cargo"].notna())]
                
                # Convertir cargos a valores positivos
                df_cargos["Cargo"] = df_cargos["Cargo"].abs()
                
                logger.info(f"Total de movimientos de cargo encontrados: {len(df_cargos)}")
                
                # Convertir a lista de diccionarios
                movimientos_bancochile = df_cargos.to_dict(orient="records")
                
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
        df = pd.read_excel(xls, sheet_name=sheet_name)

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
            if any(
                col in str(row.to_string())
                for col in ["Fecha", "Detalle", "Monto", "Cargo"]
            ):
                df_movimientos = df.iloc[i + 1 :].copy()
                df_movimientos.columns = df.iloc[i]
                break

        if df_movimientos is not None:
            # Mapear nombres de columnas que podrían variar
            column_mapping = {
                "Fecha": ["Fecha", "FECHA", "Fecha Transacción"],
                "Detalle": ["Detalle", "DETALLE", "Descripción", "Glosa"],
                "Cargo": ["Cargo", "CARGO", "Monto Cargo", "Débitos", "Débito"],
            }

            selected_columns = []
            column_names = []

            for target_col, possible_names in column_mapping.items():
                for col_name in df_movimientos.columns:
                    if any(possible in str(col_name) for possible in possible_names):
                        selected_columns.append(col_name)
                        column_names.append(target_col)
                        break

            if selected_columns:
                df_movimientos = df_movimientos[selected_columns]
                df_movimientos.columns = column_names

                # Filtrar solo cargos (valores negativos) y eliminar cargos nulos o cero
                if "Cargo" in df_movimientos.columns:
                    cargo_num = pd.to_numeric(df_movimientos["Cargo"], errors="coerce")
                    df_movimientos = df_movimientos[
                        (cargo_num < 0) & (cargo_num.notnull()) & (cargo_num != 0)
                    ]

                # Convertir DataFrame a lista de diccionarios
                movimientos_santander = df_movimientos.to_dict(orient="records")
            else:
                movimientos_santander = []
        else:
            movimientos_santander = []

        return saldo_disponible, movimientos_santander
    except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError) as e:
        print(f"Error al procesar archivo de Banco Santander: {e}")
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
                and "transacción" in row_str
                and "descripción" in row_str
            ):
                header_row = i
                break

        if header_row is not None:
            df_movimientos = df.iloc[header_row + 1 :].copy()
            df_movimientos.columns = df.iloc[header_row]

            # Mapear las columnas necesarias
            column_mapping = {
                "Fecha": ["Fecha", "Fecha Transacción", "FECHA"],
                "Descripción": ["Descripción", "DESCRIPCION", "Detalle"],
                "Cargo": ["Cargo", "CARGO", "Monto", "Débito"],
            }

            selected_columns = []
            column_names = []

            for target_col, possible_names in column_mapping.items():
                for col_name in df_movimientos.columns:
                    if any(possible in str(col_name) for possible in possible_names):
                        selected_columns.append(col_name)
                        column_names.append(target_col)
                        break

            if selected_columns:
                df_movimientos = df_movimientos[selected_columns]
                df_movimientos.columns = column_names

                # Filtrar solo cargos (valores no nulos y diferentes de cero)
                if "Cargo" in df_movimientos.columns:
                    cargo_num = pd.to_numeric(df_movimientos["Cargo"], errors="coerce")
                    df_movimientos = df_movimientos[
                        (cargo_num.notnull()) & (cargo_num != 0)
                    ]

                # Convertir DataFrame a lista de diccionarios
                movimientos_bci = df_movimientos.to_dict(orient="records")
            else:
                movimientos_bci = []
        else:
            movimientos_bci = []

        return saldo_bci, movimientos_bci
    except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError) as e:
        print(f"Error al procesar archivo de BCI: {e}")
        return 0, []


# Modelo para recibir transacciones en masa
class TransactionInput(BaseModel):
    fecha: Union[str, date, datetime]
    descripcion: str
    monto: float
    categoria: Optional[str] = "Sin clasificar"
    banco_id: Optional[int] = None

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
                
        processed_transactions.append({
            "transaction_date": parsed_date,
            "description": t.descripcion,
            "amount": monto,  # Preservamos el signo y valor original
            "category": t.categoria,
            "bank_id": t.banco_id
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

@router.get("/transactions-by-month", response_model=List[Transaction_Pydantic])
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
        
        # Eliminar decimales en el campo amount
        for transaction in transactions:
            transaction.amount = int(transaction.amount)
        
        return transactions
    
    except Exception as e:
        logger.error(f"Error al obtener transacciones por mes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener transacciones: {str(e)}"
        )
