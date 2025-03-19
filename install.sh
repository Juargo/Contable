#!/bin/bash

echo "Instalando dependencias para Contable..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null
then
    echo "Python 3 no está instalado. Por favor instala Python 3 antes de continuar."
    exit 1
fi

# Verificar virtualenv
echo "Verificando virtualenv..."
python3 -m pip install virtualenv

# Crear entorno virtual
echo "Creando entorno virtual..."
python3 -m virtualenv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar setuptools primero
echo "Instalando setuptools..."
pip install setuptools

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Verificar instalación
echo "Verificando instalación de pandas..."
python -c "import pandas; print('Pandas versión:', pandas.__version__)"

echo "Instalación completada."
echo "Para activar el entorno virtual, ejecuta:"
echo "source venv/bin/activate"
