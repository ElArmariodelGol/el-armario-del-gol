import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE_URL = "https://minkang.x.yupoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

def extraer_categoria(titulo, dicc_equipos):
    """Asigna la categoría basándose en el título del producto."""
    t = titulo.upper()
    
    # 1. Comprobar si el título contiene el nombre de algún equipo
    for liga, equipos in dicc_equipos.items():
        for equipo in equipos:
            if equipo.upper() in t:
                return liga
                
    # 2. Si no es un equipo, clasificar por tipo de prenda o marca
    if "NK" in t or "NIKE" in t: return "Nike"
    if "JB" in t or "JORDAN" in t: return "Jordan"
    if "F1" in t or "FERRARI" in t or "MCLAREN" in t: return "F1"
    if "NFL" in t: return "NFL"
    if "RETRO" in t: return "Retro"
    if "SHORT" in t: return "Shorts"
    
    return "Catálogo General"

def main():
    print("[*] Iniciando extracción masiva de Yupoo...")
    
    # 1. PRIMERO: Leemos la página 1 para sacar el menú de ligas y equipos
    print("[*] Leyendo menú lateral de categorías...")
    r_menu = requests.get(f"{BASE_URL}/categories?is_ajax=1", headers=HEADERS)
    soup_menu = BeautifulSoup(r_menu.text, "lxml")
    
    dicc_equipos = {}
    for li in soup_menu.select(".showheader__category_item"):
        a_principal = li.select_one(".showheader__link")
        if not a_principal: continue
        nombre_liga = a_principal.get_text(strip=True)
        
        # Ignoramos menús que no son ligas
        if nombre_liga in ["Menu", "Menu 2", "new season", "Casual Shorts"]: continue
        
        equipos = []
        for sub_a in li.select(".showheader__child_link"):
            equipos.append(sub_a.get_text(strip=True))
            
        if equipos:
            dicc_equipos[nombre_liga] = equipos

    print(f"[*] Ligas detectadas: {len(dicc_equipos)}")

    # 2. SEGUNDO: Recorremos las páginas para coger TODOS los productos
    todos_los_productos = []
    
    for pagina in range(1, 201): # Hasta 200 páginas
        url = f"{BASE_URL}/categories?page={pagina}"
        print(f"[*] Leyendo productos de la página {pagina}...")
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                break
                
            soup = BeautifulSoup(r.text, "lxml")
            albumes = soup.select(".album__main")
            
            if not albumes:
                print("[*] Fin del catálogo alcanzado.")
                break
                
            for alb in albumes:
                title_el = alb.select_one(".album__title")
                img_el = alb.select_one("img")
                
                if title_el and img_el:
                    titulo = title_el.get_text(strip=True)
                    img_url = img_el.get("data-src") or img_el.get("data-original") or img_el.get("src") or ""
                    
                    if img_url and not img_url.startswith("http"):
                        img_url = urljoin(BASE_URL, img_url)
                    
                    # TRUCO: Usar la imagen medium para que se vea mejor
                    if img_url:
                        img_url = img_url.replace("/small.jpg", "/medium.jpg")

                    todos_los_productos.append({
                        "title": titulo,
                        "img": img_url,
                        "category": extraer_categoria(titulo, dicc_equipos)
                    })
            
            time.sleep(1) # Pausa para no saturar
            
        except Exception as e:
            print(f"[!] Error en página {pagina}: {e}")
            break

    # 3. Guardar el JSON (CON CORCHETES POR FUERA, como lo quiere tu web)
    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump(todos_los_productos, f, ensure_ascii=False, indent=2)
        
    print(f"[+] ¡ÉXITO! {len(todos_los_productos)} productos guardados en productos.json")

if __name__ == "__main__":
    main()
