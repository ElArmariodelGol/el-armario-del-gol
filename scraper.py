import requests
import json
import sys

# La URL exacta que has encontrado en la pestaña Network
API_URL = "https://minkang.x.yupoo.com/categories?is_ajax=1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://minkang.x.yupoo.com/categories"
}

def main():
    print("[*] Conectando a la API interna de Yupoo...")
    
    try:
        r = requests.get(API_URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
        datos = r.json()
    except Exception as e:
        print(f"[!] Error de conexión: {e}")
        sys.exit(1)

    # Extraemos las categorías del menú
    categorias = datos.get('category_list', [])
    menu_final = []
    
    for cat in categorias:
        nombre = cat.get('name', '').strip()
        
        # Filtramos los menús basura
        if not nombre or nombre in ["All categories", "Menu", "Menu 2", "new season", "newF1"]: 
            continue

        # Sacamos la foto de portada de la carpeta
        img = cat.get('cover_url', '')
        if img and not img.startswith('http'):
            img = f"https:{img}" if img.startswith('//') else f"https://photo.yupoo.com{img}"
        
        # Si no hay portada, ponemos el logo
        if not img:
            img = "imagenes/logo.jpg" 

        menu_final.append({
            "name": nombre,
            "img": img,
            "count": cat.get('album_count', 20) # Sacamos el numero real de productos
        })

    # Guardamos el JSON
    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump({"menu": menu_final}, f, ensure_ascii=False, indent=2)
        
    print(f"[+] ¡Éxito! Se han guardado {len(menu_final)} categorías.")

if __name__ == "__main__":
    main()
