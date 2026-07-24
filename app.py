import streamlit as st
import requests

st.set_page_config(page_title="Diagnóstico API", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

def listar_modelos():
    if not api_key:
        return "Chave não encontrada."
    
    # Este é o link oficial para listar os modelos permitidos
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'models' in data:
            # Filtra apenas modelos que suportam geração de texto
            modelos_uteis = [m['name'] for m in data['models'] if 'generateContent' in m.get('supportedMethodNames', [])]
            return modelos_uteis
        else:
            return f"Erro: {data}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

st.title("🔍 Diagnóstico da sua Chave API")
if st.button("Listar modelos permitidos"):
    modelos = listar_modelos()
    st.write("Estes são os nomes dos modelos que sua chave permite usar:")
    st.write(modelos)
