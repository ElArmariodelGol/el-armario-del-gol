import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

URL = "https://minkang.x.yupoo.com/categories"
# Cabeceras idénticas a las de un navegador real
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

    # 1. EXTRAER EL MENÚ LATERAL (Basado en tu archivo yupoo.txt)
    # Buscamos los enlaces que estén dentro de las categorías
    for a in soup.select(".showheader__category_item a.showheader__link"):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        
        # Ignoramos menús de navegación
        if not text or text in ["Menu", "Menu 2"]:
            continue
            
        if "/categories/" in href:
            menu_final.append({
                "name": text,
                "url": urljoin("https://minkang.x.yupoo.com", href),
                "img": "imagenes/logo.jpg"
            })

    # 2. EXTRAER LOS PRODUCTOS DE LA VISTA PRINCIPAL
    # Si Yupoo carga las fotos en el HTML, las sacamos aquí
    for alb in soup.select(".album__main"):
        title_el = alb.select_one(".album__title")
        img_el = alb.select_one("img")
        
        if title_el and img_el:
            img_url = img_el.get("data-src") or img_el.get("data-original") or img_el.get("src") or ""
            if img_url and not img_url.startswith("http"):
                img_url = urljoin("https://minkang.x.yupoo.com", img_url)
                
            productos_final.append({
                "title": title_el.get_text(strip=True),
                "img": img_url,
                "category": "Todos"
            })

    # 3. SI EL MENÚ FALLA, USAMOS TU LISTA (Extraída de tu archivo)
    if not menu_final:
        print("[*] Menú no encontrado en el HTML. Usando fallback exacto de tu archivo...")
        categorias_exactas = [
            "new season", "La Liga", "Brasileiro Série A", "2026 FIFA World Cup", 
            "NRL", "newF1", "Brazil team column", "🧦Socks", "🏈NFL", "🏁F1", 
            "⚽Polos", "Shorts", "Worldwide Other League", "Retro football shirt", 
            "💨🧥Windbreaker/Training Top", "⚽💪🏻Player Version", "⚽💁🏻‍♀️Women's shirt", 
            "⚽🌍 National Teams", "⚽👦🏻kids kit size：16-28", "👶🏻Baby jersey size:9-12", 
            "⚽🧤Goalkeeper kit", "⚽Long sleeve shirt", "Premier League", "Serie A", 
            "Bundesliga", "Liga Profesional", "Primeira Liga", "Ligue 1", 
            "EREDIVISIE", "Scottish League", "Chilean League", "MLS", "LIGA MX", 
            "🇯🇵Japan League", "🔥 Clearance Sale: $9/PCS, Minimum Order 5PCS 🔥", 
            "📏Sizes"
        ]
        for c in categorias_exactas:
            menu_final.append({"name": c, "url": "#", "img": "imagenes/logo.jpg"})

    # 4. GUARDAR
    with open("productos.json", "w", encoding="utf-8") as f:
        json.dump({"menu": menu_final, "productos": productos_final}, f, ensure_ascii=False, indent=2)

    print(f"[+] ¡ÉXITO! {len(menu_final)} categorías y {len(productos_final)} productos guardados.")

if __name__ == "__main__":
    main()
