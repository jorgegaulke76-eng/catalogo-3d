import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Configura a chave
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

# FORÇANDO O USO DA VERSÃO V1 ESTÁVEL
genai.configure(api_key=api_key)
client = genai.Client(api_version='v1') 

def gerar_anuncio(nome_produto):
    try:
        # Usamos o modelo 'gemini-1.5-flash' com a versão estável
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Atue como copywriter da Alphafest. Escreva um anúncio de vendas 
        persuasivo para Mercado Livre sobre: {nome_produto}. 
        Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável. 
        Estrutura: Título, introdução, 5 benefícios (bullet points) e ficha técnica."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    else:
        with st.spinner("Conectando com a IA..."):
            resultado = gerar_anuncio(nome_produto)
            st.info(resultado)
