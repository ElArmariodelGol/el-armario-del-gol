import requests
import json
import re

API_URL = "https://minkang.x.yupoo.com/api/categories/albums"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://minkang.x.yupoo.com/categories"
}

def main():
    print("[*] Extrayendo las categorías reales de Yupoo...")
    
    # Quitamos el bucle de páginas, Yupoo devuelve todo el árbol de categorías de golpe
    try:
        respuesta = requests.get(API_URL, headers=HEADERS, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:
        print(f"[!] Error: {e}")
        return

    # Yupoo devuelve las categorías dentro de 'category_list'
    categorias = datos.get('category_list', [])
    
    if not categorias:
        print("[!] No se encontraron categorías.")
        return

    resultado = []
    
    # Recorremos las categorías principales
    for cat in categorias:
        nombre = cat.get('name', '').strip()
        cat_id = cat.get('id')
        
        # Ignoramos las que no tengan nombre o sean la raíz
        if not nombre or nombre == "All Categories":
            continue
            
        img = cat.get('cover_url', '')
        if img and not img.startswith('http'):
            img = f"https:{img}" if img.startswith('//') else f"https://photo.yupoo.com{img}"

        resultado.append({
            "title": nombre,
            "category": "Menu Principal",
            "img": img,
            "album_url": f"https://minkang.x.yupoo.com/categories/{cat_id}"
        })

    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
        
    print(f"[+] ¡Éxito! Se han guardado {len(resultado)} categorías en productos.json")

if __name__ == "__main__":
    main()
