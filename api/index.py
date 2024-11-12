from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# User-Agent para emular o Chrome
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def extrair_link_video(url):
    response = requests.get(url, headers=HEADERS)  # Incluindo o cabeçalho com o User-Agent
    
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a URL: {response.status_code}")

    doc = BeautifulSoup(response.text, 'html.parser')

    # Encontrar o link de reprodução
    assist_buttons = doc.find_all('a', class_='btn free fw-bold')
    for button in assist_buttons:
        if 'ASSISTIR' in button.text:
            video_link = button['href']
            return video_link.replace("http://", "").replace("https://", "")
    
    return "Link não encontrado."

def extrair_urls_filmes(search_query):
    url = f"https://www.visioncine-1.com.br/search.php?q={search_query}"
    response = requests.get(url, headers=HEADERS)  # Incluindo o cabeçalho com o User-Agent

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
        # Obter URLs de filmes da pesquisa
        urls = extrair_urls_filmes(search_query)
        if not urls:
            return jsonify({"message": "Nenhum filme encontrado."}), 404
        
        # Extrair os links de vídeo de cada URL de filme
        resultados = []
        for url in urls:
            video_link = extrair_link_video(url)
            if video_link != "Link não encontrado.":
                resultados.append({"url": url, "link_video": video_link})

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
