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
    url = f"https://assistir.biz/busca?q={titulo}"

    # Cabeçalhos para evitar bloqueios (definindo o User-Agent)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Fazendo a requisição para o site
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Usando BeautifulSoup para fazer o parsing do HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tentando encontrar o primeiro iframe com o link de reprodução
        iframe = soup.find("iframe")
        if iframe:
            link_reproducao = iframe['src']
            # Verificando se o link não possui o prefixo http:// ou https://
            if not link_reproducao.startswith('http://') and not link_reproducao.startswith('https://'):
                link_reproducao = 'http:' + link_reproducao
            return jsonify({"link": link_reproducao}), 200

        # Caso o link de reprodução não seja encontrado
        return jsonify({"erro": "Link de reprodução não encontrado!"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run()
