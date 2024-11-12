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

@app.route("/api/pesquisa", methods=["GET"])
def pesquisa():
    # Obtém o título do filme a partir do parâmetro na URL
    titulo = request.args.get('titulo', '')

    if not titulo:
        return jsonify({"erro": "Título do filme não fornecido!"}), 400

    # URL de pesquisa no site
    url_busca = f"https://assistir.biz/busca?q={titulo}"

    # Cabeçalhos para evitar bloqueios (definindo o User-Agent)
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

            # Buscando o link de reprodução nos iframes
            iframe = soup_filme.find("iframe", class_="iframe-fix")
            if iframe:
                link_player = iframe.get('src')
                if link_player:
                    # Verificando se o link do player precisa do prefixo http:
                    if not link_player.startswith('http://') and not link_player.startswith('https://'):
                        link_player = 'http:' + link_player
                    
                    # Verificando se o link do player está funcionando
                    if verificar_link(link_player):
                        return jsonify({"link_player": link_player}), 200
                    else:
                        return jsonify({"erro": "Link do player não está funcionando!"}), 404
                else:
                    return jsonify({"erro": "Link do player não encontrado!"}), 404
            else:
                return jsonify({"erro": "Iframe com link do player não encontrado!"}), 404

        # Caso o filme não seja encontrado na busca
        return jsonify({"erro": "Filme não encontrado!"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
