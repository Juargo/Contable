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
        return {"Otros": []}

def crear_diccionario_predeterminado():
    """Crea un diccionario de categorías predeterminado si no existe."""
    categorias_predeterminadas = {
        "Transporte público": ["PAGO AUTOMATICO PASAJE QR", "PASAJE", "METRO", "BIP"],
        "Supermercado": ["JUMBO", "LIDER", "SANTA ISABEL", "UNIMARC", "TOTTUS"],
        "Servicios básicos": ["ENEL", "AGUAS", "LUZ", "AGUA", "GAS", "INTERNET"],
        "Otros": []
    }
    
    ruta_config = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    if not os.path.exists(ruta_config):
        os.makedirs(ruta_config)
        
    ruta_categorias = os.path.join(ruta_config, 'categorias.json')
    with open(ruta_categorias, 'w', encoding='utf-8') as f:
        json.dump(categorias_predeterminadas, f, indent=2, ensure_ascii=False)
    
    logger.info("Archivo de categorías predeterminado creado en %s", ruta_categorias)

def categorizar_movimiento(descripcion, categorias):
    """
    Asigna una categoría a un movimiento basado en su descripción.
    
    Args:
        descripcion (str): Descripción del movimiento
        categorias (dict): Diccionario de categorías
        
    Returns:
        str: Nombre de la categoría asignada
    """
    if not descripcion or not isinstance(descripcion, str):
        return "Otros"
    
    descripcion = descripcion.upper()
    
    # Buscar coincidencias en cada categoría
    for categoria, palabras_clave in categorias.items():
        for palabra in palabras_clave:
            if palabra.upper() in descripcion:
                logger.debug("Movimiento '%s' categorizado como '%s' por palabra clave '%s'", 
                            descripcion, categoria, palabra)
                return categoria
    
    # Si no hay coincidencias, asignar "Otros"
    logger.debug("Movimiento '%s' categorizado como 'Otros' (sin coincidencias)", descripcion)
    return "Otros"

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

def agrupar_por_mes_categoria(movimientos, categorias=None):
    """
    Agrupa los movimientos por mes y categoría.
    
    Args:
        movimientos (list): Lista de movimientos
        categorias (dict, optional): Diccionario de categorías. Si es None, se carga del archivo.
        
    Returns:
        dict: Diccionario con estructura {mes: {categoria: total}}
    """
    if categorias is None:
        categorias = cargar_categorias()
    
    # Inicializar diccionario para agrupar resultados
    agrupado = {}
    
    # Procesar cada movimiento
    for mov in movimientos:
        # Obtener mes y año
        fecha = mov.get("Fecha")
        if not fecha:
            mes_anio, fecha_dt = "Desconocido", None
        else:
            mes_anio, fecha_dt = obtener_mes_anio(fecha)
        
        # Obtener descripción y monto
        descripcion = mov.get("Descripción", mov.get("Detalle", ""))
        monto = mov.get("Cargo", 0)
        
        # Convertir monto a número si es string
        if isinstance(monto, str):
            try:
                # Eliminar símbolos de moneda y separadores de miles
                monto = monto.replace("$", "").replace(".", "").replace(",", ".")
                monto = float(monto)
            except ValueError:
                logger.warning("No se pudo convertir el monto '%s' a número", monto)
                monto = 0
        
        # Tomar valor absoluto del monto (los cargos suelen ser negativos)
        monto = abs(float(monto))
        
        # Categorizar el movimiento
        categoria = categorizar_movimiento(descripcion, categorias)
        
        # Agregar al diccionario agrupado
        if mes_anio not in agrupado:
            agrupado[mes_anio] = {
                "fecha_dt": fecha_dt,
                "categorias": {}
            }
        
        if categoria not in agrupado[mes_anio]["categorias"]:
            agrupado[mes_anio]["categorias"][categoria] = {
                "total": 0,
                "movimientos": []
            }
        
        agrupado[mes_anio]["categorias"][categoria]["total"] += monto
        agrupado[mes_anio]["categorias"][categoria]["movimientos"].append(mov)
    
    logger.info("Movimientos agrupados por mes y categoría: %d meses", len(agrupado))
    return agrupado

def mostrar_resumen_categorizado(movimientos, mostrar_detalle=False):
    """
    Muestra un resumen de gastos categorizados y agrupados por mes.
    
    Args:
        movimientos (list): Lista de movimientos
        mostrar_detalle (bool): Si se debe mostrar el detalle de movimientos por categoría
    """
    categorias = cargar_categorias()
    agrupado = agrupar_por_mes_categoria(movimientos, categorias)
    
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
    
    print("\n" + "="*60)
    print("RESUMEN DE GASTOS POR MES Y CATEGORÍA")
    print("="*60)
    
    for mes in meses_ordenados:
        print(f"\n{mes}")
        print("-"*60)
        
        tabla = PrettyTable()
        tabla.field_names = ["Categoría", "Total", "# Movimientos"]
        tabla.align["Categoría"] = "l"
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
            total = datos_categoria["total"]
            num_movimientos = len(datos_categoria["movimientos"])
            
            tabla.add_row([
                categoria,
                f"${total:,.2f}",
                num_movimientos
            ])
            
            total_mes += total
            total_movimientos_mes += num_movimientos
            
            # Mostrar detalle de movimientos si se solicita
            if mostrar_detalle and num_movimientos > 0:
                print(f"\nDetalle de {categoria}:")
                tabla_detalle = PrettyTable()
                tabla_detalle.field_names = ["Fecha", "Descripción", "Monto"]
                tabla_detalle.align["Descripción"] = "l"
                tabla_detalle.align["Monto"] = "r"
                tabla_detalle.max_width["Descripción"] = 50
                
                for mov in datos_categoria["movimientos"]:
                    fecha = mov.get("Fecha", "")
                    desc = mov.get("Descripción", mov.get("Detalle", ""))
                    monto = abs(float(mov.get("Cargo", 0)))
                    
                    tabla_detalle.add_row([
                        fecha,
                        desc[:50],
                        f"${monto:,.2f}"
                    ])
                
                print(tabla_detalle)
        
        # Agregar fila de totales
        tabla.add_row([
            "TOTAL",
            f"${total_mes:,.2f}",
            total_movimientos_mes
        ])
        
        print(tabla)
    
    print("\n" + "="*60)

def exportar_resumen_a_gsheet(movimientos, gsheet_id=None, nombre_hoja="Resumen"):
    """
    Exporta el resumen categorizado a Google Sheets.
    
    Args:
        movimientos (list): Lista de movimientos
        gsheet_id (str, optional): ID de la hoja de Google Sheets
        nombre_hoja (str): Nombre de la hoja donde se exportará el resumen
        
    Returns:
        bool: True si la exportación fue exitosa, False en caso contrario
    """
    try:
        from scripts.actualizar_gsheet import conectar_gsheet
        
        categorias = cargar_categorias()
        agrupado = agrupar_por_mes_categoria(movimientos, categorias)
        
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
        datos.append(["RESUMEN DE GASTOS POR MES Y CATEGORÍA", "", ""])
        datos.append(["", "", ""])
        
        for mes in meses_ordenados:
            datos.append([mes, "", ""])
            datos.append(["Categoría", "Total", "# Movimientos"])
            
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
                total = datos_categoria["total"]
                num_movimientos = len(datos_categoria["movimientos"])
                
                datos.append([
                    categoria,
                    total,
                    num_movimientos
                ])
                
                total_mes += total
                total_movimientos_mes += num_movimientos
            
            datos.append(["TOTAL", total_mes, total_movimientos_mes])
            datos.append(["", "", ""])
        
        # Actualizar hoja de cálculo
        worksheet.clear()
        worksheet.update('A1', datos)
        
        # Aplicar formato
        worksheet.format('A1', {
            "textFormat": {"bold": True, "fontSize": 14}
        })
        
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
