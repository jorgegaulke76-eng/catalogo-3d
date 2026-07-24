import streamlit as st
import requests

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Puxa a chave da API
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def gerar_anuncio_direto(nome_produto):
    if not api_key:
        return "Erro: Chave não encontrada."
    
    # Esta URL usa o modelo de forma direta, sem bibliotecas que causam erro de "lista de modelos"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Atue como copywriter da Alphafest (Anna Lucia Zepelini). Escreva um anúncio de vendas persuasivo para o Mercado Livre sobre: {nome_produto}. Destaque: PLA, Bambu Lab A1, acabamento impecável. Estrutura: Título, introdução, 5 benefícios (bullet points), ficha técnica."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Erro na conexão direta: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    with st.spinner("Gerando via conexão direta..."):
        texto = gerar_anuncio_direto(nome_produto)
        st.info(texto)
