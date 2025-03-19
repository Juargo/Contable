# Contable

Sistema de procesamiento de extractos bancarios y actualización a Google Sheets.

## Características

- Procesa archivos Excel de diferentes bancos (BancoEstado, BancoChile, BancoSantander, BCI)
- Extrae saldos y movimientos específicos de cada formato
- Muestra un resumen formateado de los datos en la consola
- Actualiza automáticamente una hoja de Google Sheets con los datos procesados
- Sistema de logs detallado para depuración
- Categorización automática de gastos por mes y tipo de gasto

## Requisitos

- Python 3.6 o superior
- Bibliotecas: pandas, openpyxl, gspread, oauth2client, prettytable

## Instalación

### Opción 1: Usando scripts de instalación

#### En Windows:
```
install.bat
```

#### En macOS/Linux:
```
chmod +x install.sh
./install.sh
```

### Opción 2: Instalación manual con entorno virtual

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/Contable.git
   cd Contable
   ```

2. Crear y activar un entorno virtual:
   
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

3. Instalar setuptools primero:
   ```
   pip install setuptools
   ```

4. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

### Opción 3: Instalación directa sin setuptools

Si tienes problemas con setuptools, puedes usar la instalación directa:

```
python install_direct.py
```

## Verificación de la instalación

Verifica que pandas esté correctamente instalado:

```
python -c "import pandas; print(pandas.__version__)"
```

## Configuración

1. Configurar el acceso a Google Sheets:
   - Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
   - Habilitar la API de Google Sheets
   - Crear una cuenta de servicio y generar una clave en formato JSON
   - Guardar el archivo de credenciales en `config/credentials.json`
   - Compartir la hoja de cálculo con el email de la cuenta de servicio

2. Configurar el archivo `config/settings.json`:
   - Añadir el ID de la hoja de Google Sheets

## Resolución de problemas

### Error "Unable to import 'setuptools'" o "Unable to import 'pandas'"

Estos errores indican que algunos módulos no están instalados correctamente:

1. Instala directamente estos paquetes:
   ```
   pip install setuptools pandas
   ```

2. Si usas un IDE como VS Code o PyCharm, configura el intérprete:
   - VS Code: `Ctrl+Shift+P` → "Python: Select Interpreter" → selecciona el entorno virtual
   - PyCharm: File → Settings → Project → Python Interpreter → selecciona o añade el intérprete

3. Usa la instalación directa:
   ```
   python install_direct.py
   ```

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

7. Para categorizar gastos y ver un resumen por mes y categoría:
   ```
   python run.py --categorizar
   ```

8. Para incluir todos los movimientos, no solo los cargos:
   ```
   python run.py --categorizar --todos-movimientos
   ```

9. Para combinar opciones:
   ```
   python run.py --banco bancoestado --solo-mostrar --categorizar
   ```

## Categorización de gastos

El sistema incluye un diccionario de categorías en `config/categorias.json` que permite clasificar automáticamente los gastos según palabras clave en la descripción de los movimientos.

Por defecto, la categorización solo considera los movimientos que representan cargos o costos (valores negativos), ignorando abonos y transferencias recibidas. Esto se puede modificar con la opción `--todos-movimientos`.

### Personalizar categorías

Puedes editar el archivo `config/categorias.json` para ajustar las categorías y palabras clave según tus necesidades. El formato es:

```json
{
  "Nombre de categoría": [
    "PALABRA_CLAVE1",
    "PALABRA_CLAVE2",
    ...
  ],
  ...
}
```

### Resumen categorizado

Al usar la opción `--categorizar`, el sistema:

1. Procesa todos los archivos Excel encontrados
2. Filtra los movimientos para considerar solo los cargos (a menos que se use `--todos-movimientos`)
3. Clasifica cada movimiento en una categoría según las palabras clave
4. Agrupa los movimientos por mes y categoría
5. Muestra un resumen en la consola con los totales por categoría en cada mes
6. Opcionalmente exporta el resumen a una hoja en Google Sheets

## Bancos soportados

- **BancoEstado**: Extrae saldo contable y movimientos (fecha, N° operación, descripción, cargo)
- **BancoChile**: Extrae saldo disponible y movimientos (fecha, descripción, cargo)
- **BancoSantander**: Extrae saldo disponible y movimientos (fecha, detalle, cargo)
- **BCI**: Extrae movimientos (fecha transacción, descripción, cargo)
