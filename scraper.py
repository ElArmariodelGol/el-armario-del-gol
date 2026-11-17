import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin

BASE_URL = "https://minkang.x.yupoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://minkang.x.yupoo.com/"
}

def extraer_categoria(titulo):
    t = titulo.upper()
    if any(x in t for x in ["REAL MADRID", "BARCELONA", "ATLETICO", "SEVILLA", "VALENCIA", "VILLARREAL", "BETIS", "CELTA"]): return "La Liga"
    if any(x in t for x in ["M-U", "LFC", "ARSENAL", "CHELSEA", "CITY", "TOTTENHAM", "UNITED", "NEWCASTLE"]): return "Premier League"
    if any(x in t for x in ["INTER", "MILAN", "JUV", "NAPOLI", "ROMA", "LAZIO"]): return "Serie A"
    if "NK" in t or "NIKE" in t: return "Nike"
    if "JB" in t or "JORDAN" in t: return "Jordan"
    if "F1" in t or "FERRARI" in t or "MCLAREN" in t: return "F1"
    if "NFL" in t: return "NFL"
    if "RETRO" in t: return "Retro"
    if "SHORT" in t: return "Shorts"
    return "Catálogo General"

def descargar_imagen(url, nombre_archivo):
    try:
        # Usamos el proxy para saltarnos el bloqueo de Yupoo
        url_proxy = f"https://images.weserv.nl/?url={url.replace('https://', '')}"
        
        r = requests.get(url_proxy, timeout=20)
        if r.status_code == 200:
            # Comprobamos que lo que ha descargado es una imagen de verdad
            if r.headers.get('Content-Type', '').startswith('image'):
                with open(nombre_archivo, "wb") as f:
                    f.write(r.content)
                return True
    except Exception as e:
        print(f"[!] Error descargando {url}: {e}")
    return False

def main():
    print("[*] Iniciando extracción y descarga...")
    
    # Crear carpeta para las fotos si no existe
    os.makedirs("imagenes/productos", exist_ok=True)
    
    todos_los_productos = []
    contador_fotos = 0
    
    for pagina in range(1, 201):
        url = f"{BASE_URL}/categories?page={pagina}"
        print(f"[*] Leyendo página {pagina}...")
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200: break
                
            soup = BeautifulSoup(r.text, "lxml")
            albumes = soup.select(".album__main")
            
            if not albumes: break
                
            for alb in albumes:
                title_el = alb.select_one(".album__title")
                img_el = alb.select_one("img")
                
                if title_el and img_el:
                    titulo = title_el.get_text(strip=True)
                    img_url = img_el.get("data-src") or img_el.get("data-original") or img_el.get("src") or ""
                    
                    if img_url and not img_url.startswith("http"):
                        img_url = urljoin(BASE_URL, img_url)
                    
                    if img_url:
                        # Generar nombre único para la foto
                        nombre_foto = f"foto_{pagina}_{contador_fotos}.jpg"
                        ruta_local = f"imagenes/productos/{nombre_foto}"
                        
                        # Descargar la foto a tu GitHub
                        exito = descargar_imagen(img_url, ruta_local)
                        
                        if exito:
                            todos_los_productos.append({
                                "title": titulo,
                                "img": ruta_local, 
                                "category": extraer_categoria(titulo)
                            })
                            contador_fotos += 1
            
            print(f"    -> {len(albumes)} productos procesados.")
            time.sleep(1.5) # Pausa para no saturar el proxy
            
        except Exception as e:
            print(f"[!] Error: {e}")
            break

    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump(todos_los_productos, f, ensure_ascii=False, indent=2)
        
    print(f"[+] ¡ÉXITO! {len(todos_los_productos)} productos y fotos guardadas.")

if __name__ == "__main__":
    main()
