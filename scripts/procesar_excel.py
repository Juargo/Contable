import pandas as pd
import argparse
import os

def extraer_datos(archivo):
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
    # Cargar el archivo Excel
    xls = pd.ExcelFile(archivo)
    sheet_name = xls.sheet_names[0]  # Asume que la primera hoja es la correcta
    df = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Extraer saldo contable
    saldo_contable = df.iloc[9, 3]
    
    # Extraer movimientos (a partir de la fila 13 en adelante)
    df_movimientos = df.iloc[13:, [0, 1, 2, 3]]  # Fecha, N° Operación, Descripción, Cargo
    df_movimientos.columns = ["Fecha", "N° Operación", "Descripción", "Cargo"]
    
    # Filtrar solo los cargos (valores negativos)
    df_movimientos = df_movimientos[pd.to_numeric(df_movimientos["Cargo"], errors='coerce') < 0]
    
    # Convertir DataFrame a lista de diccionarios
    movimientos = df_movimientos.to_dict(orient="records")
    
    return saldo_contable, movimientos

def extraer_datos_bancochile(archivo):
    try:
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Buscar la fila que contiene "Saldo disponible"
        for i, row in df.iterrows():
            for j, cell in enumerate(row):
                if isinstance(cell, str) and "Saldo disponible" in cell:
                    saldo_disponible = df.iloc[i, j+1]  # El valor está en la columna siguiente
                    break
        
        # Identificar la tabla de movimientos
        # Buscamos la fila que contiene los encabezados
        header_row = None
        for i, row in df.iterrows():
            for cell in row:
                if isinstance(cell, str) and "Fecha" in cell:
                    header_row = i
                    break
            if header_row is not None:
                break
        
        # Extraer los movimientos
        if header_row is not None:
            df_movimientos = df.iloc[header_row+1:].copy()
            df_movimientos.columns = df.iloc[header_row]
            
            # Seleccionamos las columnas de interés
            columns_interest = ["Fecha", "Descripción", "Cargo"]
            existing_columns = [col for col in columns_interest if col in df_movimientos.columns]
            df_movimientos = df_movimientos[existing_columns]
            
            # Filtrar solo cargos (valores negativos o columna específica)
            if "Cargo" in df_movimientos.columns:
                df_movimientos = df_movimientos[pd.to_numeric(df_movimientos["Cargo"], errors='coerce') < 0]
            
            # Convertir DataFrame a lista de diccionarios
            movimientos = df_movimientos.to_dict(orient="records")
        else:
            movimientos = []
        
        return saldo_disponible, movimientos
    except Exception as e:
        print(f"Error al procesar archivo de BancoChile: {e}")
        return 0, []

def extraer_datos_santander(archivo):
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
            if any(col in str(row.to_string()) for col in ["Fecha", "Detalle", "Monto", "Cargo"]):
                df_movimientos = df.iloc[i+1:].copy()
                df_movimientos.columns = df.iloc[i]
                break
        
        if df_movimientos is not None:
            # Mapear nombres de columnas que podrían variar
            column_mapping = {
                "Fecha": ["Fecha", "FECHA", "Fecha Transacción"],
                "Detalle": ["Detalle", "DETALLE", "Descripción", "Glosa"],
                "Cargo": ["Cargo", "CARGO", "Monto Cargo", "Débitos", "Débito"]
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
                
                # Filtrar solo cargos (valores negativos)
                if "Cargo" in df_movimientos.columns:
                    df_movimientos = df_movimientos[pd.to_numeric(df_movimientos["Cargo"], errors='coerce') < 0]
                
                # Convertir DataFrame a lista de diccionarios
                movimientos = df_movimientos.to_dict(orient="records")
            else:
                movimientos = []
        else:
            movimientos = []
        
        return saldo_disponible, movimientos
    except Exception as e:
        print(f"Error al procesar archivo de Banco Santander: {e}")
        return 0, []

def extraer_datos_bci(archivo):
    try:
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # No hay saldo para BCI según requerimientos
        saldo = 0
        
        # Buscar columnas con información de movimientos
        header_row = None
        for i, row in df.iterrows():
            row_str = row.to_string().lower()
            if "fecha" in row_str and "transacción" in row_str and "descripción" in row_str:
                header_row = i
                break
        
        if header_row is not None:
            df_movimientos = df.iloc[header_row+1:].copy()
            df_movimientos.columns = df.iloc[header_row]
            
            # Mapear las columnas necesarias
            column_mapping = {
                "Fecha": ["Fecha", "Fecha Transacción", "FECHA"],
                "Descripción": ["Descripción", "DESCRIPCION", "Detalle"],
                "Cargo": ["Cargo", "CARGO", "Monto", "Débito"]
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
                
                # Filtrar solo cargos (valores negativos o positivos según el formato)
                if "Cargo" in df_movimientos.columns:
                    # Asumimos que en BCI los cargos son positivos (verificar con muestras reales)
                    df_movimientos = df_movimientos[pd.to_numeric(df_movimientos["Cargo"], errors='coerce') != 0]
                
                # Convertir DataFrame a lista de diccionarios
                movimientos = df_movimientos.to_dict(orient="records")
            else:
                movimientos = []
        else:
            movimientos = []
        
        return saldo, movimientos
    except Exception as e:
        print(f"Error al procesar archivo de BCI: {e}")
        return 0, []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae saldo contable y movimientos de un archivo Excel de banco.")
    parser.add_argument("archivo", type=str, help="Ruta del archivo Excel")
    args = parser.parse_args()
    
    saldo, movimientos = extraer_datos(args.archivo)
    
    print(f"Saldo: {saldo}")
    print("Movimientos:")
    for mov in movimientos:
        print(mov)
