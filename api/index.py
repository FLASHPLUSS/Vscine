import requests
from bs4 import BeautifulSoup

# Função para buscar o link de reprodução do filme
def buscar_links_reproducao(titulo_filme):
    # URL base para a busca
    url_base = f"https://assistir.biz/busca?q={titulo_filme}"
    
    # Cabeçalhos com o User-Agent para simular uma requisição de navegador
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Fazendo a requisição para a página
    response = requests.get(url_base, headers=headers)
    
    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurando os botões de player
        buttons = soup.find_all('button', class_='section__view')
        
        if buttons:
            links = []
            # Iterando sobre todos os botões de player encontrados
            for button in buttons:
                # Aqui vamos procurar o iframe que contém o link do player
                iframe = button.find_next('iframe')
                
                if iframe and iframe.get('src'):
                    player_url = iframe['src']
                    
                    # Se a URL começar com //, adiciona o http:
                    if player_url.startswith('//'):
                        player_url = f"http:{player_url}"
                    
                    links.append(player_url)
            return links
        else:
            return {"erro": "Nenhum player encontrado na página!"}
    else:
        return {"erro": "Erro ao acessar a página!"}

# Testando a função com um título de filme
titulo = "coringa"
links = buscar_links_reproducao(titulo)

if 'erro' in links:
    print(links['erro'])
else:
    print("Links encontrados:")
    for link in links:
        print(link)
