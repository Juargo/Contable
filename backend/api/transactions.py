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
    # Filtrar solo los cargos (valores negativos) y eliminar cargos nulos o cero
    df_movimientos = df_movimientos[
        (pd.to_numeric(df_movimientos["Cargo"], errors="coerce") < 0)
        & (pd.to_numeric(df_movimientos["Cargo"], errors="coerce").notnull())
        & (pd.to_numeric(df_movimientos["Cargo"], errors="coerce") != 0)
    ]
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
        logger.debug("Primeras 5 filas: \n %s", {df.head()})
        # Variables para seguimiento
        saldo_disponible = None
        header_row = None
        # Buscar la fila que contiene "Saldo disponible"
        logger.info("Buscando información de 'Saldo disponible'...")
        for i, row in df.iterrows():
            for j, cell in enumerate(row):
                logger.debug("Fila %d, Columna %d, Valor: %s", i, j, cell)
                if isinstance(cell, str) and "Saldo disponible" in cell:
                    saldo_disponible = df.iloc[
                        i, j + 1
                    ]  # El valor está en la columna siguiente
                    logger.info(
                        "Saldo disponible encontrado en fila %d, columna %d: %s",
                        i,
                        j + 1,
                        saldo_disponible,
                    )
                    break

        if saldo_disponible is None:
            logger.warning("No se encontró 'Saldo disponible' en el archivo")

        # Identificar la tabla de movimientos
        # Buscamos la fila que contiene los encabezados
        logger.info("Buscando encabezados de tabla de movimientos...")
        for i, row in df.iterrows():
            row_str = " ".join([str(cell) for cell in row if isinstance(cell, str)])
            logger.debug("Fila %d, Contenido: %s", i, row_str)

            for j, cell in enumerate(row):
                if isinstance(cell, str) and "Fecha" in cell:
                    header_row = i
                    logger.info("Encabezado de tabla encontrado en fila %d", i)
                    logger.debug("Encabezados: %s", [str(h) for h in df.iloc[i]])
                    break

            if header_row is not None:
                break

        # Extraer los movimientos
        if header_row is not None:
            logger.info("Extrayendo movimientos desde la fila %d", header_row + 1)
            df_movimientos = df.iloc[header_row + 1 :].copy()
            df_movimientos.columns = df.iloc[header_row]

            logger.debug("Columnas disponibles: %s", list(df_movimientos.columns))

            # Seleccionamos las columnas de interés
            columns_interest = ["Fecha", "Descripción", "Cargo"]
            existing_columns = [
                col for col in columns_interest if col in df_movimientos.columns
            ]

            logger.info("Columnas seleccionadas: %s", existing_columns)

            if existing_columns:
                df_movimientos = df_movimientos[existing_columns]

                # Filtrar solo cargos (valores negativos o columna específica)
                if "Cargo" in df_movimientos.columns:
                    # Mostrar ejemplos de valores en la columna Cargo
                    cargo_examples = df_movimientos["Cargo"].head(10).tolist()
                    logger.debug(
                        "Ejemplos de valores en columna Cargo: %s", cargo_examples
                    )

                    df_movimientos["Cargo_num"] = pd.to_numeric(
                        df_movimientos["Cargo"], errors="coerce"
                    )
                    filtered_df = df_movimientos[
                        (df_movimientos["Cargo_num"] < 0)
                        & (df_movimientos["Cargo_num"].notnull())
                        & (df_movimientos["Cargo_num"] != 0)
                    ]

                    logger.info("Registros antes del filtrado: %d", len(df_movimientos))
                    logger.info(
                        "Registros después del filtrado de cargos negativos: %d",
                        len(filtered_df),
                    )

                    df_movimientos = filtered_df
                    df_movimientos = df_movimientos.drop(
                        "Cargo_num", axis=1, errors="ignore"
                    )

                # Convertir DataFrame a lista de diccionarios
                movimientos_bancochile = df_movimientos.to_dict(orient="records")
                logger.info(
                    "Total de movimientos encontrados: %d", len(movimientos_bancochile)
                )

                # Mostrar ejemplos de movimientos
                if movimientos_bancochile:
                    logger.debug(
                        "Ejemplo de primer movimiento: %s", movimientos_bancochile[0]
                    )
            else:
                logger.warning("No se encontraron las columnas de interés en los datos")
                movimientos_bancochile = []
        else:
            logger.warning("No se encontraron encabezados de tabla en el archivo")
            movimientos_bancochile = []

        logger.info(
            "Procesamiento de Banco Chile completado. Saldo: %s, Movimientos: %d",
            saldo_disponible,
            len(movimientos_bancochile),
        )
        return saldo_disponible, movimientos_bancochile
    except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError) as e:
        logger.error("Error al procesar archivo de Banco Chile: %s", e, exc_info=True)
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
                
        processed_transactions.append({
            "transaction_date": parsed_date,
            "description": t.descripcion,
            "amount": t.monto,
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
        
        # Utilizar from_queryset en lugar de convertir a lista
        return await Transaction_Pydantic.from_queryset(query)
    
    except Exception as e:
        logger.error(f"Error al obtener transacciones por mes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener transacciones: {str(e)}"
        )
