from prettytable import PrettyTable
from datetime import datetime

def mostrar_resumen_datos(banco, saldo, movimientos):
    """
    Muestra en consola un resumen de los datos procesados del banco.
    
    Args:
        banco (str): Nombre del banco
        saldo (float): Saldo disponible o contable
        movimientos (list): Lista de diccionarios con los movimientos
    """
    print("\n" + "="*50)
    print(f"RESUMEN DE DATOS: {banco.upper()}")
    print("="*50)
    
    # Mostrar saldo
    if saldo != 0 and saldo is not None:
        print(f"\nSaldo: ${saldo:,.2f}")
    else:
        print("\nSaldo no disponible")
    
    # Filtrar movimientos con cargo cero o nulo
    movimientos_validos = []
    for mov in movimientos:
        cargo = mov.get("Cargo", 0)
        if cargo is None:
            continue
        
        try:
            if isinstance(cargo, str):
                cargo = cargo.replace("$", "").replace(".", "").replace(",", ".")
                cargo = float(cargo)
            
            if cargo == 0:
                continue
                
            movimientos_validos.append(mov)
        except (ValueError, TypeError):
            # Si no podemos convertir a número, omitimos el movimiento
            continue
    
    # Mostrar resumen de movimientos
    print(f"\nTotal de movimientos (cargos) encontrados: {len(movimientos_validos)}")
    
    if movimientos_validos:
        total_cargos = sum(float(mov.get("Cargo", 0)) for mov in movimientos_validos 
                          if isinstance(mov.get("Cargo"), (int, float)) or 
                          (isinstance(mov.get("Cargo"), str) and mov.get("Cargo").replace('-', '').replace(',', '').replace('.', '').isdigit()))
        print(f"Suma total de cargos: ${total_cargos:,.2f}")
        
        # Mostrar tabla de movimientos
        print("\nDETALLE DE MOVIMIENTOS:")
        tabla = PrettyTable()
        
        # Determinar columnas según tipo de banco
        if banco.lower() == "bancoestado":
            tabla.field_names = ["Fecha", "N° Operación", "Descripción", "Cargo"]
        elif banco.lower() in ["bancochile", "bci"]:
            tabla.field_names = ["Fecha", "Descripción", "Cargo"]
        elif banco.lower() == "bancosantander":
            tabla.field_names = ["Fecha", "Detalle", "Cargo"]
        else:
            tabla.field_names = ["Fecha", "Descripción", "Cargo"]
        
        # Ajustar ancho máximo de columnas
        tabla.max_width = 40
        
        # Añadir filas a la tabla
        for mov in movimientos_validos[:10]:  # Mostrar solo los primeros 10 para no saturar la consola
            if banco.lower() == "bancoestado":
                tabla.add_row([
                    mov.get("Fecha", ""),
                    mov.get("N° Operación", ""),
                    mov.get("Descripción", "")[:40],
                    mov.get("Cargo", "")
                ])
            elif banco.lower() in ["bancochile", "bci"]:
                tabla.add_row([
                    mov.get("Fecha", ""),
                    mov.get("Descripción", "")[:40],
                    mov.get("Cargo", "")
                ])
            elif banco.lower() == "bancosantander":
                tabla.add_row([
                    mov.get("Fecha", ""),
                    mov.get("Detalle", "")[:40],
                    mov.get("Cargo", "")
                ])
        
        print(tabla)
        
        if len(movimientos_validos) > 10:
            print(f"... y {len(movimientos_validos) - 10} movimientos más.")
    
    print("\n" + "="*50)
    print(f"FIN DEL RESUMEN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Ejemplo de uso
    ejemplo_movimientos = [
        {"Fecha": "2023-05-01", "Descripción": "Compra en tienda ABC", "Cargo": -50000},
        {"Fecha": "2023-05-02", "Descripción": "Retiro en cajero automático", "Cargo": -100000},
    ]
    
    mostrar_resumen_datos("BancoEjemplo", 500000, ejemplo_movimientos)
