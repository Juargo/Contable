"""Procesamiento de archivos Excel de bancos para extraer saldo contable y movimientos"""

import argparse
import os
import logging
import sys
import pandas as pd

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("contable")


def extraer_datos(archivo):
    """Extrae el saldo contable y movimientos de un archivo Excel de banco."""
    # Identificar el banco según el nombre del archivo
    nombre_archivo = os.path.basename(archivo).lower()
    if "bancoestado" in nombre_archivo:
        return extraer_datos_bancoestado(archivo)
    elif "bancochile" in nombre_archivo:
        return extraer_datos_bancochile(archivo)
    elif "bancosantander" in nombre_archivo:
        return extraer_datos_santander(archivo)
    elif "bci" in nombre_archivo:
        return extraer_datos_bci(archivo)
    else:
        raise ValueError(f"Formato de banco no reconocido para el archivo: {archivo}")


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
        (pd.to_numeric(df_movimientos["Cargo"], errors="coerce") < 0) &
        (pd.to_numeric(df_movimientos["Cargo"], errors="coerce").notnull()) &
        (pd.to_numeric(df_movimientos["Cargo"], errors="coerce") != 0)
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

                    # Intentar convertir a numérico y filtrar (eliminando también los cargos nulos o cero)
                    df_movimientos["Cargo_num"] = pd.to_numeric(
                        df_movimientos["Cargo"], errors="coerce"
                    )
                    filtered_df = df_movimientos[
                        (df_movimientos["Cargo_num"] < 0) &
                        (df_movimientos["Cargo_num"].notnull()) &
                        (df_movimientos["Cargo_num"] != 0)
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
                logger.info("Total de movimientos encontrados: %d", len(movimientos_bancochile))

                # Mostrar ejemplos de movimientos
                if movimientos_bancochile:
                    logger.debug("Ejemplo de primer movimiento: %s", movimientos_bancochile[0])
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
                        (cargo_num < 0) &
                        (cargo_num.notnull()) &
                        (cargo_num != 0)
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
                        (cargo_num.notnull()) &
                        (cargo_num != 0)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrae saldo contable y movimientos de un archivo Excel de banco."
    )
    parser.add_argument("archivo", type=str, help="Ruta del archivo Excel")
    args = parser.parse_args()

    saldo, movimientos = extraer_datos(args.archivo)

    print(f"Saldo: {saldo}")
    print("Movimientos:")
    for mov in movimientos:
        print(mov)
