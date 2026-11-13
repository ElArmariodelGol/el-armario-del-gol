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
    max_paginas = 120  # Límite ampliado a 120 páginas

    print(f"Iniciando extracción automática de Yupoo (hasta {max_paginas} páginas)...")

    while page <= max_paginas:
        url_actual = f"{BASE_URL}?page={page}"
        print(f"Leyendo página {page} de {max_paginas}...")
        
        try:
            response = requests.get(url_actual, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"La página {page} no devolvió código 200 (Código: {response.status_code}). Fin del catálogo.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar todos los contenedores de álbumes en la página actual
            albums = soup.find_all('div', class_='album__main') or soup.find_all('a', class_='album__item')
            if not albums:
                albums = soup.select('a.album')
            
            # Si una página no devuelve ningún álbum, hemos llegado al final real del catálogo
            if not albums:
                print(f"No hay más álbumes en la página {page}. ¡Catálogo completamente descargado!")
                break

            productos_en_pagina = 0
            for album in albums:
                # Extraer título del álbum de forma segura
                title_elem = album.find('div', class_='album__title') or album.find('span', class_='album__title') or album.find('img')
                title = "Camiseta de Fútbol"
                if title_elem:
                    if title_elem.has_attr('alt') and title_elem['alt'].strip():
                        title = title_elem['alt'].strip()
                    elif title_elem.text.strip():
                        title = title_elem.text.strip()

                # Extraer la imagen de portada
                img_elem = album.find('img')
                img_url = ""
                if img_elem:
                    img_url = img_elem.get('data-src') or img_elem.get('src') or img_elem.get('data-original')
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = "https:" + img_url
                        elif img_url.startswith('/'):
                            img_url = "https://minkang.x.yupoo.com" + img_url

                if img_url:
                    # Categorización automática inteligente por palabras clave en el título
                    category = "Otros"
                    t_lower = title.lower()
                    if any(k in t_lower for k in ['madrid', 'barcelona', 'atlético', 'valencia', 'sevilla', 'betis', 'laliga', 'real madrid', 'fc barcelona']):
                        category = "LaLiga"
                    elif any(k in t_lower for k in ['premier', 'arsenal', 'chelsea', 'city', 'united', 'liverpool', 'tottenham', 'manchester']):
                        category = "Premier League"
                    elif any(k in t_lower for k in ['retro', 'vintage', 'classic', '90', '80', 'historic', 'remake']):
                        category = "Retro"
                    elif any(k in t_lower for k in ['españa', 'argentina', 'brasil', 'francia', 'selección', 'world cup', 'italy', 'germany', 'portugal', 'mexico']):
                        category = "Selecciones"

                    # Evitar duplicados exactos en la lista
                    if not any(p['img'] == img_url for p in productos):
                        productos.append({
                            "title": title,
                            "img": img_url,
                            "category": category
                        })
                        productos_en_pagina += 1

            print(f"-> Añadidas {productos_en_pagina} camisetas de la página {page}.")
            
            # Pausa de cortesía para no saturar el servidor
            time.sleep(0.4)
            page += 1

        except Exception as e:
            print(f"Error procesando la página {page}: {e}")
            break

    print(f"¡Proceso finalizado con éxito! Total de camisetas recopiladas: {len(productos)}")
    return productos

if __name__ == "__main__":
    datos = extraer_todo_yupoo()
    if datos:
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print("Archivo productos.json actualizado con éxito.")
    else:
        print("No se pudieron extraer productos.")
