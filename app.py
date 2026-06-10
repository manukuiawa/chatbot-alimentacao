from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import unicodedata
import re

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")
contexto = {
    "resultados": None
}


def normalizar(texto):
    texto = str(texto).lower().strip()

    return unicodedata.normalize(
        "NFKD",
        texto
    ).encode(
        "ASCII",
        "ignore"
    ).decode("ASCII")


try:
    df = pd.read_excel("unidades.xlsx", header=1)

    df.columns = [normalizar(col) for col in df.columns]

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    print("Excel carregado com sucesso.")

except Exception as e:
    print("Erro ao carregar Excel:", e)
    df = None


def encontrar_coluna_unidade():

    for col in df.columns:
        if "unidade" in col and "nome" not in col:
            return col

    return None


def formatar_resposta(linha):

    return (
        f"Unidade: {linha.get('nome unidade', 'N/A')}\n\n"
        f"Nutricionista: {linha.get('nutricionista', 'N/A')}\n"
        f"Email: {linha.get('email da nutricionista', 'N/A')}\n"
        f"Contato: {linha.get('contato da unidade', 'N/A')}\n"
        f"Endereço: {linha.get('endereco', 'N/A')}"
    )

def buscar_por_contato(contato):

    contato_limpo = re.sub(r"\D", "", contato)

    for _, linha in df.iterrows():

        valor = re.sub(
            r"\D",
            "",
            str(linha.get("contato da unidade", ""))
        )

        if valor == contato_limpo:
            return linha

    return None

def resposta_especifica(pergunta, linha):

    if "cnpj" in pergunta:
        return str(linha.get("cnpj", "CNPJ não encontrado"))

    if "cep" in pergunta:
        return str(linha.get("cep", "CEP não encontrado"))

    if "abertura" in pergunta:
        return str(
            linha.get(
                "data de abertura",
                "Data de abertura não encontrada"
            )
        )

    if "refeic" in pergunta:
        return str(
            linha.get(
                "refeicoes por dia",
                "Informação não encontrada"
            )
        )

    if "email" in pergunta:
        return str(
            linha.get(
                "email da nutricionista",
                "Email não encontrado"
            )
        )

    if "contato" in pergunta or "telefone" in pergunta:
        return str(
            linha.get(
                "contato da unidade",
                "Contato não encontrado"
            )
        )

    if "nutricionista" in pergunta:
        return str(
            linha.get(
                "nutricionista",
                "Nutricionista não encontrada"
            )
        )

    if "endereco" in pergunta:
        return str(
            linha.get(
                "endereco",
                "Endereço não encontrado"
            )
        )

    return (
        f"Unidade: {linha.get('nome unidade', 'N/A')}\n\n"
        f"Código: {linha.get('no unidade', 'N/A')}\n"
        f"CNPJ: {linha.get('cnpj', 'N/A')}\n"
        f"Data de abertura: {linha.get('data de abertura', 'N/A')}\n\n"
        f"Endereço: {linha.get('endereco', 'N/A')}\n"
        f"CEP: {linha.get('cep', 'N/A')}\n\n"
        f"Refeições por dia: {linha.get('refeicoes por dia', 'N/A')}\n\n"
        f"Nutricionista: {linha.get('nutricionista', 'N/A')}\n"
        f"Email: {linha.get('email da nutricionista', 'N/A')}\n"
        f"Contato: {linha.get('contato da unidade', 'N/A')}"
    )


def buscar_por_codigo(codigo):

    coluna_unidade = encontrar_coluna_unidade()

    resultado = df[
        df[coluna_unidade]
        .astype(str)
        .str.strip()
        == str(codigo)
    ]

    if resultado.empty:
        return None

    return resultado.iloc[0]

def buscar_por_cnpj(cnpj):

    cnpj_limpo = re.sub(r"\D", "", str(cnpj))

    if len(cnpj_limpo) != 14:
        return None

    for _, linha in df.iterrows():

        valor = re.sub(
            r"\D",
            "",
            str(linha["cnpj"])
        )

        if valor == cnpj_limpo:
            return linha

    return None


def buscar_por_cep(cep):

    cep_limpo = re.sub(r"\D", "", cep)

    for _, linha in df.iterrows():

        valor = re.sub(
            r"\D",
            "",
            str(linha.get("cep", ""))
        )

        if valor == cep_limpo:
            return linha

    return None


def buscar_por_nome(texto):

    texto = normalizar(texto)

    return df[
        df["nome unidade"]
        .apply(normalizar)
        .str.contains(texto, na=False)
    ]

def buscar_por_contato(contato):

    contato_limpo = re.sub(r"\D", "", str(contato))

    for _, linha in df.iterrows():

        valor = re.sub(
            r"\D",
            "",
            str(linha.get("contato da unidade", ""))
        )

        if valor == contato_limpo:
            return linha

    return None

def buscar_por_email(email):

    resultado = df[
        df["email da nutricionista"]
        .astype(str)
        .str.lower()
        == email.lower()
    ]

    if resultado.empty:
        return None

    return resultado.iloc[0]

def responder(pergunta):

    global contexto

    if df is None:
        return "A planilha não foi carregada."

    pergunta = normalizar(pergunta)

    # BUSCA REVERSA POR CONTATO

    if (
        ("contato" in pergunta or "telefone" in pergunta)
        and ("de quem" in pergunta or "qual unidade" in pergunta)
    ):

        numeros = re.findall(r"\d+", pergunta)

        if numeros:

            contato = "".join(numeros)

            linha = buscar_por_contato(contato)

            if linha is not None:

                return (
                    f"O contato pertence à unidade:\n\n"
                    f"{linha['nome unidade']}\n"
                    f"Unidade: {linha['no unidade']}"
                )

            return "Não encontrei nenhuma unidade com esse contato."

    pergunta = normalizar(pergunta)

    if "cep" in pergunta and (
        re.search(r"\d{5,8}", pergunta)
    ):

        ceps = re.findall(r"\d+", pergunta)

        if not ceps:
            return "Informe um CEP válido."

        cep = "".join(ceps)

        linha = buscar_por_cep(cep)

        if linha is not None:
            return (
                f"O CEP pertence à unidade:\n"
                f"{linha['nome unidade']}\n"
                f"Código: {linha['no unidade']}"
            )

        return "Não encontrei nenhuma unidade com esse CEP."

    if "cnpj" in pergunta and (
        re.search(r"\d{8,14}", pergunta)
    ):

        cnpjs = re.findall(
            r"\d+",
            pergunta
        )

        if cnpjs:

            cnpj = "".join(cnpjs)

            linha = buscar_por_cnpj(cnpj)

            if linha is not None:

                return (
                    f"O CNPJ pertence à unidade:\n"
                    f"{linha['nome unidade']}\n"
                    f"Unidade: {linha['no unidade']}"
                )

            return "Não encontrei nenhuma unidade com esse CNPJ."



    numeros = re.findall(r"\d+", pergunta)

    if numeros:

        codigo = numeros[0]

        if contexto["resultados"] is not None:

            resultado = contexto["resultados"]

            unidade = resultado[
                resultado[encontrar_coluna_unidade()]
                .astype(str)
                .str.strip()
                == str(codigo)
            ]

            if not unidade.empty:

                contexto["resultados"] = None

                return resposta_especifica(
                    pergunta,
                    unidade.iloc[0]
                )

        unidade = buscar_por_codigo(codigo)

        if unidade is not None:

            return resposta_especifica(
                pergunta,
                unidade
            )

        return f"Não encontrei nenhuma unidade com o código {codigo}."

    palavras_ignorar = [
    "email",
    "nutricionista",
    "contato",
    "telefone",
    "endereco",
    "cnpj",
    "cep",
    "abertura",
    "abriu",
    "refeicoes",
    "refeicao",
    "serve",
    "qual",
    "quem",
    "preciso",
    "passa",
    "me",
    "da",
    "de",
    "do",
    "unidade"
    "qual",
    "quais",
    "quale",
    "qualo",
    "qualeo",
    "e",
    "eh",
    "o",
    "a",
    "os",
    "as",
    "um",
    "uma",
    "me",
    "passa",
    "informe",
    "mostrar",
    "mostre",
    "diga",
    "qual",
]

    termo_busca = pergunta

    for palavra in palavras_ignorar:
        termo_busca = termo_busca.replace(
            palavra,
            ""
        )

    termo_busca = termo_busca.strip()

    if len(termo_busca) < 3:
        return "Não consegui identificar a unidade."

    resultados = buscar_por_nome(termo_busca)

    if resultados.empty:
        return "Não encontrei nenhuma unidade relacionada à sua busca."

    if len(resultados) == 1:

        return resposta_especifica(
            pergunta,
            resultados.iloc[0]
        )

    contexto["resultados"] = resultados

    resposta = f"Encontrei {len(resultados)} unidades:\n"

    coluna_unidade = encontrar_coluna_unidade()

    for _, linha in resultados.iterrows():

        resposta += (
            f"\n{linha[coluna_unidade]} - "
            f"{linha['nome unidade']}"
        )

    resposta += "\n\nQual unidade você deseja consultar?"

    return resposta


@app.route("/chat", methods=["POST"])
def chat():

    pergunta = request.json.get("message", "")

    return jsonify({
        "response": responder(pergunta)
    })


if __name__ == "__main__":
    app.run(debug=True)