import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://minkang.x.yupoo.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://minkang.x.yupoo.com/"
}

def extraer_todo_yupoo():
    productos = []
    page = 1
    max_paginas = 120

    print("Iniciando extracción desde la raíz de Yupoo...")

    while page <= max_paginas:
        # Añadimos el parámetro de paginación sobre la raíz de álbumes
        url_actual = f"{BASE_URL}albums?page={page}"
        print(f"Escaneando página {page}: {url_actual}")
        
        try:
            response = requests.get(url_actual, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"Fin del catálogo en página {page} (Código: {response.status_code})")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Selectores universales para atrapar los álbumes
            albums = soup.select('.album__main, .album__item, a.album, div.album')
            if not albums:
                all_links = soup.find_all('a', href=lambda x: x and '/albums/' in x)
                albums = [l for l in all_links if l.find('img')]

            if not albums:
                print(f"No se detectaron más álbumes en la página {page}.")
                break

            encontrados = 0
            for album in albums:
                # Extraer título
                title = "Camiseta de Fútbol"
                title_elem = album.find(class_='album__title') or album.find('span') or album.find('img')
                if title_elem:
                    if title_elem.has_attr('alt') and title_elem['alt'].strip():
                        title = title_elem['alt'].strip()
                    elif title_elem.text.strip():
                        title = title_elem.text.strip()

                # Categorización inteligente
                category = "Catálogo General"
                t_lower = title.lower()
                if any(k in t_lower for k in ['madrid', 'barcelona', 'atlético', 'valencia', 'sevilla', 'betis', 'laliga', 'real madrid', 'fc barcelona']):
                    category = "LaLiga"
                elif any(k in t_lower for k in ['premier', 'arsenal', 'chelsea', 'city', 'united', 'liverpool', 'tottenham', 'manchester']):
                    category = "Premier League"
                elif any(k in t_lower for k in ['retro', 'vintage', 'classic', '90', '80', 'historic', 'remake']):
                    category = "Retro"
                elif any(k in t_lower for k in ['españa', 'argentina', 'brasil', 'francia', 'selección', 'world cup', 'italy', 'germany', 'portugal', 'mexico']):
                    category = "Selecciones"

                # Extraer imagen de alta calidad
                img_elem = album.find('img')
                img_url = ""
                if img_elem:
                    img_url = (
                        img_elem.get('data-src') or 
                        img_elem.get('src') or 
                        img_elem.get('data-original') or
                        img_elem.get('data-lazy-src') or
                        img_elem.get('data-origin-src')
                    )
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = "https:" + img_url
                        elif img_url.startswith('/'):
                            img_url = "https://minkang.x.yupoo.com" + img_url

                if img_url and not any(p['img'] == img_url for p in productos):
                    productos.append({
                        "title": title,
                        "img": img_url,
                        "category": category
                    })
                    encontrados += 1

            print(f"-> Página {page}: {encontrados} productos añadidos.")
            
            if encontrados == 0 and page > 1:
                break

            time.sleep(0.4)
            page += 1

        except Exception as e:
            print(f"Error procesando la página {page}: {e}")
            break

    print(f"¡Extracción finalizada! Total global de productos: {len(productos)}")
    return productos

if __name__ == "__main__":
    datos = extraer_todo_yupoo()
    if datos:
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print("Archivo productos.json generado correctamente.")
    else:
        print("No se pudieron extraer productos.")
