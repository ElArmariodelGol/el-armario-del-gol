#!/usr/bin/env python3
"""
scraper.py — Scraper para el catálogo Yupoo de KANG Team
URL: https://minkang.x.yupoo.com/categories
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://minkang.x.yupoo.com"
CATEGORIES_URL = f"{BASE_URL}/categories"
MAX_PAGES_DEFAULT = 200

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": BASE_URL,
}


@dataclass
class Producto:
    title: str
    category: str
    img: str
    album_url: str = ""
    rating: Optional[str] = None
    sizes: Optional[str] = None


class YupooScraper:
    def __init__(self, delay: float = 0.5):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = delay

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        try:
            r = self.session.get(url, timeout=30)
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")
        except requests.RequestException as e:
            print(f"[!] Fallo al pedir {url}: {e}", file=sys.stderr)
            return None

    def iter_listing_pages(self, start_url: str, max_pages: int):
        url = start_url
        page = 1
        while url and page <= max_pages:
            print(f"[*] Página {page}/{max_pages}: {url}")
            soup = self.fetch(url)
            if not soup:
                break
            yield soup
            nxt = self._find_next_link(soup)
            if not nxt:
                print(f"[*] No hay más páginas después de la {page}.")
                break
            url = urljoin(BASE_URL, nxt)
            page += 1
            time.sleep(self.delay)

    @staticmethod
    def _find_next_link(soup: BeautifulSoup) -> Optional[str]:
        # Buscar botones de "Siguiente" o números de paginación
        for a in soup.select("a[rel='next'], a.next, .pagination a, .pagination__number"):
            txt = (a.get_text(strip=True) or "").lower()
            if a.get("rel") == ["next"] or txt in {"next", "›", "»", "next page"}:
                href = a.get("href")
                if href and not href.startswith("#"):
                    return href
        return None

    @staticmethod
    def _clasificar(title: str) -> str:
        t = title.upper()
        if re.search(r"\bNK\b", t) or "NIKE" in t:
            return "Nike"
        if re.search(r"\bJB\b", t) or "JORDAN" in t:
            return "Jordan"
        if "SHORT" in t:
            return "Shorts"
        if "HOODIE" in t or "SUDADERA" in t or "SWEAT" in t:
            return "Sudaderas"
        if "PANT" in t or "JOGGER" in t:
            return "Pantalones"
        if "JERSEY" in t or "CAMISETA" in t or "SHIRT" in t:
            return "Camisetas"
        if "SOCK" in t or "CAP" in t or "BAG" in t or "ACCESSOR" in t:
            return "Accesorios"
        return "Shorts"

    @staticmethod
    def _extraer_tallas(title: str, desc: Optional[str] = None) -> Optional[str]:
        txt = f"{title} {desc or ''}"
        m = re.search(
            r"\b(XS|S|M|L|XL|2XL|3XL|4XL|5XL)\s*[-–]\s*(XS|S|M|L|XL|2XL|3XL|4XL|5XL)\b",
            txt, re.IGNORECASE,
        )
        if m:
            return f"{m.group(1).upper()}-{m.group(2).upper()}"
        return None

    def parse_products(self, soup: BeautifulSoup) -> list[Producto]:
        productos: list[Producto] = []
        
        # Selectores más amplios para atrapar la estructura de Yupoo
        cards = soup.select("div.album__main") or soup.select("a[href*='albums']")

        for card in cards:
            # Si el elemento es el enlace directamente (a), lo usamos
            link = card if card.name == 'a' else card.select_one("a[href]")
            if not link:
                continue
                
            album_url = urljoin(BASE_URL, link["href"])

            # Intentar sacar el título
            title_el = link.select_one("img[alt]") or card.select_one(".album__title")
            title = ""
            if title_el:
                title = title_el.get("alt") or title_el.get("title") or title_el.get_text(strip=True)
            
            if not title or len(title) < 3 or "yupoo" in title.lower():
                continue

            # Intentar sacar la imagen
            img_el = card.select_one("img")
            img = ""
            if img_el:
                img = (
                    img_el.get("data-src")
                    or img_el.get("data-original")
                    or img_el.get("src")
                    or ""
                )
                if img:
                    img = urljoin(BASE_URL, img)

            productos.append(Producto(
                title=title.strip(),
                category=self._clasificar(title),
                img=img,
                album_url=album_url,
                sizes=self._extraer_tallas(title),
            ))

        return productos

    def completar_detalle(self, prod: Producto) -> Optional[Producto]:
        if not prod.album_url:
            return prod
        soup = self.fetch(prod.album_url)
        if not soup:
            return prod

        if "请输入访问密码" in str(soup) or "access password" in str(soup).lower():
            print(f"    [~] Saltando álbum protegido: {prod.title[:50]}")
            return None

        # Sacar la mejor imagen si no la tenemos
        if not prod.img:
            for img in soup.select(".showalbum__children img, .album__children img, img.autocover"):
                src = img.get("data-src") or img.get("data-original") or img.get("src")
                if src:
                    prod.img = urljoin(BASE_URL, src)
                    break
        time.sleep(self.delay)
        return prod

    def scrape(self, with_details: bool = False, max_pages: int = MAX_PAGES_DEFAULT) -> list[Producto]:
        todos: list[Producto] = []
        
        # Vamos a iterar las páginas añadiendo ?page=X por si el botón "Siguiente" falla
        url = CATEGORIES_URL
        for page in range(1, max_pages + 1):
            current_url = f"{CATEGORIES_URL}?page={page}" if page > 1 else url
            print(f"[*] Página {page}/{max_pages}: {current_url}")
            
            soup = self.fetch(current_url)
            if not soup:
                break
                
            prods = self.parse_products(soup)
            print(f"    -> {len(prods)} productos en página {page}")
            
            # Si no encontramos productos, es que hemos llegado al final
            if len(prods) == 0:
                print("[*] Fin del catálogo alcanzado.")
                break
                
            todos.extend(prods)
            time.sleep(self.delay)

        # Deduplicar
        vistos = set()
        unicos = []
        for p in todos:
            key = (p.title, p.album_url)
            if key in vistos:
                continue
            vistos.add(key)
            unicos.append(p)

        print(f"[*] Total único (listado): {len(unicos)} productos")

        if with_details and unicos:
            print(f"[*] Completando detalle; los protegidos se omiten...")
            finales: list[Producto] = []
            for idx, p in enumerate(unicos, 1):
                print(f"    [{idx}/{len(unicos)}] {p.title[:60]}")
                resultado = self.completar_detalle(p)
                if resultado is not None:
                    finales.append(resultado)
            return finales

        return unicos


def guardar_json(productos: list[Producto], path: str):
    data = [
        {"title": p.title, "category": p.category, "img": p.img}
        for p in productos
        if p.title and p.img
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Escritos {len(data)} productos en {path}")


def main():
    ap = argparse.ArgumentParser(description="Scraper Yupoo → productos.json")
    ap.add_argument("--details", action="store_true", help="Visita cada álbum para coger la imagen real")
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--out", default="productos.json")
    args = ap.parse_args()

    scraper = YupooScraper(delay=args.delay)
    productos = scraper.scrape(with_details=args.details, max_pages=args.max_pages)

    if not productos:
        print("[!] No se encontraron productos visibles.", file=sys.stderr)
        sys.exit(1)

    guardar_json(productos, args.out)


if __name__ == "__main__":
    main()
