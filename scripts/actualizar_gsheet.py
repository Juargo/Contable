import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def cargar_configuracion():
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def conectar_gsheet():
    """Establece conexión con Google Sheets utilizando las credenciales"""
    config = cargar_configuracion()
    creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'credentials.json')
    
    # Definir los alcances
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # Autenticar
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(credentials)
    
    # Abrir la hoja por su ID
    spreadsheet = client.open_by_key(config.get('spreadsheet_id'))
    
    return spreadsheet

def actualizar_movimientos(hoja_nombre, banco, saldo, movimientos):
    """Actualiza los movimientos en la hoja de Google Sheets"""
    try:
        spreadsheet = conectar_gsheet()
        
        # Intentar obtener la hoja, si no existe la creamos
        try:
            worksheet = spreadsheet.worksheet(hoja_nombre)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=hoja_nombre, rows="1000", cols="10")
        
        # Preparar los headers
        if banco.lower() == "bancoestado":
            headers = ["Fecha", "N° Operación", "Descripción", "Cargo", "Fecha Actualización"]
        elif banco.lower() == "bancochile":
            headers = ["Fecha", "Descripción", "Cargo", "Fecha Actualización"]
        elif banco.lower() == "bancosantander":
            headers = ["Fecha", "Detalle", "Cargo", "Fecha Actualización"]
        elif banco.lower() == "bci":
            headers = ["Fecha", "Descripción", "Cargo", "Fecha Actualización"]
        else:
            headers = ["Fecha", "Descripción", "Cargo", "Fecha Actualización"]
        
        # Actualizar encabezados
        worksheet.update('A1', [headers])
        
        # Preparar los datos
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos = []
        
        for mov in movimientos:
            fila = []
            # Agregar datos según el banco
            if "Fecha" in mov:
                fila.append(str(mov["Fecha"]))
            else:
                fila.append("")
                
            if banco.lower() == "bancoestado" and "N° Operación" in mov:
                fila.append(str(mov["N° Operación"]))
                
            if "Descripción" in mov:
                fila.append(str(mov["Descripción"]))
            elif "Detalle" in mov:
                fila.append(str(mov["Detalle"]))
            else:
                fila.append("")
                
            if "Cargo" in mov:
                fila.append(str(mov["Cargo"]))
            else:
                fila.append("")
                
            fila.append(fecha_actual)
            datos.append(fila)
        
        # Actualizar datos
        if datos:
            worksheet.update('A2', datos)
        
        # Actualizar saldo en una celda específica
        worksheet.update('G1', f"Saldo: {saldo}")
        
        print(f"Datos actualizados para {banco} en hoja {hoja_nombre}")
        return True
    except Exception as e:
        print(f"Error al actualizar datos: {e}")
        return False

if __name__ == "__main__":
    print("Este script está diseñado para ser importado. Para ejecutarlo, use run.py")
