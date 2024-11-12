from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Função para buscar o link de reprodução
def buscar_links_reproducao(titulo_filme):
    # Formatação da URL de busca
    url = f"https://assistir.biz/busca?q={titulo_filme}"
    
    # Fazendo o request para buscar a página
    response = requests.get(url)
    
    # Verificando se a resposta foi bem-sucedida
    if response.status_code == 200:
        # Parseando o conteúdo HTML com BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Log para verificar o conteúdo da página
        print("Conteúdo da página:", soup.prettify())
        
        # Procurando todos os iframes na página
        iframes = soup.find_all('iframe')
        
        if iframes:
            links = []
            # Iterando sobre todos os iframes encontrados
            for iframe in iframes:
                player_url = iframe.get('src', '')
                if player_url:
                    # Se a URL começar com //, adiciona o http:
                    if player_url.startswith('//'):
                        player_url = f"http:{player_url}"
                    links.append(player_url)
            if links:
                return links
            else:
                print("Nenhum link de player encontrado nos iframes.")
        else:
            print("Nenhum iframe encontrado na página.")
    else:
        print(f"Erro ao acessar o site: {response.status_code}")
    
    return None

# Rota da API
@app.route('/api/reproduzir', methods=['GET'])
def reproduzir():
    # Obtendo o título do filme a partir dos parâmetros de query
    titulo_filme = request.args.get('titulo')
    
    if not titulo_filme:
        return jsonify({"erro": "O título do filme é obrigatório!"}), 400
    
    # Buscando os links de reprodução
    links = buscar_links_reproducao(titulo_filme)
    
    if links:
        return jsonify({"links": links})
    else:
        return jsonify({"erro": "Links de reprodução não encontrados!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
