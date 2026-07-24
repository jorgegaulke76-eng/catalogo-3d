import streamlit as st
import requests
import json

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def gerar_anuncio_direto(nome_produto):
    if not api_key:
        return "Erro: Chave não encontrada."
    
    # URL usando o modelo 1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Escreva um anúncio de vendas persuasivo para: {nome_produto}. Estrutura: Título, introdução, 5 benefícios, ficha técnica."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # DEBUG: Se der erro, vamos mostrar o erro real do Google
        if 'error' in result:
            return f"ERRO DO GOOGLE: {result['error']['message']} (Código: {result['error']['code']})"
            
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    with st.spinner("Conectando..."):
        texto = gerar_anuncio_direto(nome_produto)
        st.info(texto)
