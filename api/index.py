import requests
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup

app = Flask(__name__)

def verificar_link(link):
    """
    Função auxiliar para verificar se o link do player está funcionando.
    Retorna True se o link estiver funcionando (status 200), False caso contrário.
    """
    try:
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        return response.status_code == 200
    except requests.RequestException:
        return False

def obter_links_verdadeiros(link_player):
    """
    Função para fazer uma requisição ao link do player e obter os links de vídeo em resoluções 360p e 720p.
    """
    response = requests.get(link_player)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        sources = soup.find_all('source')

        video_links = {"360p": None, "720p": None}
        
        for source in sources:
            video_link = source.get('src')
            resolution = source.get('size')  # Obtém o atributo size para identificar a resolução
            
            if video_link and resolution:
                if video_link.startswith('//'):
                    video_link = 'https:' + video_link
                
                if resolution == "360":
                    video_links["360p"] = video_link
                elif resolution == "720":
                    video_links["720p"] = video_link

        return video_links
    else:
        return None

@app.route("/api/pesquisa", methods=["GET"])
def pesquisa():
    # Obtém o título do filme a partir do parâmetro na URL
    titulo = request.args.get('titulo', '')

    if not titulo:
        return jsonify({"erro": "Título do filme não fornecido!"}), 400

    # URL de pesquisa no site
    url_busca = f"https://assistir.biz/busca?q={titulo}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Fazendo a requisição para o site de busca
        response = requests.get(url_busca, headers=headers)
        response.raise_for_status()

        # Usando BeautifulSoup para fazer o parsing do HTML da página de busca
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrando o link da página do filme, que está no href do <a> com a classe "card__play"
        link_pagina_filme = soup.find("a", class_="card__play")
        if link_pagina_filme:
            filme_url = "https://assistir.biz" + link_pagina_filme['href']

            # Agora vamos fazer uma requisição para pegar a página do filme e extrair o link do iframe
            response_filme = requests.get(filme_url, headers=headers)
            response_filme.raise_for_status()

            # Usando BeautifulSoup para fazer o parsing do HTML da página do filme
            soup_filme = BeautifulSoup(response_filme.text, 'html.parser')

            # Buscando todos os iframes na página do filme
            iframes = soup_filme.find_all("iframe", class_="iframe-fix")

            # Procurando especificamente o iframe com 'player=2'
            for iframe in iframes:
                src = iframe.get('src')
                if src and 'player=2' in src:
                    # Se encontrado o player=2, verificar se o link está funcionando
                    if not src.startswith('http://') and not src.startswith('https://'):
                        src = 'http:' + src
                    
                    if verificar_link(src):
                        # Obter links de 360p e 720p
                        video_links = obter_links_verdadeiros(src)
                        
                        if video_links:
                            return jsonify({
                                "link_player": src,
                                "resolucao_360p": video_links["360p"],
                                "resolucao_720p": video_links["720p"]
                            }), 200
                        else:
                            return jsonify({"erro": "Links de vídeo não encontrados!"}), 404

            # Se não encontrar o iframe correto com player=2, exibir erro
            return jsonify({"erro": "Link do player 2 não encontrado!"}), 404

        # Caso o filme não seja encontrado na busca
        return jsonify({"erro": "Filme não encontrado!"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
