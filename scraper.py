import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://minkang.x.yupoo.com/albums"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://minkang.x.yupoo.com/"
}

def extraer_todo_yupoo():
    productos = []
    page = 1
    max_paginas = 120

    print("Iniciando extracción universal de Yupoo...")

    while page <= max_paginas:
        url_actual = f"{BASE_URL}?page={page}"
        print(f"Escaneando página {page}...")
        
        try:
            response = requests.get(url_actual, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"Página {page} no disponible. Código: {response.status_code}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Selector ultra-robusto: busca cualquier enlace que lleve a un álbum y contenga imagen
            albums = soup.find_all('a', href=lambda x: x and '/albums/' in x)
            valid_albums = [a for a in albums if a.find('img')]

            if not valid_albums:
                valid_albums = soup.select('.album, .album__item, .album__main')

            if not valid_albums:
                print(f"No se detectaron más álbumes en la página {page}. Fin de la extracción.")
                break

            encontrados = 0
            for album in valid_albums:
                # 1. Título
                title = "Camiseta de Fútbol"
                title_elem = album.find(class_='album__title') or album.find('span') or album.find('img')
                if title_elem:
                    if title_elem.has_attr('alt') and title_elem['alt'].strip():
                        title = title_elem['alt'].strip()
                    elif title_elem.text.strip():
                        title = title_elem.text.strip()

                # 2. Categoría original de Yupoo si está presente en el bloque
                category = "Catálogo General"
                cat_elem = album.find(class_='category') or album.find(class_='album__category')
                if cat_elem and cat_elem.text.strip():
                    category = cat_elem.text.strip()

                # 3. Imagen de alta calidad
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
            print(f"Error en página {page}: {e}")
            break

    print(f"Total global de productos extraídos: {len(productos)}")
    return productos

if __name__ == "__main__":
    datos = extraer_todo_yupoo()
    if datos:
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print("Guardado en productos.json correctamente.")
    else:
        print("No se encontraron productos.")
