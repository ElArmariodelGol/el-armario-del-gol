import json
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    print("[*] Iniciando motor de Playwright con sigilo (Stealth)...")
    
    with sync_playwright() as p:
        # Lanzamos Chromium con flags que ocultan la automatización
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        
        # Creamos un contexto con un User-Agent real y viewport
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="es-ES"
        )
        
        page = context.new_page()
        
        # 1. CALENTAMIENTO: Entramos a la home para coger cookies y "confianza"
        print("[*] Calentando sesión (visitando home)...")
        page.goto("https://minkang.x.yupoo.com/", timeout=60000, wait_until="domcontentloaded")
        time.sleep(2)
        
        # 2. INYECTAR REFERER: Ahora vamos a la página de categorías
        print("[*] Accediendo a categorías...")
        page.goto(
            "https://minkang.x.yupoo.com/categories",
            timeout=60000,
            wait_until="domcontentloaded",
            referer="https://minkang.x.yupoo.com/"
        )
        time.sleep(3)
        
        # 3. EXTRAER EL MENÚ LATERAL DIRECTAMENTE DEL DOM
        print("[*] Extrayendo menú lateral...")
        
        # Yupoo renderiza el menú con JS, así que esperamos a que aparezca
        try:
            page.wait_for_selector(".show-layout-category__catewrap", timeout=15000)
        except:
            print("[!] No se encontró el selector del menú. Intentando con otro...")
        
        # Extraemos todos los enlaces del menú
        menu_final = []
        
        # Selector principal (según estructura de Yupoo)
        enlaces = page.query_selector_all(".show-layout-category__catewrap a")
        
        if not enlaces:
            # Selector alternativo por si acaso
            enlaces = page.query_selector_all(".category__item a")
        
        for a in enlaces:
            nombre = a.inner_text().strip()
            href = a.get_attribute("href") or ""
            
            if not nombre or nombre in ["All categories", "Menu", "Menu 2", ""]:
                continue
            
            # Construimos la URL completa
            if href.startswith("/"):
                url = f"https://minkang.x.yupoo.com{href}"
            elif href.startswith("http"):
                url = href
            else:
                continue
            
            menu_final.append({
                "name": nombre,
                "url": url,
                "img": "imagenes/logo.jpg"  # Placeholder
            })
        
        # 4. EXTRAER PRODUCTOS DE LA PÁGINA (opcional, para tener algo en el grid)
        print("[*] Extrayendo productos de la vista principal...")
        productos = []
        albumes = page.query_selector_all(".album__main")
        
        for alb in albumes:
            title_el = alb.query_selector(".album__title")
            img_el = alb.query_selector("img")
            
            if title_el and img_el:
                img_url = img_el.get_attribute("data-src") or img_el.get_attribute("src") or ""
                if img_url and not img_url.startswith("http"):
                    img_url = f"https:{img_url}" if img_url.startswith("//") else f"https://minkang.x.yupoo.com{img_url}"
                
                productos.append({
                    "title": title_el.inner_text().strip(),
                    "img": img_url,
                    "category": "All categories"
                })
        
        # 5. GUARDAR
        with open("productos.json", "w", encoding="utf-8") as f:
            json.dump({"menu": menu_final, "productos": productos}, f, ensure_ascii=False, indent=2)
        
        print(f"[+] ¡ÉXITO! {len(menu_final)} categorías y {len(productos)} productos guardados.")
        
        browser.close()

if __name__ == "__main__":
    main()
