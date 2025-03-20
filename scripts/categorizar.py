"""Módulo para categorización y agrupación de movimientos bancarios."""

import os
import json
from datetime import datetime
import pandas as pd
from prettytable import PrettyTable
from scripts.utils.logger import get_logger

logger = get_logger()

def cargar_categorias():
    """Carga el diccionario de categorías desde el archivo de configuración."""
    try:
        ruta_categorias = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'config', 'categorias.json'
        )
        with open(ruta_categorias, 'r', encoding='utf-8') as f:
            categorias = json.load(f)
        logger.info("Diccionario de categorías cargado: %d categorías", len(categorias))
        return categorias
    except FileNotFoundError:
        logger.warning("Archivo de categorías no encontrado. Creando uno predeterminado.")
        crear_diccionario_predeterminado()
        return cargar_categorias()
    except json.JSONDecodeError:
        logger.error("Error al leer el archivo de categorías. Formato JSON inválido.")
        return {"Otros": {"palabras_clave": [], "subcategorias": {"General": {"palabras_clave": []}}}}

def crear_diccionario_predeterminado():
    """Crea un diccionario de categorías predeterminado si no existe."""
    categorias_predeterminadas = {
        "Transporte": {
            "subcategorias": {
                "Público": {
                    "palabras_clave": ["PAGO AUTOMATICO PASAJE QR", "PASAJE", "METRO", "BIP"]
                },
                "Taxi/Uber": {
                    "palabras_clave": ["UBER", "CABIFY", "DIDI", "TAXI"]
                },
                "Otros": {
                    "palabras_clave": []
                }
            }
        },
        "Alimentación": {
            "subcategorias": {
                "Supermercado": {
                    "palabras_clave": ["JUMBO", "LIDER", "SANTA ISABEL", "UNIMARC", "TOTTUS"]
                },
                "Restaurantes": {
                    "palabras_clave": ["RESTAURANT", "RESTAURANTE"]
                },
                "Otros": {
                    "palabras_clave": []
                }
            }
        },
        "Otros": {
            "subcategorias": {
                "General": {
                    "palabras_clave": []
                }
            }
        }
    }
    
    ruta_config = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    if not os.path.exists(ruta_config):
        os.makedirs(ruta_config)
        
    ruta_categorias = os.path.join(ruta_config, 'categorias.json')
    with open(ruta_categorias, 'w', encoding='utf-8') as f:
        json.dump(categorias_predeterminadas, f, indent=2, ensure_ascii=False)
    
    logger.info("Archivo de categorías predeterminado creado en %s", ruta_categorias)

def cargar_palabras_descartar():
    """Carga la lista de palabras clave para descartar movimientos."""
    try:
        ruta_descartar = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'config', 'descartar.json'
        )
        with open(ruta_descartar, 'r', encoding='utf-8') as f:
            config_descartar = json.load(f)
        
        palabras_descartar = config_descartar.get('palabras_clave', [])
        logger.info("Lista de palabras a descartar cargada: %d palabras", len(palabras_descartar))
        return palabras_descartar
    except FileNotFoundError:
        logger.warning("Archivo de palabras a descartar no encontrado. Creando uno predeterminado.")
        crear_archivo_descartar_predeterminado()
        return cargar_palabras_descartar()
    except json.JSONDecodeError:
        logger.error("Error al leer el archivo de palabras a descartar. Formato JSON inválido.")
        return []

def crear_archivo_descartar_predeterminado():
    """Crea un archivo predeterminado con palabras clave a descartar."""
    config_predeterminado = {
        "palabras_clave": [
            "TRANSFERENCIA ENVIADA A JORGE RETAMA"
        ],
        "comentarios": {
            "TRANSFERENCIA ENVIADA A JORGE RETAMA": "Transferencia entre cuentas propias"
        }
    }
    
    ruta_config = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    if not os.path.exists(ruta_config):
        os.makedirs(ruta_config)
        
    ruta_descartar = os.path.join(ruta_config, 'descartar.json')
    with open(ruta_descartar, 'w', encoding='utf-8') as f:
        json.dump(config_predeterminado, f, indent=2, ensure_ascii=False)
    
    logger.info("Archivo de palabras a descartar predeterminado creado en %s", ruta_descartar)

def debe_descartarse(descripcion, palabras_descartar=None):
    """
    Determina si un movimiento debe descartarse según su descripción.
    
    Args:
        descripcion (str): Descripción del movimiento
        palabras_descartar (list, optional): Lista de palabras clave para descartar
        
    Returns:
        bool: True si el movimiento debe descartarse, False en caso contrario
    """
    if not descripcion or not isinstance(descripcion, str):
        return False
    
    if palabras_descartar is None:
        palabras_descartar = cargar_palabras_descartar()
    
    descripcion = descripcion.upper()
    
    # Verificar si alguna palabra clave está en la descripción
    for palabra in palabras_descartar:
        if palabra.upper() in descripcion:
            logger.debug("Movimiento '%s' descartado por palabra clave '%s'", 
                        descripcion, palabra)
            return True
    
    return False

def categorizar_movimiento(descripcion, categorias):
    """
    Asigna una categoría y subcategoría a un movimiento basado en su descripción.
    Ahora solo busca coincidencias en subcategorías, ya que las categorías principales
    no tienen palabras clave propias.
    
    Args:
        descripcion (str): Descripción del movimiento
        categorias (dict): Diccionario de categorías
        
    Returns:
        tuple: (str: Nombre de la categoría asignada, str: Nombre de la subcategoría asignada)
    """
    if not descripcion or not isinstance(descripcion, str):
        return "Otros", "General"
    
    descripcion = descripcion.upper()
    
    # Buscar coincidencias solamente en las subcategorías
    for categoria, datos_categoria in categorias.items():
        subcategorias = datos_categoria.get("subcategorias", {})
        for subcategoria, datos_subcategoria in subcategorias.items():
            palabras_subcategoria = datos_subcategoria.get("palabras_clave", [])
            for palabra in palabras_subcategoria:
                if not palabra:  # Ignorar palabras vacías
                    continue
                if palabra.upper() in descripcion:
                    logger.debug("Movimiento '%s' categorizado como '%s - %s' por palabra clave '%s'", 
                                descripcion, categoria, subcategoria, palabra)
                    return categoria, subcategoria
    
    # Si no hay coincidencias, asignar "Otros - General"
    logger.debug("Movimiento '%s' categorizado como 'Otros - General' (sin coincidencias)", descripcion)
    return "Otros", "General"

def obtener_mes_anio(fecha):
    """
    Obtiene el mes y año a partir de una fecha.
    
    Args:
        fecha: Fecha en formato string, datetime o similar
        
    Returns:
        tuple: (str: Mes y año en formato "MesAAAA", datetime: fecha convertida o None)
    """
    try:
        # Intentar convertir a datetime si es string
        if isinstance(fecha, str):
            # Probar diferentes formatos de fecha
            formatos = [
                "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
                "%d-%m-%y", "%d/%m/%y", "%y/%m/%d", "%y-%m-%d"
            ]
            
            for formato in formatos:
                try:
                    fecha_dt = datetime.strptime(fecha, formato)
                    break
                except ValueError:
                    continue
            else:
                logger.warning("No se pudo convertir la fecha '%s' a datetime", fecha)
                return "Desconocido", None
        elif isinstance(fecha, datetime):
            fecha_dt = fecha
        else:
            # Intentar convertir desde un tipo pandas (Timestamp)
            fecha_dt = pd.to_datetime(fecha)
        
        # Obtener nombre del mes en español
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        mes_nombre = meses[fecha_dt.month]
        return f"{mes_nombre}{fecha_dt.year}", fecha_dt
    except Exception as e:
        logger.error("Error al procesar fecha '%s': %s", fecha, e)
        return "Desconocido", None

def es_cargo(monto, banco=None):
    """
    Determina si un monto representa un cargo/costo basado en su valor y posiblemente el banco.
    
    Args:
        monto: El monto a evaluar
        banco (str, optional): El nombre del banco si está disponible
        
    Returns:
        bool: True si es un cargo, False en caso contrario
    """
    try:
        # Convertir a número si es string
        if isinstance(monto, str):
            # Eliminar símbolos y formateo
            monto_limpio = monto.replace("$", "").replace(".", "").replace(",", ".")
            monto = float(monto_limpio)
        else:
            monto = float(monto)
        
        # Diferentes bancos pueden usar diferentes formatos para los cargos
        if banco:
            banco = banco.lower()
            # En BCI, los cargos podrían ser positivos
            if banco == "bci":
                return monto != 0  # Consideramos cualquier valor diferente de cero como cargo
            # Para otros bancos, los cargos generalmente son negativos
            else:
                return monto < 0
        else:
            # Por defecto, asumimos que los cargos son negativos
            return monto < 0
    except (ValueError, TypeError):
        # Si no podemos convertir a número, no podemos determinar si es cargo
        logger.warning("No se pudo determinar si '%s' es un cargo", monto)
        return False

def es_cargo_valido(monto, banco=None):
    """
    Determina si un monto representa un cargo/costo válido (no nulo, no cero).
    
    Args:
        monto: El monto a evaluar
        banco (str, optional): El nombre del banco si está disponible
        
    Returns:
        bool: True si es un cargo válido, False en caso contrario
    """
    try:
        # Convertir a número si es string
        if isinstance(monto, str):
            # Eliminar símbolos y formateo
            monto_limpio = monto.replace("$", "").replace(".", "").replace(",", ".")
            monto = float(monto_limpio)
        else:
            monto = float(monto)
        
        # Verificar que no sea cero ni None
        return monto != 0 and monto is not None
    except (ValueError, TypeError):
        # Si no podemos convertir a número, no es un cargo válido
        return False

def es_mes_en_curso(fecha):
    """
    Verifica si una fecha está en el mes en curso.
    
    Args:
        fecha (datetime): Fecha a verificar
        
    Returns:
        bool: True si la fecha está en el mes en curso, False en caso contrario
    """
    hoy = datetime.today()
    return fecha is not None and fecha.year == hoy.year and fecha.month == hoy.month

def agrupar_por_mes_categoria(movimientos, categorias=None, solo_cargos=True, mes_en_curso=False):
    """
    Agrupa los movimientos por mes, categoría y subcategoría.
    
    Args:
        movimientos (list): Lista de movimientos
        categorias (dict, optional): Diccionario de categorías. Si es None, se carga del archivo.
        solo_cargos (bool): Si solo se deben considerar los movimientos de cargo/costo
        mes_en_curso (bool): Si solo se deben considerar los movimientos del mes en curso
        
    Returns:
        dict: Diccionario con estructura {mes: {categoria: {subcategoria: {...}}}}
    """
    if categorias is None:
        categorias = cargar_categorias()
    
    # Cargar palabras a descartar
    palabras_descartar = cargar_palabras_descartar()
    
    # Inicializar diccionario para agrupar resultados
    agrupado = {}
    
    # Procesar cada movimiento
    for mov in movimientos:
        # Obtener descripción y monto
        descripcion = mov.get("Descripción", mov.get("Detalle", ""))
        
        # Verificar si se debe descartar este movimiento
        if debe_descartarse(descripcion, palabras_descartar):
            continue
            
        monto = mov.get("Cargo", 0)
        banco = mov.get("Banco")  # Algunos movimientos podrían tener el banco identificado
        
        # Verificar si el cargo es válido (no nulo, no cero)
        if not es_cargo_valido(monto, banco):
            continue
            
        # Si solo queremos considerar cargos, verificar si este movimiento es un cargo
        if solo_cargos and not es_cargo(monto, banco):
            continue
        
        # Convertir monto a número si es string
        if isinstance(monto, str):
            try:
                # Eliminar símbolos de moneda y separadores de miles
                monto = monto.replace("$", "").replace(".", "").replace(",", ".")
                monto = float(monto)
            except ValueError:
                logger.warning("No se pudo convertir el monto '%s' a número", monto)
                continue  # Saltamos este movimiento ya que no podemos procesar el monto
        
        # Verificar nuevamente que el monto no sea cero después de la conversión
        if monto == 0:
            continue
        
        # Tomar valor absoluto del monto para calcular totales
        # (los cargos suelen ser negativos pero queremos mostrar totales positivos)
        monto = abs(float(monto))
        
        # Obtener mes y año
        fecha = mov.get("Fecha")
        if not fecha:
            mes_anio, fecha_dt = "Desconocido", None
        else:
            mes_anio, fecha_dt = obtener_mes_anio(fecha)
        
        # Si solo queremos considerar movimientos del mes en curso, verificar la fecha
        if mes_en_curso and (fecha_dt is None or not es_mes_en_curso(fecha_dt)):
            continue
        
        # Categorizar el movimiento
        categoria, subcategoria = categorizar_movimiento(descripcion, categorias)
        
        # Agregar al diccionario agrupado
        if mes_anio not in agrupado:
            agrupado[mes_anio] = {
                "fecha_dt": fecha_dt,
                "categorias": {}
            }
        
        if categoria not in agrupado[mes_anio]["categorias"]:
            agrupado[mes_anio]["categorias"][categoria] = {
                "total": 0,
                "subcategorias": {}
            }
        
        if subcategoria not in agrupado[mes_anio]["categorias"][categoria]["subcategorias"]:
            agrupado[mes_anio]["categorias"][categoria]["subcategorias"][subcategoria] = {
                "total": 0,
                "movimientos": []
            }
        
        # Actualizar totales
        agrupado[mes_anio]["categorias"][categoria]["total"] += monto
        agrupado[mes_anio]["categorias"][categoria]["subcategorias"][subcategoria]["total"] += monto
        agrupado[mes_anio]["categorias"][categoria]["subcategorias"][subcategoria]["movimientos"].append(mov)
    
    logger.info("Movimientos agrupados por mes y categoría: %d meses", len(agrupado))
    return agrupado

def mostrar_resumen_categorizado(movimientos, mostrar_detalle=False, solo_cargos=True, mes_en_curso=False):
    """
    Muestra un resumen de gastos categorizados y agrupados por mes.
    
    Args:
        movimientos (list): Lista de movimientos
        mostrar_detalle (bool): Si se debe mostrar el detalle de movimientos por categoría
        solo_cargos (bool): Si solo se deben considerar los movimientos de cargo/costo
        mes_en_curso (bool): Si solo se deben considerar los movimientos del mes en curso
    """
    categorias = cargar_categorias()
    agrupado = agrupar_por_mes_categoria(movimientos, categorias, solo_cargos, mes_en_curso)
    
    # Ordenar meses cronológicamente
    # Usamos una clave personalizada: primero por fecha si está disponible, luego alfabéticamente
    def clave_ordenamiento(mes):
        if mes == "Desconocido":
            return (datetime(9999, 12, 31), mes)  # Poner "Desconocido" al final
        fecha_dt = agrupado[mes]["fecha_dt"]
        if fecha_dt:
            return (fecha_dt, mes)
        return (datetime(9998, 12, 31), mes)  # Si no hay fecha, poner después de las fechas conocidas
    
    meses_ordenados = sorted(agrupado.keys(), key=clave_ordenamiento)
    
    print("\n" + "="*70)
    print("RESUMEN DE GASTOS POR MES, CATEGORÍA Y SUBCATEGORÍA")
    print("="*70)
    
    for mes in meses_ordenados:
        print(f"\n{mes}")
        print("-"*70)
        
        tabla = PrettyTable()
        tabla.field_names = ["Categoría", "Subcategoría", "Total", "# Movimientos"]
        tabla.align["Categoría"] = "l"
        tabla.align["Subcategoría"] = "l"
        tabla.align["Total"] = "r"
        tabla.align["# Movimientos"] = "r"
        
        categorias_mes = agrupado[mes]["categorias"]
        categorias_ordenadas = sorted(
            categorias_mes.keys(),
            key=lambda c: categorias_mes[c]["total"],
            reverse=True
        )
        
        total_mes = 0
        total_movimientos_mes = 0
        
        for categoria in categorias_ordenadas:
            datos_categoria = categorias_mes[categoria]
            total_categoria = datos_categoria["total"]
            
            # Obtener subcategorías ordenadas por monto
            subcategorias = datos_categoria["subcategorias"]
            subcategorias_ordenadas = sorted(
                subcategorias.keys(),
                key=lambda sc: subcategorias[sc]["total"],
                reverse=True
            )
            
            # Calcular totales para esta categoría
            total_movimientos_categoria = sum(
                len(subcategorias[sc]["movimientos"])
                for sc in subcategorias
            )
            
            # Añadir fila de la categoría principal
            tabla.add_row([
                f"{categoria.upper()}",
                "",
                f"${total_categoria:,.0f}**",
                f"{total_movimientos_categoria}"
            ])
            
            # Añadir subcategorías
            for subcategoria in subcategorias_ordenadas:
                datos_subcategoria = subcategorias[subcategoria]
                total_subcategoria = datos_subcategoria["total"]
                num_movimientos = len(datos_subcategoria["movimientos"])
                
                if total_subcategoria > 0:
                    tabla.add_row([
                        "",
                        subcategoria,
                        f"${total_subcategoria:,.0f}",
                        num_movimientos
                    ])
                    
                    # Mostrar detalle de movimientos si se solicita
                    if mostrar_detalle and num_movimientos > 0:
                        print(f"\nDetalle de {categoria} - {subcategoria}:")
                        tabla_detalle = PrettyTable()
                        tabla_detalle.field_names = ["Fecha", "Descripción", "Monto"]
                        tabla_detalle.align["Descripción"] = "l"
                        tabla_detalle.align["Monto"] = "r"
                        tabla_detalle.max_width["Descripción"] = 50
                        
                        for mov in datos_subcategoria["movimientos"]:
                            fecha = mov.get("Fecha", "")
                            desc = mov.get("Descripción", mov.get("Detalle", ""))
                            monto = abs(float(mov.get("Cargo", 0)))
                            
                            tabla_detalle.add_row([
                                fecha,
                                desc[:50],
                                f"${monto:,.f}"
                            ])
                        
                        print(tabla_detalle)
            
            total_mes += total_categoria
            total_movimientos_mes += total_movimientos_categoria
        
        # Agregar fila de totales
        tabla.add_row([
            "TOTAL",
            "",
            f"${total_mes:,.0f}",
            total_movimientos_mes
        ])
        
        print(tabla)
    
    print("\n" + "="*70)

def exportar_resumen_a_gsheet(movimientos, gsheet_id=None, nombre_hoja="Resumen", solo_cargos=True, mes_en_curso=False):
    """
    Exporta el resumen categorizado a Google Sheets.
    
    Args:
        movimientos (list): Lista de movimientos
        gsheet_id (str, optional): ID de la hoja de Google Sheets
        nombre_hoja (str): Nombre de la hoja donde se exportará el resumen
        solo_cargos (bool): Si solo se deben considerar los movimientos de cargo/costo
        mes_en_curso (bool): Si solo se deben considerar los movimientos del mes en curso
        
    Returns:
        bool: True si la exportación fue exitosa, False en caso contrario
    """
    try:
        from scripts.actualizar_gsheet import conectar_gsheet
        
        categorias = cargar_categorias()
        agrupado = agrupar_por_mes_categoria(movimientos, categorias, solo_cargos, mes_en_curso)
        
        # Ordenar meses cronológicamente (misma función que en mostrar_resumen_categorizado)
        def clave_ordenamiento(mes):
            if mes == "Desconocido":
                return (datetime(9999, 12, 31), mes)  # Poner "Desconocido" al final
            fecha_dt = agrupado[mes]["fecha_dt"]
            if fecha_dt:
                return (fecha_dt, mes)
            return (datetime(9998, 12, 31), mes)  # Si no hay fecha, poner después de las fechas conocidas
        
        meses_ordenados = sorted(agrupado.keys(), key=clave_ordenamiento)
        
        # Conectar a Google Sheets
        spreadsheet = conectar_gsheet()
        
        # Obtener o crear la hoja de resumen
        try:
            worksheet = spreadsheet.worksheet(nombre_hoja)
        except:
            worksheet = spreadsheet.add_worksheet(title=nombre_hoja, rows="1000", cols="20")
        
        # Preparar datos para exportar
        datos = []
        datos.append(["RESUMEN DE GASTOS POR MES, CATEGORÍA Y SUBCATEGORÍA", "", "", ""])
        datos.append(["", "", "", ""])
        
        for mes in meses_ordenados:
            datos.append([mes, "", "", ""])
            datos.append(["Categoría", "Subcategoría", "Total", "# Movimientos"])
            
            categorias_mes = agrupado[mes]["categorias"]
            categorias_ordenadas = sorted(
                categorias_mes.keys(),
                key=lambda c: categorias_mes[c]["total"],
                reverse=True
            )
            
            total_mes = 0
            total_movimientos_mes = 0
            
            for categoria in categorias_ordenadas:
                datos_categoria = categorias_mes[categoria]
                total_categoria = datos_categoria["total"]
                
                # Obtener subcategorías ordenadas por monto
                subcategorias = datos_categoria["subcategorias"]
                subcategorias_ordenadas = sorted(
                    subcategorias.keys(),
                    key=lambda sc: subcategorias[sc]["total"],
                    reverse=True
                )
                
                # Calcular totales para esta categoría
                total_movimientos_categoria = sum(
                    len(subcategorias[sc]["movimientos"])
                    for sc in subcategorias
                )
                
                # Añadir fila de la categoría principal
                datos.append([
                    categoria,
                    "",
                    total_categoria,
                    total_movimientos_categoria
                ])
                
                # Añadir subcategorías
                for subcategoria in subcategorias_ordenadas:
                    datos_subcategoria = subcategorias[subcategoria]
                    total_subcategoria = datos_subcategoria["total"]
                    num_movimientos = len(datos_subcategoria["movimientos"])
                    
                    if total_subcategoria > 0:
                        datos.append([
                            "",
                            subcategoria,
                            total_subcategoria,
                            num_movimientos
                        ])
                
                total_mes += total_categoria
                total_movimientos_mes += total_movimientos_categoria
            
            # Agregar fila de totales
            datos.append([
                "TOTAL",
                "",
                total_mes,
                total_movimientos_mes
            ])
            datos.append(["", "", "", ""])
        
        # Actualizar hoja de cálculo
        worksheet.clear()
        worksheet.update('A1', datos)
        
        # Aplicar formato
        worksheet.format('A1', {
            "textFormat": {"bold": True, "fontSize": 14}
        })
        
        # Aplicar formato a categorías principales y totales (en negrita)
        for i, fila in enumerate(datos):
            if fila[0] and not fila[1] and fila[0] != "Categoría":  # Es categoría principal o total
                worksheet.format(f'A{i+1}:D{i+1}', {"textFormat": {"bold": True}})
        
        logger.info("Resumen categorizado exportado a Google Sheets")
        return True
    except Exception as e:
        logger.error("Error al exportar resumen a Google Sheets: %s", e)
        return False

if __name__ == "__main__":
    # Ejemplo de uso del módulo
    ejemplo_movimientos = [
        {"Fecha": "2023-03-15", "Descripción": "PAGO AUTOMATICO PASAJE QR", "Cargo": -1500},
        {"Fecha": "2023-03-25", "Descripción": "PAGO AUTOMATICO PASAJE QR", "Cargo": -1500},
        {"Fecha": "2023-03-10", "Descripción": "JUMBO SUCURSAL CENTRO", "Cargo": -45000},
        {"Fecha": "2023-04-05", "Descripción": "NETFLIX", "Cargo": -12900},
        {"Fecha": "2023-04-15", "Descripción": "PAGO AUTOMATICO PASAJE QR", "Cargo": -1500},
    ]
    
    mostrar_resumen_categorizado(ejemplo_movimientos, mostrar_detalle=True)
