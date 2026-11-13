import requests
from bs4 import BeautifulSoup
import json

# Enlace directo a tu Yupoo
YUPOO_URL = "https://minkang.x.yupoo.com/albums"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def obtener_productos():
    productos = []
    page = 1
    
    while True:
        url_pag = f"{YUPOO_URL}?page={page}" if page == 1 else f"{YUPOO_URL}?page={page}"
        print(f"Buscando en: {url_pag}")
        
        try:
            response = requests.get(url_pag, headers=headers)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Selectores habituales para los álbumes de Yupoo
            albums = soup.find_all('div', class_='album__main') or soup.find_all('a', class_='album__item')
            
            if not albums:
                # Intento alternativo de búsqueda por etiquetas si cambia el diseño
                albums = soup.select('a.album')
                if not albums:
                    break

            contador_pagina = 0
            for album in albums:
                # Extraer título
                title_elem = album.find('div', class_='album__title') or album.find('span', class_='album__title') or album.find('img')
                if title_elem and title_elem.has_attr('alt'):
                    title = title_elem['alt'].strip()
                elif title_elem:
                    title = title_elem.text.strip()
                else:
                    title = "Camiseta de Fútbol"

                if not title or title == "":
                    title = "Camiseta de Fútbol"

                # Extraer imagen de portada
                img_elem = album.find('img')
                img_url = ""
                if img_elem:
                    img_url = img_elem.get('data-src') or img_elem.get('src') or img_elem.get('data-original')
                    if img_url and img_url.startswith('//'):
                        img_url = "https:" + img_url
                    elif img_url and img_url.startswith('/'):
                        img_url = "https://minkang.x.yupoo.com" + img_url

                if img_url:
                    # Categorización automática inteligente por palabras clave
                    category = "Otros"
                    t_lower = title.lower()
                    if any(k in t_lower for k in ['madrid', 'barcelona', 'atlético', 'valencia', 'sevilla', 'betis', 'laliga', 'real madrid', 'fc barcelona']):
                        category = "LaLiga"
                    elif any(k in t_lower for k in ['premier', 'arsenal', 'chelsea', 'city', 'united', 'liverpool', 'tottenham', 'manchester']):
                        category = "Premier League"
                    elif any(k in t_lower for k in ['retro', 'vintage', 'classic', '90', '80', 'historic', 'remake']):
                        category = "Retro"
                    elif any(k in t_lower for k in ['españa', 'argentina', 'brasil', 'francia', 'selección', 'world cup', 'italy', 'germany', 'portugal']):
                        category = "Selecciones"

                    # Evitar duplicados
                    if not any(p['img'] == img_url for p in productos):
                        productos.append({
                            "title": title,
                            "img": img_url,
                            "category": category
                        })
                        contador_pagina += 1

            # Si en esta página no encontró productos nuevos, salimos del bucle
            if contador_pagina == 0 and page > 1:
                break
                
            page += 1
            if page > 15: # Límite de seguridad de páginas
                break
                
        except Exception as e:
            print(f"Error procesando la página {page}: {e}")
            break

    print(f"Total de productos extraídos: {len(productos)}")
    return productos

if __name__ == "__main__":
    datos = obtener_productos()
    if datos:
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print("Archivo productos.json guardado con éxito.")
    else:
        print("No se encontraron productos.")
