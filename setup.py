""" Archivo de configuración de setuptools para instalar el paquete contable. """

try:
    from setuptools import setup, find_packages
except ImportError:
    print("ERROR: setuptools no está instalado.")
    print("Por favor, instala setuptools primero:")
    print("pip install setuptools")
    print("\nAlternativamente, puedes instalar las dependencias directamente:")
    print("pip install -r requirements.txt")
    import sys
    sys.exit(1)

setup(
    name="contable",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "gspread>=5.0.0",
        "oauth2client>=4.1.3",
        "prettytable>=2.0.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Sistema de procesamiento de extractos bancarios y actualización a Google Sheets",
    keywords="excel, bank, sheets, finance",
    python_requires=">=3.6",
)
