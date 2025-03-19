"""
Script de instalación alternativo que instala directamente las dependencias
sin necesidad de usar setuptools.
"""
import subprocess
import sys
import os

def check_python():
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 6):
        print("ERROR: Se requiere Python 3.6 o superior")
        sys.exit(1)
    print(f"Usando Python {sys.version}")

def install_dependencies():
    """Instala las dependencias desde requirements.txt"""
    print("Instalando dependencias...")
    
    # Lista de paquetes con versiones mínimas
    packages = [
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "gspread>=5.0.0",
        "oauth2client>=4.1.3",
        "prettytable>=2.0.0",
    ]
    
    for package in packages:
        print(f"Instalando {package}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"ERROR: No se pudo instalar {package}")
            return False
    
    return True

def verify_installation():
    """Verifica que los paquetes se hayan instalado correctamente"""
    try:
        import pandas
        print(f"pandas {pandas.__version__} instalado correctamente")
        
        import openpyxl
        print(f"openpyxl {openpyxl.__version__} instalado correctamente")
        
        import gspread
        print(f"gspread {gspread.__version__} instalado correctamente")
        
        import oauth2client
        print(f"oauth2client {oauth2client.__version__} instalado correctamente")
        
        import prettytable
        print(f"prettytable {prettytable.__version__} instalado correctamente")
        
        return True
    except ImportError as e:
        print(f"ERROR: {e}")
        return False

def setup_project():
    """Configura los directorios necesarios para el proyecto"""
    # Crear directorio de datos
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Directorio {data_dir} creado")
    
    # Crear directorio de configuración
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"Directorio {config_dir} creado")
    
    # Crear archivo de configuración si no existe
    config_file = os.path.join(config_dir, "settings.json")
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write('''
{
    "spreadsheet_id": "", 
    "bancos": {
        "bancoestado": {
            "nombre_hoja": "BancoEstado"
        },
        "bancochile": {
            "nombre_hoja": "BancoChile"
        },
        "bancosantander": {
            "nombre_hoja": "BancoSantander"
        },
        "bci": {
            "nombre_hoja": "BCI"
        }
    }
}''')
        print(f"Archivo de configuración creado: {config_file}")
        print("Recuerda establecer el ID de la hoja de Google en settings.json")

if __name__ == "__main__":
    print("=== Instalación directa de dependencias para Contable ===")
    
    check_python()
    
    if install_dependencies():
        print("\nDependencias instaladas correctamente.")
        
        if verify_installation():
            print("\nVerificación completada exitosamente.")
            setup_project()
            print("\nInstalación finalizada. Ahora puedes ejecutar:")
            print("python run.py")
        else:
            print("\nVerificación fallida. Por favor revisa los errores.")
    else:
        print("\nInstalación fallida. Por favor revisa los errores.")
