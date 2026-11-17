import requests
import json
import time
import re

# La URL secreta de la API de Yupoo
API_URL = "https://minkang.x.yupoo.com/api/categories/albums"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://minkang.x.yupoo.com/categories"
}

def clasificar(title):
    t = title.upper()
    if re.search(r"\bNK\b", t) or "NIKE" in t: return "Nike"
    if re.search(r"\bJB\b", t) or "JORDAN" in t: return "Jordan"
    if "SHORT" in t: return "Shorts"
    if "HOODIE" in t or "SUDADERA" in t or "SWEAT" in t: return "Sudaderas"
    if "PANT" in t or "JOGGER" in t: return "Pantalones"
    if "JERSEY" in t or "CAMISETA" in t or "SHIRT" in t: return "Camisetas"
    if "SOCK" in t or "CAP" in t or "BAG" in t or "ACCESSOR" in t: return "Accesorios"
    return "Catálogo General"

def main():
    print("[*] Iniciando extracción vía API interna...")
    todos_los_productos = []
    pagina = 1
    
    while True:
        print(f"[*] Pidiendo página {pagina}...")
        params = {"page": pagina}
        
        try:
            respuesta = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except Exception as e:
            print(f"[!] Error en la petición: {e}")
            break

        # La API devuelve los álbumes dentro de la clave 'albums' o directamente en una lista
        albumes = datos.get('albums', []) if isinstance(datos, dict) else datos
        
        if not albumes:
            print("[*] No hay más productos. Fin del catálogo.")
            break

        for album in albumes:
            # Extraemos los datos que nos interesan del JSON
            title = album.get('title', '').strip()
            
            # Ignoramos los álbumes vacíos, bloqueados o con contraseña
            if not title or "加密相册" in title or len(title) < 3:
                continue
                
            # Sacamos la imagen (Yupoo usa 'cover_url' o similar en su API)
            img = album.get('cover_url', '')
            if img and not img.startswith('http'):
                img = f"https:{img}" if img.startswith('//') else f"https://photo.yupoo.com{img}"

            todos_los_productos.append({
                "title": title,
                "category": clasificar(title),
                "img": img
            })

        print(f"    -> {len(albumes)} encontrados en esta página.")
        pagina += 1
        time.sleep(1) # Pausa de 1 segundo para no saturar

    # Guardar el JSON
    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump(todos_los_productos, f, ensure_ascii=False, indent=2)
        
    print(f"[+] ¡Éxito! {len(todos_los_productos)} productos guardados en productos.json")

if __name__ == "__main__":
    main()
