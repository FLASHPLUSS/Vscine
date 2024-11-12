import requests
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/buscar_filme", methods=["GET"])
def buscar_filme():
    # Pega o título do filme a partir da query string
    titulo = request.args.get('titulo', '')

    if not titulo:
        return jsonify({"erro": "Título do filme não fornecido!"}), 400

    # URL da pesquisa do filme
    url = f"https://assistir.biz/busca?q={titulo}"

    # Definindo o cabeçalho do User-Agent para evitar bloqueios
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Fazendo o request para o site
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Usando BeautifulSoup para fazer o parse do HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Localizando o iframe com o link de reprodução (ajuste conforme necessário)
        iframe = soup.find("iframe")
        if iframe:
            link_reproducao = iframe['src']
            return jsonify({"link": f"http:{link_reproducao}"})

        return jsonify({"erro": "Link de reprodução não encontrado!"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run()
