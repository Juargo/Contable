# Contable

Sistema de procesamiento de extractos bancarios y actualización a Google Sheets.

## Características

- Procesa archivos Excel de diferentes bancos (BancoEstado, BancoChile, BancoSantander, BCI)
- Extrae saldos y movimientos específicos de cada formato
- Actualiza automáticamente una hoja de Google Sheets con los datos procesados

## Requisitos

- Python 3.6 o superior
- Bibliotecas: pandas, openpyxl, gspread, oauth2client

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/Contable.git
   cd Contable
   ```

2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Configurar el acceso a Google Sheets:
   - Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
   - Habilitar la API de Google Sheets
   - Crear una cuenta de servicio y generar una clave en formato JSON
   - Guardar el archivo de credenciales en `config/credentials.json`
   - Compartir la hoja de cálculo con el email de la cuenta de servicio

4. Configurar el archivo `config/settings.json`:
   - Añadir el ID de la hoja de Google Sheets

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

## Bancos soportados

- **BancoEstado**: Extrae saldo contable y movimientos (fecha, N° operación, descripción, cargo)
- **BancoChile**: Extrae saldo disponible y movimientos (fecha, descripción, cargo)
- **BancoSantander**: Extrae saldo disponible y movimientos (fecha, detalle, cargo)
- **BCI**: Extrae movimientos (fecha transacción, descripción, cargo)
