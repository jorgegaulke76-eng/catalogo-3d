import streamlit as st
import requests

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def gerar_anuncio_direto(nome_produto):
    if not api_key:
        return "Erro: Chave não encontrada."
    
    # MUDANÇA: Usando v1 em vez de v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Atue como copywriter da Alphafest. Escreva um anúncio de vendas persuasivo para o Mercado Livre sobre: {nome_produto}. Destaque: PLA, Bambu Lab A1, acabamento impecável. Estrutura: Título, introdução, 5 benefícios (bullet points), ficha técnica."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # Verifica se houve erro na resposta do Google
        if 'error' in result:
            return f"ERRO DO GOOGLE: {result['error']['message']}"
            
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    with st.spinner("Conectando ao servidor estável..."):
        texto = gerar_anuncio_direto(nome_produto)
        st.info(texto)
