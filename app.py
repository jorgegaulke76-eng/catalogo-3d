import streamlit as st
import requests

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Coloque sua chave aqui nos Secrets como sempre
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def gerar_anuncio_estavel(nome_produto):
    # Usando a versão de endpoint mais genérica e compatível
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"Atue como copywriter da Alphafest. Escreva um anúncio de vendas persuasivo para: {nome_produto}. Destaque: PLA de alta qualidade, precisão da Bambu Lab A1."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro {response.status_code}: {data.get('error', {}).get('message', 'Erro desconhecido')}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

st.title("📦 Gerador Alphafest (Modo Alternativo)")
nome = st.text_input("Nome do produto:")
if st.button("Gerar"):
    resultado = gerar_anuncio_estavel(nome)
    st.write(resultado)
