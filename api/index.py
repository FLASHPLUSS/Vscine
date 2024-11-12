from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extrair_dados_filme(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a URL: {response.status_code}")

    doc = BeautifulSoup(response.text, 'html.parser')

    # Extrair os dados necessários com verificação
    title_elem = doc.select_one("h1.fw-bolder.mb-0")
    title = title_elem.get_text(strip=True) if title_elem else "Título não encontrado"

    synopsis_elem = doc.select_one("p.small.linefive")
    synopsis = synopsis_elem.get_text(strip=True) if synopsis_elem else "Sinopse nao encontrada"

    duration_elem = doc.find("span", string=lambda x: x and "Min" in x)
    duration = duration_elem.get_text(strip=True) if duration_elem else "Duracao nao encontrada"

    year_elem = doc.find("span", string=lambda x: x and x.isdigit())
    year = year_elem.get_text(strip=True) if year_elem else "Ano nao encontrado"

    classification_elem = doc.select_one("em.classification")
    classification = classification_elem.get_text(strip=True) if classification_elem else "Classificação não encontrada"

    genre_elems = doc.select("p.lineone span")
    genre = ', '.join([span.get_text(strip=True) for span in genre_elems]) if genre_elems else "Genero nao encontrado"

    background_image_style = doc.select_one("div.backImage")
    background_image_url = background_image_style['style'].split("url('")[1].split("')")[0] if background_image_style else "Capa de fundo nao encontrada"

    poster_image_style = doc.select_one("div.poster")
    poster_image_url = poster_image_style['style'].split("url('")[1].split("')")[0] if poster_image_style else "Capa do video nao encontrada"

    video_link = None
    assist_buttons = doc.find_all('a', class_='btn free fw-bold')
    
    for button in assist_buttons:
        if 'ASSISTIR' in button.text:
            video_link = button['href']
            break

    if video_link:
        video_link = video_link.replace("http://", "").replace("https://", "")

    return {
        "Titulo": title,
        "Sinopse": synopsis,
        "Duracao": duration,
        "Ano": year,
        "Classificacao": classification,
        "Genero": genre,
        "Capa de Fundo": background_image_url,
        "Capa do Video": poster_image_url,
        "Link do Video": video_link if video_link else "Link não encontrado."
    }

def extrair_urls_filmes(search_query):
    url = f"https://www.visioncine-1.com.br/search.php?q={search_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.get(url, headers=headers)

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

@app.route('/api/filme', methods=['GET'])
def filme():
    filme_url = request.args.get('url')
    if not filme_url:
        return jsonify({"error": "URL do filme não fornecida."}), 400
    
    try:
        dados_filme = extrair_dados_filme(filme_url)
        return jsonify(dados_filme)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            dados_filme = extrair_dados_filme(url)
            # Verifica se o link do vídeo é válido antes de adicionar aos resultados
            if dados_filme["Link do Video"] != "Link não encontrado." and not dados_filme["Link do Video"].startswith("#"):
                resultados.append(dados_filme)

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
