import os
import argparse
import json
from scripts.procesar_excel import extraer_datos
from scripts.actualizar_gsheet import actualizar_movimientos

def cargar_configuracion():
    """Carga la configuración desde el archivo settings.json"""
    try:
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Archivo de configuración no encontrado. Creando uno nuevo...")
        crear_configuracion_inicial()
        return {}
    except json.JSONDecodeError:
        print("Error al leer el archivo de configuración. Formato incorrecto.")
        return {}

def crear_configuracion_inicial():
    """Crea un archivo de configuración inicial si no existe"""
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_file = os.path.join(config_dir, 'settings.json')
    config_data = {
        "spreadsheet_id": "",
        "bancos": {
            "bancoestado": {"nombre_hoja": "BancoEstado"},
            "bancochile": {"nombre_hoja": "BancoChile"},
            "bancosantander": {"nombre_hoja": "BancoSantander"},
            "bci": {"nombre_hoja": "BCI"}
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=4)
    
    print(f"Archivo de configuración creado en {config_file}")
    print("Por favor, edite el archivo y agregue su ID de Google Spreadsheet")

def procesar_archivos(directorio, banco=None):
    """Procesa los archivos Excel del directorio y actualiza Google Sheets"""
    config = cargar_configuracion()
    
    if not config.get("spreadsheet_id"):
        print("Error: ID de Google Spreadsheet no configurado. Edite el archivo config/settings.json")
        return
    
    if not os.path.exists(directorio):
        print(f"Error: El directorio {directorio} no existe")
        return
    
    # Extensiones de archivo a procesar
    extensiones = ['.xls', '.xlsx']
    
    # Filtrar archivos por banco si se especifica
    for archivo in os.listdir(directorio):
        nombre_archivo = archivo.lower()
        ruta_completa = os.path.join(directorio, archivo)
        
        # Verificar que sea un archivo Excel
        if not any(nombre_archivo.endswith(ext) for ext in extensiones):
            continue
        
        # Determinar el banco según el nombre del archivo
        banco_detectado = None
        if "bancoestado" in nombre_archivo:
            banco_detectado = "bancoestado"
        elif "bancochile" in nombre_archivo:
            banco_detectado = "bancochile"
        elif "bancosantander" in nombre_archivo:
            banco_detectado = "bancosantander"
        elif "bci" in nombre_archivo:
            banco_detectado = "bci"
        else:
            print(f"No se pudo determinar el banco para el archivo: {archivo}")
            continue
        
        # Si se especificó un banco y no coincide, saltar este archivo
        if banco and banco.lower() != banco_detectado:
            continue
        
        try:
            # Procesar el archivo
            print(f"Procesando archivo: {archivo} (Banco: {banco_detectado})")
            saldo, movimientos = extraer_datos(ruta_completa)
            
            # Obtener el nombre de la hoja para este banco
            nombre_hoja = config.get("bancos", {}).get(banco_detectado, {}).get("nombre_hoja", banco_detectado.capitalize())
            
            # Actualizar Google Sheets
            actualizar_movimientos(nombre_hoja, banco_detectado, saldo, movimientos)
            
        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesa archivos Excel de bancos y actualiza Google Sheets")
    parser.add_argument("--directorio", "-d", type=str, default="data", 
                       help="Directorio que contiene los archivos Excel (por defecto: 'data')")
    parser.add_argument("--banco", "-b", type=str, choices=["bancoestado", "bancochile", "bancosantander", "bci"],
                       help="Procesar solo archivos de un banco específico")
    
    args = parser.parse_args()
    
    # Convertir ruta relativa a absoluta
    directorio_absoluto = os.path.join(os.path.dirname(__file__), args.directorio)
    
    # Crear directorio de datos si no existe
    if not os.path.exists(directorio_absoluto):
        os.makedirs(directorio_absoluto)
        print(f"Directorio {directorio_absoluto} creado. Coloque sus archivos Excel aquí.")
    
    # Procesar archivos
    procesar_archivos(directorio_absoluto, args.banco)
