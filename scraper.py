import requests
import json
import time

BASE_URL = "https://minkang.x.yupoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": f"{BASE_URL}/categories"
}

def main():
    print("[*] Extrayendo menú de categorías idéntico a Yupoo...")
    
    try:
        # Endpoint que devuelve el menú lateral de Yupoo
        r = requests.get(f"{BASE_URL}/api/categories", headers=HEADERS, timeout=15)
        r.raise_for_status()
        datos = r.json()
    except Exception as e:
        print(f"[!] Error al conectar: {e}")
        return

    categorias = datos.get('category_list', [])
    resultado = []

    # Filtramos para que queden exactamente las que salen en tu foto
    for cat in categorias:
        nombre = cat.get('name', '').strip()
        cat_id = cat.get('id')
        
        # Ignoramos los menús basura o vacíos de Yupoo
        if not nombre or nombre in ["All categories", "Menu", "Menu 2"]:
            continue

        # Sacamos la foto de portada de la carpeta
        img = cat.get('cover_url', '')
        if img and not img.startswith('http'):
            img = f"https:{img}" if img.startswith('//') else f"https://photo.yupoo.com{img}"

        resultado.append({
            "id": cat_id,
            "name": nombre,
            "img": img,
            "count": cat.get('album_count', 0) # El numero de productos que tiene dentro
        })

    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
        
    print(f"[+] ¡Éxito! Menú guardado con {len(resultado)} categorías.")

if __name__ == "__main__":
    main()
