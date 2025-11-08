import requests
from bs4 import BeautifulSoup

URL = "https://programathor.com.br/jobs"


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def buscar_vagas():

    print("Iniciando scraper... Buscando vagas no Programathor.")
    
    try:
        pagina = requests.get(URL, headers=HEADERS)
        
        pagina.raise_for_status()

        soup = BeautifulSoup(pagina.content, "html.parser")

        
        lista_vagas_html = soup.find_all("div", class_="cell-list")
        
        if not lista_vagas_html:
            print("Não foram encontrados 'cards' de vagas. O HTML do site pode ter mudado.")
            return []

        print(f"Encontrados {len(lista_vagas_html)} 'cards' de vagas.")

        vagas_coletadas = []

        
        for vaga_html in lista_vagas_html:
           
            titulo_h3 = vaga_html.find("h3")
            empresa_span = vaga_html.find("span", class_="company")
            link_a = vaga_html.find("a", href=True) 
            
            
            tags_div = vaga_html.find("div", class_="cell-list-tags")
            tags = []
            if tags_div:
                tags_spans = tags_div.find_all("span")
                tags = [tag.text.strip().lower() for tag in tags_spans] 

            
            if titulo_h3 and empresa_span and link_a:
                titulo = titulo_h3.text.strip()
                empresa = empresa_span.text.strip()
                link = link_a['href']
                
                if not link.startswith("http"):
                    link = "https://programathor.com.br" + link
                
                vaga_obj = {
                    "titulo": titulo,
                    "empresa": empresa,
                    "link": link,
                    "tags": tags,
                    "origem": "Programathor"
                }
                vagas_coletadas.append(vaga_obj)
        
        return vagas_coletadas

    except requests.exceptions.HTTPError as errh:
        print(f"Erro de HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Erro de Conexão: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Erro de Timeout: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Erro inesperado: {err}")
    
    return [] 

if __name__ == "__main__":
    vagas = buscar_vagas()
    if vagas:
        print(f"\n--- {len(vagas)} Vagas Coletadas ---")
        print(vagas[0])
        for i, vaga in enumerate(vagas):
            print(f"{i+1}. {vaga['titulo']} - Tags: {vaga['tags']}")