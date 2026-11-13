import requests
from bs4 import BeautifulSoup
import json
import time

# Enlace base de tus álbumes en Yupoo
BASE_URL = "https://minkang.x.yupoo.com/albums"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def extraer_todo_yupoo():
    productos = []
    page = 1
    max_paginas = 120

    print("Iniciando extracción y respeto de categorías originales de Yupoo...")

    while page <= max_paginas:
        url_actual = f"{BASE_URL}?page={page}"
        print(f"Consultando página {page}...")
        
        try:
            response = requests.get(url_actual, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Página {page} no disponible (Código {response.status_code}). Fin.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar contenedores de álbumes
            albums = soup.find_all('div', class_='album__main') or soup.find_all('div', class_='album') or soup.find_all('a', class_='album__item')
            if not albums:
                albums = soup.select('a.album')
            
            if not albums:
                print(f"No se detectaron álbumes en la página {page}. Fin de la extracción.")
                break

            encontrados_en_pagina = 0
            for album in albums:
                # 1. Extraer título
                title_elem = album.find('div', class_='album__title') or album.find('span') or album.find('img')
                title = "Camiseta de Fútbol"
                if title_elem:
                    if title_elem.has_attr('alt') and title_elem['alt'].strip():
                        title = title_elem['alt'].strip()
                    elif title_elem.text.strip():
                        title = title_elem.text.strip()

                # 2. Extraer Categoría original de Yupoo (buscando clases o etiquetas nativas de categorías del sitio)
                category = "Catálogo General"
                cat_elem = album.find('div', class_='album__category') or album.find('span', class_='category') or album.find('a', class_='category')
                if cat_elem and cat_elem.text.strip():
                    category = cat_elem.text.strip()
                else:
                    # Si Yupoo agrupa por carpetas o usa la primera palabra descriptiva del título/etiqueta
                    # Intentamos extraer alguna pista de categoría corporativa si existe en el contenedor
                    parent_cat = album.find_parent('div', class_='category__item')
                    if parent_cat:
                        cat_title = parent_cat.find('h3') or parent_cat.find('span')
                        if cat_title:
                            category = cat_title.text.strip()

                # 3. Extraer imagen
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
                    # Evitar duplicados exactos
                    if not any(p['img'] == img_url for p in productos):
                        productos.append({
                            "title": title,
                            "img": img_url,
                            "category": category
                        })
                        encontrados_en_pagina += 1

            print(f"-> Página {page}: {encontrados_en_pagina} camisetas añadidas con sus categorías originales.")
            
            if encontrados_en_pagina == 0 and page > 1:
                break

            time.sleep(0.3)
            page += 1

        except Exception as e:
            print(f"Error en página {page}: {e}")
            break

    print(f"Total global de camisetas extraídas: {len(productos)}")
    return productos

if __name__ == "__main__":
    datos = extraer_todo_yupoo()
    if datos:
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print("Guardado en productos.json con éxito respetando categorías de Yupoo.")
    else:
        print("No se encontraron productos.")
