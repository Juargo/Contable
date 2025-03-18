import pandas as pd
import argparse

def extraer_datos(archivo):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae saldo contable y movimientos de un archivo Excel de BancoEstado.")
    parser.add_argument("archivo", type=str, help="Ruta del archivo Excel")
    args = parser.parse_args()
    
    saldo, movimientos = extraer_datos(args.archivo)
    
    print(f"Saldo Contable: {saldo}")
    print("Movimientos:")
    for mov in movimientos:
        print(mov)
