import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://minkang.x.yupoo.com/albums"

# Cabeceras completas de navegador real para evitar bloqueos de Yupoo
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://minkang.x.yupoo.com/",
    "Connection": "keep-alive"
}

def extraer_todo_yupoo():
    productos = []
    page = 1
    max_paginas = 120

    print("Iniciando extracción robusta de Yupoo...")

    while page <= max_paginas:
        url_actual = f"{BASE_URL}?page={page}"
        print(f"Escaneando página {page}...")
        
        try:
            response = requests.get(url_actual, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"Página {page} respondió con código {response.status_code}. Fin del recorrido.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Selectores amplios adaptados a los contenedores de álbumes de Yupoo
            albums = soup.select('.album__main, .album__item, a.album, .showalbumlist__item')
            
            if not albums:
                print(f"No se detectaron álbumes en la página {page}. Fin de la extracción.")
                break

            encontrados = 0
            for album in albums:
                # 1. Extraer título
                title = "Camiseta de Fútbol"
                title_elem = album.find(class_='album__title') or album.find('span') or album.find('img')
                if title_elem:
                    if title_elem.has_attr('alt') and title_elem['alt'].strip():
                        title = title_elem['alt'].strip()
                    elif title_elem.text.strip():
                        title = title_elem.text.strip()

                # 2. Asignación automática inteligente de categoría
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

                # 3. Extraer imagen de alta calidad
                img_elem = album.find('img')
                img_url = ""
                if img_elem:
                    img_url = (
                        img_elem.get('data-src') or 
                        img_elem.get('src') or 
                        img_elem.get('data-original') or
                        img_elem.get('data-lazy-src')
                    )
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = "https:" + img_url
                        elif img_url.startswith('/'):
                            img_url = "https://minkang.x.yupoo.com" + img_url

                if img_url:
                    # Evitar duplicados
                    if not any(p['img'] == img_url for p in productos):
                        productos.append({
                            "title": title,
                            "img": img_url,
                            "category": category
                        })
                        encontrados += 1

            print(f"-> Página {page}: {encontrados} camisetas recopiladas.")
            
            if encontrados == 0 and page > 1:
                break

            time.sleep(0.5)
            page += 1

        except Exception as e:
            print(f"Error procesando la página {page}: {e}")
            break

    print(f"¡Extracción terminada! Total global de camisetas: {len(productos)}")
    return productos

if __name__ == "__main__":
    datos = extraer_todo_yupoo()
    if datos:
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print("Archivo productos.json guardado correctamente.")
    else:
        print("No se encontraron productos.")
