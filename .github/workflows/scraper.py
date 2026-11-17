import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://minkang.x.yupoo.com"
CATEGORIES_URL = f"{BASE_URL}/categories"
MAX_PAGES_DEFAULT = 200

@dataclass
class Producto:
    title: str
    category: str
    img: str
    album_url: str = ""
    sizes: Optional[str] = None

class YupooScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=chrome_options)

    @staticmethod
    def _clasificar(title: str) -> str:
        t = title.upper()
        if re.search(r"\bNK\b", t) or "NIKE" in t: return "Nike"
        if re.search(r"\bJB\b", t) or "JORDAN" in t: return "Jordan"
        if "SHORT" in t: return "Shorts"
        if "HOODIE" in t or "SUDADERA" in t or "SWEAT" in t: return "Sudaderas"
        if "PANT" in t or "JOGGER" in t: return "Pantalones"
        if "JERSEY" in t or "CAMISETA" in t or "SHIRT" in t: return "Camisetas"
        if "SOCK" in t or "CAP" in t or "BAG" in t or "ACCESSOR" in t: return "Accesorios"
        return "Catálogo General"

    def scrape_page(self, url: str) -> list[Producto]:
        print(f"[*] Navegando a: {url}")
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.album__main, a[href*='albums']"))
            )
            time.sleep(2)
        except Exception:
            print("[*] No se han encontrado productos en esta página.")
            return []

        productos = []
        cards = self.driver.find_elements(By.CSS_SELECTOR, "div.album__main, a[href*='albums']")
        
        for card in cards:
            try:
                link = card if card.tag_name == 'a' else card.find_element(By.CSS_SELECTOR, "a[href]")
                album_url = link.get_attribute("href")
                
                # Obtener título
                try:
                    img_el = link.find_element(By.CSS_SELECTOR, "img[alt]")
                    title = img_el.get_attribute("alt")
                except:
                    try:
                        title = link.find_element(By.CSS_SELECTOR, ".album__title").text
                    except:
                        continue
                
                # Si el título está vacío o es basura, lo saltamos
                if not title or len(title) < 3 or "yupoo" in title.lower() or "加密相册" in title:
                    continue

                # Obtener imagen
                try:
                    img_el = card.find_element(By.CSS_SELECTOR, "img")
                    img = img_el.get_attribute("data-src") or img_el.get_attribute("data-original") or img_el.get_attribute("src") or ""
                    if img:
                        img = urljoin(BASE_URL, img)
                except:
                    img = ""

                productos.append(Producto(
                    title=title.strip(),
                    category=self._clasificar(title),
                    img=img,
                    album_url=album_url
                ))
            except Exception:
                continue
                
        return productos

    def scrape_all(self, max_pages: int):
        todos = []
        for page in range(1, max_pages + 1):
            url = f"{CATEGORIES_URL}?page={page}" if page > 1 else CATEGORIES_URL
            prods = self.scrape_page(url)
            print(f"    -> {len(prods)} productos encontrados.")
            
            if len(prods) == 0:
                print("[*] Fin del catálogo.")
                break
                
            todos.extend(prods)
            time.sleep(1)

        self.driver.quit()

        vistos = set()
        unicos = []
        for p in todos:
            key = (p.title, p.album_url)
            if key in vistos: continue
            vistos.add(key)
            unicos.append(p)

        return unicos

def guardar_json(productos: list[Producto], path: str):
    data = [{"title": p.title, "category": p.category, "img": p.img} for p in productos if p.title and p.img]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] ¡Éxito! Escritos {len(data)} productos en {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT)
    ap.add_argument("--out", default="productos.json")
    args = ap.parse_args()

    print("[*] Iniciando navegador fantasma...")
    scraper = YupooScraper()
    productos = scraper.scrape_all(args.max_pages)

    if not productos:
        print("[!] No se encontraron productos.")
        sys.exit(1)

    guardar_json(productos, args.out)

if __name__ == "__main__":
    main()