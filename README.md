# Contable

Sistema de procesamiento de extractos bancarios y actualización a Google Sheets.

## Características

- Procesa archivos Excel de diferentes bancos (BancoEstado, BancoChile, BancoSantander, BCI)
- Extrae saldos y movimientos específicos de cada formato
- Muestra un resumen formateado de los datos en la consola
- Actualiza automáticamente una hoja de Google Sheets con los datos procesados
- Sistema de logs detallado para depuración

## Requisitos

- Python 3.6 o superior
- Bibliotecas: pandas, openpyxl, gspread, oauth2client, prettytable

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/Contable.git
   cd Contable
   ```

2. Crear y activar un entorno virtual (recomendado):
   
   En Windows:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   
   En macOS/Linux:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
   
   Si tienes problemas con la instalación de pandas, puedes instalarlo directamente:
   ```
   pip install pandas
   ```

4. Verificar la instalación:
   ```
   python -c "import pandas; print(pandas.__version__)"
   ```

5. Configurar el acceso a Google Sheets:
   - Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
   - Habilitar la API de Google Sheets
   - Crear una cuenta de servicio y generar una clave en formato JSON
   - Guardar el archivo de credenciales en `config/credentials.json`
   - Compartir la hoja de cálculo con el email de la cuenta de servicio

6. Configurar el archivo `config/settings.json`:
   - Añadir el ID de la hoja de Google Sheets

## Resolución de problemas

### Error "Unable to import pandas"

Si encuentras este error en tu IDE o al ejecutar lint:

1. Asegúrate de que estás utilizando el intérprete de Python del entorno virtual donde instalaste pandas
2. Verifica la instalación con: `pip list | grep pandas`
3. Reinstala pandas si es necesario: `pip install --upgrade --force-reinstall pandas`
4. Si usas VS Code, selecciona el intérprete correcto con `Ctrl+Shift+P` → "Python: Select Interpreter"

### Problemas con Google Sheets

1. Verifica que el archivo `credentials.json` sea válido y esté en la ubicación correcta
2. Asegúrate de que la cuenta de servicio tenga permisos para acceder a la hoja de cálculo
3. Confirma que el ID de la hoja en `settings.json` sea correcto

## Uso

1. Colocar los archivos Excel de los bancos en el directorio `data/`

2. Ejecutar el script principal:
   ```
   python run.py
   ```

3. Para procesar un banco específico:
   ```
   python run.py --banco bancoestado
   ```

4. Para especificar un directorio diferente:
   ```
   python run.py --directorio mi_directorio
   ```

5. Para solo mostrar los datos sin actualizar Google Sheets:
   ```
   python run.py --solo-mostrar
   ```

6. Para ver logs detallados (modo depuración):
   ```
   python run.py --debug
   ```

## Bancos soportados

- **BancoEstado**: Extrae saldo contable y movimientos (fecha, N° operación, descripción, cargo)
- **BancoChile**: Extrae saldo disponible y movimientos (fecha, descripción, cargo)
- **BancoSantander**: Extrae saldo disponible y movimientos (fecha, detalle, cargo)
- **BCI**: Extrae movimientos (fecha transacción, descripción, cargo)
