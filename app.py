import streamlit as st
import requests

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Puxa a chave da API dos secrets do Streamlit
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def gerar_anuncio_direto(nome_produto):
    if not api_key:
        return "Erro: Chave não encontrada nos Secrets do Streamlit."
    
    # Usando a versão v1 (estável) da API
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Atue como copywriter da Alphafest (fundada por Anna Lucia Zepelini). Escreva um anúncio de vendas persuasivo para Mercado Livre sobre: {nome_produto}. Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável. Estrutura: Título chamativo, introdução, 5 benefícios (bullet points) e ficha técnica."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # Verifica se o Google retornou algum erro técnico
        if 'error' in result:
            return f"ERRO DO GOOGLE: {result['error']['message']}"
            
        # Tenta extrair o texto da resposta
        return result['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        return f"Erro de processamento: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome ou link do produto:")

if st.button("Gerar Anúncio"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    else:
        with st.spinner("Gerando anúncio profissional..."):
            texto = gerar_anuncio_direto(nome_produto)
            st.info(texto)
