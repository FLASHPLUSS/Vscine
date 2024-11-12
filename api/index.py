import requests
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup

app = Flask(__name__)

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
            return jsonify({"link": filme_url}), 200

        # Caso o filme não seja encontrado na busca
        return jsonify({"erro": "Filme não encontrado!"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
