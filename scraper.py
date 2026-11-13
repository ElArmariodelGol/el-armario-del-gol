import os
import json
import re
import requests
from bs4 import BeautifulSoup

# CONFIGURACIÓN
YUPOO_URL = "https://minkang.x.yupoo.com/albums?tab=gallery"
IMG_DIR = "imagenes"
JSON_FILE = "productos.json"
PRECIO_DEFECTO = 25  # Precio si no lo pones en el título de Yupoo

os.makedirs(IMG_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": YUPOO_URL  # Clave para que Yupoo deje descargar las fotos
}

def detectar_categoria(titulo):
    t = titulo.lower()
    if any(x in t for x in ["madrid", "barcelona", "atletico", "betis", "sevilla", "laliga"]):
        return "LaLiga"
    if any(x in t for x in ["arsenal", "chelsea", "liverpool", "city", "united", "premier"]):
        return "Premier League"
    if any(x in t for x in ["españa", "espana", "argentina", "brasil", "francia", "selección"]):
        return "Selecciones"
    if any(x in t for x in ["retro", "199", "200", "classic"]):
        return "Retro"
    return "Otros"

def extraer_precio(titulo):
    # Si pones "25€" o "25EUR" en el título de Yupoo, lo detecta solo
    match = re.search(r'(\d+)\s*(?:€|eur)', titulo, re.IGNORECASE)
    return int(match.group(1)) if match else PRECIO_DEFECTO

def actualizar_catalogo():
    print("Conectando con Yupoo...")
    resp = requests.get(YUPOO_URL, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    albumes = soup.select(".album__main")
    productos = []

    for idx, album in enumerate(albumes, start=1):
        titulo_el = album.select_one(".album__title")
        img_el = album.select_one("img")
        
        if not titulo_el or not img_el:
            continue

        titulo = titulo_el.get_text(strip=True)
        # Yupoo guarda la imagen real en data-origin-src o src
        img_url = img_el.get("data-origin-src") or img_el.get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url

        # Descargar imagen localmente
        nombre_archivo = f"camiseta_{idx}.jpg"
        ruta_local = os.path.join(IMG_DIR, nombre_archivo)
        
        img_data = requests.get(img_url, headers=headers).content
        with open(ruta_local, "wb") as f:
            f.write(img_data)

        productos.append({
            "id": idx,
            "title": titulo,
            "category": detectar_categoria(titulo),
            "price": extraer_precio(titulo),
            "img": f"{IMG_DIR}/{nombre_archivo}"
        })
        print(f"Guardado: {titulo}")

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)
    print(f"¡Listo! {len(productos)} productos actualizados.")

if __name__ == "__main__":
    actualizar_catalogo()