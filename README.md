# Aplicación Contable

Esta aplicación utiliza Astro con React para el frontend y FastAPI para el backend, permitiendo procesar reportes bancarios y visualizar transacciones.

## Requisitos previos

### Para el frontend:
- Node.js 14.x o superior
- pnpm 7.x o superior (recomendado sobre npm)

### Para el backend:
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Contable
```

### 2. Configurar el entorno del frontend

```bash
# Instalar pnpm globalmente si no lo tienes
npm install -g pnpm

# Instalar dependencias del proyecto principal
pnpm install

# Navegar a la carpeta del frontend
cd frontend

# Instalar dependencias de Astro y React
pnpm install
```

### 3. Configurar el entorno del backend

```bash
# Navegar a la carpeta del backend
cd backend

# Se recomienda crear un entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

Si no existe el archivo requirements.txt, puedes crearlo con:

```bash
pip install fastapi uvicorn pandas numpy
pip freeze > requirements.txt
```

## Ejecución del proyecto

### Opción 1: Ejecutar frontend y backend por separado

#### Para el frontend:
```bash
# Desde la carpeta raíz del proyecto
cd frontend
pnpm run dev
```
El frontend estará disponible en: http://localhost:4321

#### Para el backend:
```bash
# Desde la carpeta raíz del proyecto
cd backend
python main.py
```
El backend estará disponible en: http://localhost:8000

### Opción 2: Ejecutar todo en un solo comando

Desde la carpeta raíz del proyecto:

```bash
pnpm run dev
```

Este comando usa concurrently para iniciar tanto el frontend como el backend en un solo terminal.

## Ejecución con Docker

El proyecto incluye configuración Docker para facilitar su despliegue y desarrollo.

### Requisitos

- Docker
- Docker Compose

### Configuración

1. Los archivos Docker se encuentran en el directorio `docker/`
2. El archivo principal de configuración es `docker/docker-compose.yml`
3. Las variables de entorno están definidas en el archivo `.env` en la raíz

### Comandos principales

Puedes usar el Makefile incluido para operaciones comunes:

```bash
# Iniciar todos los servicios en segundo plano
make up

# Detener todos los servicios
make down

# Ver logs de todos los servicios
make logs

# Acceder a la shell del backend
make shell-backend

# Acceder al cliente MySQL
make mysql-cli

# Ver todos los comandos disponibles
make help
```

O usar Docker Compose directamente:

```bash
# Iniciar los contenedores
docker-compose -f docker/docker-compose.yml up -d

# Detener los contenedores
docker-compose -f docker/docker-compose.yml down
```

### Servicios incluidos

- **MySQL**: Base de datos para almacenar transacciones
- **Backend**: API de FastAPI
- **Frontend**: Aplicación Astro con React

### Estructura de la base de datos

La base de datos incluye tablas para:
- Bancos
- Transacciones
- Categorías y subcategorías
- Palabras clave para categorización automática

Al iniciar el contenedor por primera vez, se ejecutan los scripts de inicialización en `docker/mysql/init/`.

## Uso de la API

### Endpoints disponibles:

- `GET /api/transactions`: Obtiene todas las transacciones
- `POST /api/upload-bank-report`: Sube y procesa un reporte bancario

### Ejemplo de uso con curl:

```bash
# Obtener transacciones
curl http://localhost:8000/api/transactions

# Subir un reporte bancario
curl -X POST http://localhost:8000/api/upload-bank-report \
  -F "file=@ruta/al/archivo.csv" \
  -F "bank_name=santander"
```

## Estructura del proyecto

```
/Contable/
├── frontend/             # Frontend con Astro y React
│   ├── public/           # Archivos estáticos
│   ├── src/              # Código fuente
│   │   ├── components/   # Componentes React
│   │   ├── layouts/      # Layouts Astro
│   │   └── pages/        # Páginas Astro
├── backend/              # API de Python
│   ├── api/              # Endpoints de la API
│   ├── models/           # Modelos de datos
│   ├── services/         # Servicios (incluye procesamiento de datos)
│   └── utils/            # Utilidades
├── scripts/              # Scripts para procesar datos
└── data/                 # Datos de la aplicación
```

## Desarrollo

### Añadir nuevos bancos

Para añadir soporte para un nuevo banco, sigue estos pasos:

1. Crea una nueva función en `backend/services/bank_report_service.py` siguiendo el patrón de las existentes
2. Añade el nombre del banco en el diccionario `processors` en la función `process_bank_report`
3. Añade el nombre del banco a la lista `valid_banks` en `backend/api/transactions.py`
4. Añade una nueva opción en el selector de bancos del frontend (`frontend/src/components/ContableApp.jsx`)

## Solución de problemas

### CORS (Cross-Origin Resource Sharing)

Si encuentras problemas de CORS, verifica que los orígenes permitidos en `backend/main.py` incluyan la URL de tu frontend.

### Errores de dependencias

Si encuentras errores relacionados con dependencias Python, asegúrate de estar usando el entorno virtual y que todos los paquetes estén instalados:

```bash
pip install -r requirements.txt
```

### Problemas con la carga de archivos

- Asegúrate de que el formato del archivo coincida con el esperado por el procesador del banco específico
- Verifica los logs del servidor para obtener información detallada sobre errores

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

9. Para mostrar solo los movimientos del mes en curso:
   ```
   python run.py --categorizar --mes-en-curso
   ```

10. Para combinar opciones:
   ```
   python run.py --banco bancoestado --solo-mostrar --categorizar --mes-en-curso
   ```

## Categorización de gastos

El sistema incluye un diccionario de categorías en `config/categorias.json` que permite clasificar automáticamente los gastos según palabras clave en la descripción de los movimientos.

Por defecto, la categorización solo considera los movimientos que representan cargos o costos (valores negativos), ignorando abonos y transferencias recibidas. Esto se puede modificar con la opción `--todos-movimientos`.

### Personalizar categorías

El sistema utiliza un esquema jerárquico con categorías y subcategorías. Puedes editar el archivo `config/categorias.json` para ajustar las categorías, subcategorías y palabras clave según tus necesidades. El formato es:

```json
{
  "Nombre de categoría": {
    "subcategorias": {
      "Nombre subcategoría 1": {
        "palabras_clave": ["PALABRA1", "PALABRA2"]
      },
      "Nombre subcategoría 2": {
        "palabras_clave": ["PALABRA3", "PALABRA4"]
      }
    }
  }
}
```

#### Funcionamiento del sistema de categorización:

1. El sistema busca coincidencias en las palabras clave de las subcategorías
2. Si encuentra una coincidencia, asigna esa subcategoría y su categoría principal al movimiento
3. Si no encuentra ninguna coincidencia, asigna "Otros - General"
4. El valor de cada categoría principal es la suma de todas sus subcategorías

### Descartar movimientos específicos

El sistema permite descartar movimientos específicos basados en palabras clave, como transferencias entre cuentas propias u otros movimientos que no quieras considerar en tu análisis. Para esto:

1. Edita el archivo `config/descartar.json`
2. Agrega las palabras clave en el arreglo `palabras_clave`
3. Opcionalmente añade comentarios para cada palabra clave en la sección `comentarios`

Ejemplo:
```json
{
  "palabras_clave": [
    "TRANSFERENCIA ENVIADA A JORGE RETAMA",
    "TRANSFERENCIA RECIBIDA DE JORGE RETAMA"
  ],
  "comentarios": {
    "TRANSFERENCIA ENVIADA A JORGE RETAMA": "Transferencia entre cuentas propias",
    "TRANSFERENCIA RECIBIDA DE JORGE RETAMA": "Transferencia entre cuentas propias"
  }
}
```

Cualquier movimiento que contenga alguna de estas palabras clave será excluido automáticamente de los análisis y resúmenes.

### Migración desde versión anterior

Si vienes de una versión anterior del sistema sin subcategorías, puedes migrar tu archivo de categorías ejecutando:

```
python -m scripts.utils.migracion_categorias
```

Esto convertirá tu archivo manteniendo todas las palabras clave existentes y creando la estructura necesaria para subcategorías.

### Resumen categorizado

Al usar la opción `--categorizar`, el sistema:

1. Procesa todos los archivos Excel encontrados
2. Filtra los movimientos para considerar solo los cargos (a menos que se use `--todos-movimientos`)
3. Clasifica cada movimiento en una categoría y subcategoría según las palabras clave
4. Agrupa los movimientos por mes, categoría y subcategoría
5. Muestra un resumen en la consola con los totales por categoría y subcategoría en cada mes
6. Opcionalmente exporta el resumen a una hoja en Google Sheets

## Bancos soportados

- **BancoEstado**: Extrae saldo contable y movimientos (fecha, N° operación, descripción, cargo)
- **BancoChile**: Extrae saldo disponible y movimientos (fecha, descripción, cargo)
- **BancoSantander**: Extrae saldo disponible y movimientos (fecha, detalle, cargo)
- **BCI**: Extrae movimientos (fecha transacción, descripción, cargo)
