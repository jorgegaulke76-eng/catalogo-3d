import streamlit as st
import requests

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def gerar_anuncio_direto(nome_produto):
    if not api_key:
        return "Erro: Chave não encontrada nos Secrets."
    
    # URL de acesso direto ao modelo (não consulta lista, vai direto ao ponto)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Escreva um anúncio de vendas para: {nome_produto}. Destaque: PLA, Bambu Lab A1."}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # Se o Google retornar erro, vamos exibir o erro exato
        if 'error' in result:
            return f"ERRO API: {result['error']['message']}"
            
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Erro na execução: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    texto = gerar_anuncio_direto(nome_produto)
    st.info(texto)
