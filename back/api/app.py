from flask import Flask, request, jsonify
from flask_cors import CORS # Importa o CORS
from openai import OpenAI
from dotenv import load_dotenv
import json, random, os

load_dotenv()

# Configuração da chave da API do OpenAI
client = OpenAI(
  api_key=os.getenv("API_KEY")
)

app = Flask(__name__)
CORS(app)  # Habilita o CORS para todas as rotas

# Regras de batalha entre objetos e seus emojis
# alguma hora eu ainda posso usar isso
# battle_rules = {
#     "Pedra": {"derrota": "Tesoura", "derrotado_por": "Papel", "emoji": "🗿"},
#     "Papel": {"derrota": "Pedra", "derrotado_por": "Tesoura", "emoji": "📄"},
#     "Tesoura": {"derrota": "Papel", "derrotado_por": "Pedra", "emoji": "✂️"}
# }

# função para obter um objeto aleatório, usada so quando perdemos
def get_random_objeto():
    objetos = [
        {"nome": "Pedra", "emoji": "🗿"},
        {"nome": "Água", "emoji": "💧"},
        {"nome": "Fogo", "emoji": "🔥"},
    ]
    return random.choice(objetos)

# Função para obter o resultado da batalha
# usei o chatgpt porque torna o jogo infinito, e eu não conheço uma ia mais rapida
def get_battle_result(obj1, obj2):

    lista_obj = [obj1, obj2]
    
    # Mensagem do sistema e prompt para o ChatGPT
    system = """Você é o juiz de um jogo onde existem dois objetos e você deve decidir, de acordo a lógica, qual deles ganha.
    Por favor, forneça as respostas como um json com duas chaves e seus valores, mas sem formatação do chat; lembre-se de relevar erros gramaticais corrigi-los ao retornar o nome dos objetos vencedores no json:
    {"venceu": [retorne 1 se o objeto 1 venceu. retorne 2 se o objeto 2 venceu], "emoji": [EMOJI que você acha que mais se adequa ao OBJETO VENCEDOR], "nome": [NOME do objeto vencedor corrigido para exposição no título da batalha]}"""
    prompt = f"Batalha: {obj1} vs {obj2}.\nQual objeto vence?"
    print(prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Ou "gpt-3.5-turbo", se preferir
            store=True,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
        )

        result_text = response.choices[0].message.content
        print(response.choices[0].message)
        
        # Verificando a resposta da ia e retornando o resultado
        if "venceu" in result_text and "emoji" in result_text:
            x = json.loads(result_text)
            print(x)
            return {"venceu": lista_obj[x["venceu"]-1], "emoji": x["emoji"], "nome": x["nome"]}
    # tratamento de erro
        else:
            return {"error": "Resposta inválida do ChatGPT"}
    except Exception as e:
        print(str(e))
        return {"error": f"Erro ao se comunicar com a API do ChatGPT: {str(e)}"}
        
@app.after_request
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
    return response

@app.route('/hello', methods=['GET'])
def hello():
    return "hello world"

# Endpoint de batalha
@app.route('/batalha', methods=['POST'])
def batalha():
    try:
        # data = json.loads(request.get_json())
        data = request.get_json()

        print(data)

        # obj1, obj2 = data.values()

        obj1 = data.get("obj1")
        obj2 = data.get("obj2")

        if not obj1 or not obj2:
            return jsonify({"error": "Ambos 'obj1' e 'obj2' são obrigatórios."}), 400

        # talvez eu use
        # if obj1 not in battle_rules or obj2 not in battle_rules:
        #     return jsonify({"error": f"'{obj1}' ou '{obj2}' não são objetos válidos."}), 400

        # Determina o resultado da batalha
        # {"venceu": "Pedra", "emoji": "🗿"}
        battle_result = get_battle_result(obj1, obj2)
        print(battle_result)

        if 'error' in battle_result:
            return jsonify(battle_result), 500
        
        # Determinando se o obj2 venceu ou não
        if battle_result["venceu"] == obj2:
            print(jsonify(battle_result))
                         # {"venceu": 2, "newobj": "papel", "newobj_emoji": "📄"}
            return jsonify({"venceu": 2, "newobj": obj2, "newobj_emoji": battle_result["emoji"], "nome": battle_result["nome"]})
        else:
            # Caso obj1 não tenha sido derrotado, um novo objeto é retornado
            nobj = get_random_objeto()
                         # {"venceu": 1, "newobj": "Tesoura", "newobj_emoji": "✂️"}
            return jsonify({"venceu": 1, "newobj": nobj["nome"], "newobj_emoji": nobj["emoji"]})

    except Exception as e:
        print(e)
        return jsonify({"error": f"Erro no servidor: {str(e)}"})

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)
