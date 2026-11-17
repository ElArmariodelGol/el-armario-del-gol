import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://minkang.x.yupoo.com/categories"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

def main():
    print("[*] Conectando a Yupoo...")
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "lxml")

    menu_final = []
    productos_final = []

    # 1. Extraer el menú de la izquierda (Categorías)
    # Buscamos los enlaces que estén dentro de las listas de categorías
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        
        # Filtramos enlaces basura o menús de navegación
        if not text or text in ["All categories", "Menu", "Menu 2", "Home", "Album", "Contact"]:
            continue
            
        # Si el enlace lleva a una categoría o álbum
        if "/categories/" in href or "/albums/" in href:
            if not any(m['name'] == text for m in menu_final):
                menu_final.append({
                    "name": text,
                    "url": f"https://minkang.x.yupoo.com{href}" if href.startswith("/") else href,
                    "img": "imagenes/logo.jpg"
                })

    # 2. Extraer las carpetas/productos que se ven en el centro
    # Buscamos los bloques de álbumes
    for alb in soup.select(".album__main, .showalbumheader__galleryitem"):
        # Título
        title_el = alb.select_one(".album__title, .showalbumheader__gallerytitle")
        # Imagen
        img_el = alb.select_one("img")
        
        if title_el and img_el:
            title = title_el.get_text(strip=True)
            img_url = img_el.get("data-src") or img_el.get("data-original") or img_el.get("src") or ""
            
            if img_url and not img_url.startswith("http"):
                img_url = f"https:{img_url}" if img_url.startswith("//") else f"https://minkang.x.yupoo.com{img_url}"
            
            # Evitar duplicados
            if not any(p['title'] == title for p in productos_final):
                productos_final.append({
                    "title": title,
                    "img": img_url,
                    "category": "All categories"
                })

    # 3. Si por lo que sea no hay menú (porque Yupoo carga el menú con JS), forzamos las de tu foto
    if not menu_final:
        print("[*] Menú no encontrado en HTML (posible carga JS). Usando fallback...")
        categorias_fijas = [
            "new season", "Casual Shorts", "La Liga", "Brasileiro Série A", 
            "2026 FIFA World Cup", "NRL", "newF1", "Brazil team column",
            "Worldwide Other League", "NFL", "Bundesliga", "EREDIVISIE", 
            "LIGA MX", "Premier League", "Serie A", "Ligue 1", "MLS"
        ]
        for c in categorias_fijas:
            menu_final.append({"name": c, "url": "#", "img": "imagenes/logo.jpg"})

    # 4. Guardar JSON
    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump({"menu": menu_final, "productos": productos_final}, f, ensure_ascii=False, indent=2)

    print(f"[+] ¡ÉXITO! {len(menu_final)} categorías y {len(productos_final)} productos guardados.")

if __name__ == "__main__":
    main()
