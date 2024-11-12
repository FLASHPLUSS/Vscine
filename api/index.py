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

            # Buscando o reprodutor de vídeo e as tags <source> que contêm as resoluções
            sources = soup_filme.find_all("source")
            sd_link = None
            hd_link = None

            for source in sources:
                src = source.get('src')
                if src:
                    # Exibindo cada link extraído para depuração
                    # print(f"Link encontrado: {src}")  # Removido para produção

                    # Se a resolução for 360 (sd), armazenar o link
                    if 'sd' in src:
                        sd_link = 'http:' + src if not src.startswith('http') else src
                    # Se a resolução for 720 (hd), armazenar o link
                    elif 'hd' in src:
                        hd_link = 'http:' + src if not src.startswith('http') else src

            # Verificar se os links encontrados são válidos
            if sd_link and verificar_link(sd_link):
                sd_link_status = sd_link
            else:
                sd_link_status = None

            if hd_link and verificar_link(hd_link):
                hd_link_status = hd_link
            else:
                hd_link_status = None

            # Verificar qual link (sd ou hd) foi encontrado e retornar
            if sd_link_status and hd_link_status:
                return jsonify({"sd_link": sd_link_status, "hd_link": hd_link_status}), 200
            elif sd_link_status:
                return jsonify({"sd_link": sd_link_status}), 200
            elif hd_link_status:
                return jsonify({"hd_link": hd_link_status}), 200
            else:
                return jsonify({"erro": "Links de resolução não encontrados ou não funcionais!"}), 404

        # Caso o filme não seja encontrado na busca
        return jsonify({"erro": "Filme não encontrado!"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
