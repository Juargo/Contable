"""
Script para migrar el formato antiguo de categorías al nuevo formato con subcategorías.
"""
import os
import json
import sys

def migrar_categorias():
    """
    Migra el formato antiguo de categorías al nuevo con subcategorías.
    """
    try:
        # Ruta al archivo de categorías
        ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        ruta_categorias = os.path.join(ruta_base, 'config', 'categorias.json')
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_categorias):
            print(f"Archivo de categorías no encontrado en {ruta_categorias}")
            return False
        
        # Hacer una copia de respaldo
        ruta_backup = os.path.join(ruta_base, 'config', 'categorias_backup.json')
        with open(ruta_categorias, 'r', encoding='utf-8') as f:
            categorias_antiguas = json.load(f)
            
        with open(ruta_backup, 'w', encoding='utf-8') as f:
            json.dump(categorias_antiguas, f, indent=2, ensure_ascii=False)
        
        print(f"Copia de respaldo creada en {ruta_backup}")
        
        # Verificar si ya tiene el nuevo formato
        primera_categoria = list(categorias_antiguas.keys())[0]
        if isinstance(categorias_antiguas[primera_categoria], dict) and "subcategorias" in categorias_antiguas[primera_categoria]:
            print("El archivo ya tiene el formato nuevo con subcategorías.")
            return True
        
        # Convertir al nuevo formato
        categorias_nuevas = {}
        for categoria, palabras_clave in categorias_antiguas.items():
            categorias_nuevas[categoria] = {
                "palabras_clave": [palabra.upper() for palabra in palabras_clave if palabra],
                "subcategorias": {
                    "General": {
                        "palabras_clave": palabras_clave
                    },
                    "Otros": {
                        "palabras_clave": []
                    }
                }
            }
        
        # Guardar el nuevo archivo
        with open(ruta_categorias, 'w', encoding='utf-8') as f:
            json.dump(categorias_nuevas, f, indent=2, ensure_ascii=False)
        
        print(f"Migración completada. Archivo actualizado: {ruta_categorias}")
        return True
        
    except Exception as e:
        print(f"Error al migrar categorías: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando migración de categorías...")
    if migrar_categorias():
        print("¡Migración exitosa!")
        sys.exit(0)
    else:
        print("La migración falló.")
        sys.exit(1)
