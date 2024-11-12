from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Cabeçalhos atualizados para emular melhor um navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def extrair_urls_filmes(search_query):
    url = f"https://www.visioncine-1.com.br/search.php?q={search_query}"
    
    # Usando uma sessão para manter os cookies
    session = requests.Session()
    session.headers.update(HEADERS)

    response = session.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        movie_links = soup.select("a.btn.free.fw-bold")

        urls = []
        if movie_links:
            for link in movie_links:
                movie_url = link['href']
                if "watch" in movie_url:  # Verifica se o link é válido
                    urls.append(movie_url)
            return urls
        else:
            return []
    else:
        raise Exception(f"Erro ao acessar a página de pesquisa: {response.status_code}")

@app.route('/api/pesquisa', methods=['GET'])
def pesquisa():
    search_query = request.args.get('query')
    if not search_query:
        return jsonify({"error": "Consulta de pesquisa não fornecida."}), 400
    
    try:
        urls = extrair_urls_filmes(search_query)
        if not urls:
            return jsonify({"message": "Nenhum filme encontrado."}), 404
        
        resultados = []
        for url in urls:
            resultados.append({"url": url})

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
