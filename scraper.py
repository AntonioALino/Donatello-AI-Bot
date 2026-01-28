import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from unidecode import unidecode 

HEADERS = {
    'User-Agent': 'Mozilla.5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def buscar_vagas(url: str, tag_extra: str = None):
    
    print(f"Iniciando scraper (Produção)... Buscando vagas em: {url}")
    
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            ) 
            context = await browser.new_context(user_agent=HEADERS['User-Agent'])
            page = await context.new_page()
            
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            try:
                await page.wait_for_selector("h3", timeout=10000)
            except Exception as e:
                print(f"Alerta: O seletor 'h3' não apareceu em 10s. (Página {url} pode estar vazia)")
            
            html_content = await page.content()
            await browser.close()

            soup = BeautifulSoup(html_content, "html.parser")
            titulos_h3 = soup.find_all("h3")
            
            if not titulos_h3:
                print(f"Não foram encontrados 'cards' (H3) em {url}.")
                return []

            vagas_coletadas = []
            
            for titulo_h3 in titulos_h3:
                
                if len(titulo_h3.text.strip()) < 3 or not titulo_h3.text.strip():
                    continue

                content_div = titulo_h3.parent
                if not content_div or "cell-list-content" not in content_div.get('class', []):
                    continue 

                titulo = unidecode(titulo_h3.text.strip()).replace("NOVA", "").strip()

                link_a = titulo_h3.find_parent("a", href=True)
                if not link_a:
                    continue 
                link = "https://programathor.com.br" + link_a['href']

                empresa_span = content_div.find("i", class_="fa-briefcase")
                empresa = unidecode(empresa_span.parent.text.strip()) if empresa_span else "Não informado"

                
                tags_nivel = content_div.find("i", class_="fa-chart-bar")
                if tags_nivel:
                    tags_nivel = unidecode(tags_nivel.parent.text.strip().lower())
                
                tags_skills = content_div.find_all("span", class_="tag-list")
                tags = [unidecode(tag.text.strip().lower()) for tag in tags_skills]
                
                if tags_nivel and tags_nivel not in tags:
                    tags.append(tags_nivel)
                
                if tag_extra:
                    tag_extra_limpa = unidecode(tag_extra.lower())
                    if tag_extra_limpa not in tags:
                        tags.append(tag_extra_limpa)

                vaga_obj = {
                    "titulo": titulo,
                    "empresa": empresa,
                    "link": link,
                    "tags": list(set(tags)), 
                    "origem": "Programathor"
                }
                vagas_coletadas.append(vaga_obj)
            
            return vagas_coletadas

        except Exception as err:
            print(f"Erro inesperado no scraper (Produção): {err}")
            if browser: await browser.close()
            return []