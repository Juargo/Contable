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
            # Si ya tiene el formato nuevo, verificar si tiene palabras_clave a nivel de categoría
            for categoria, datos in categorias_antiguas.items():
                if "palabras_clave" in datos:
                    # Migrar palabras clave a subcategoría "Otros" y eliminar palabras_clave a nivel de categoría
                    if "Otros" not in datos["subcategorias"]:
                        datos["subcategorias"]["Otros"] = {"palabras_clave": []}
                    
                    # Solo agregar palabras clave que no estén ya en alguna subcategoría
                    todas_palabras_subcats = set()
                    for subcat_datos in datos["subcategorias"].values():
                        todas_palabras_subcats.update(subcat_datos.get("palabras_clave", []))
                    
                    palabras_a_agregar = [p for p in datos["palabras_clave"] if p not in todas_palabras_subcats]
                    datos["subcategorias"]["Otros"]["palabras_clave"].extend(palabras_a_agregar)
                    
                    # Eliminar palabras_clave a nivel de categoría
                    del datos["palabras_clave"]
            
            print("Archivo actualizado: se movieron las palabras clave de categorías a subcategorías.")
            
        else:
            # Convertir al nuevo formato
            categorias_nuevas = {}
            for categoria, palabras_clave in categorias_antiguas.items():
                categorias_nuevas[categoria] = {
                    "subcategorias": {
                        "General": {
                            "palabras_clave": palabras_clave
                        },
                        "Otros": {
                            "palabras_clave": []
                        }
                    }
                }
            
            categorias_antiguas = categorias_nuevas
            print("Archivo migrado al nuevo formato con subcategorías.")
        
        # Guardar el archivo actualizado
        with open(ruta_categorias, 'w', encoding='utf-8') as f:
            json.dump(categorias_antiguas, f, indent=2, ensure_ascii=False)
        
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
