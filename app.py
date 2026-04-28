from flask import Flask, request, jsonify
from flask_cors import CORS
from rapidfuzz import fuzz
import re

app = Flask(__name__)
CORS(app)

ultimo_assunto = ""

respostas_fixas = {
    "o que é alimenta sesi": """O Alimenta Sesi é uma iniciativa do Sesi que oferece serviços de alimentação para indústrias, garantindo refeições equilibradas, seguras e de qualidade para os trabalhadores.""",

    "historia alimenta sesi": """O Alimenta SESI foi criado com o objetivo de promover a saúde e qualidade de vida dos trabalhadores da indústria por meio da alimentação saudável e balanceada.""",

    "objetivo alimenta sesi": """O principal objetivo do Alimenta SESI é promover saúde, bem-estar e produtividade através da oferta de refeições equilibradas e educação alimentar.""",

    "quem pode usar alimenta sesi": """O Alimenta SESI é destinado principalmente aos trabalhadores da indústria, podendo também atender empresas parceiras conforme contratos estabelecidos.""",

    "servicos alimenta sesi": """🍽️ O Alimenta SESI oferece serviços como:
        \n- Refeições industriais
        \n- Gestão de restaurantes corporativos
        \n- Consultoria em alimentação
        \n- Educação nutricional
        \n- Programas de saúde alimentar"""
}


def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto


def detectar_assunto(pergunta):
    if "alimenta sesi" in pergunta:
        return "alimenta sesi"
    return None


def encontrar_resposta(pergunta):
    melhor_match = None
    maior_score = 0

    for chave in respostas_fixas:
        score = fuzz.partial_ratio(pergunta, chave)

        if score > maior_score:
            maior_score = score
            melhor_match = chave

    if maior_score > 70:
        return respostas_fixas[melhor_match]

    return None


@app.route("/chat", methods=["POST"])
def chat():
    global ultimo_assunto

    pergunta = request.json["message"]
    pergunta_limpa = limpar_texto(pergunta)

    assunto = detectar_assunto(pergunta_limpa)
    if assunto:
        ultimo_assunto = assunto

    if any(p in pergunta_limpa for p in ["objetivo", "historia", "o que", "quem", "servicos"]):
        if ultimo_assunto:
            pergunta_limpa += " " + ultimo_assunto

    resposta = encontrar_resposta(pergunta_limpa)

    if resposta:
        return jsonify({"response": resposta})

    return jsonify({
        "response": """Posso te ajudar com:

📖 Sobre o Alimenta SESI  
🍽️ Serviços  
👥 Público atendido  

Tenta perguntar algo como:
- O que é o Alimenta SESI?
- Qual o objetivo?
- Quais serviços oferece?"""
    })


if __name__ == "__main__":
    app.run(debug=True)