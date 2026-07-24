import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configuração
st.set_page_config(page_title="Gerador Alphafest", layout="wide")
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

def gerar_anuncio(nome_produto):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Reforcei o prompt para a IA não te dar um modelo, mas sim o texto pronto
        prompt = f"""
        Você é um copywriter de elite da Alphafest, marca fundada por Anna Lucia Zepelini.
        Escreva um anúncio de vendas pronto para copiar e colar no Mercado Livre para o produto: {nome_produto}.
        
        Use esta estrutura:
        1. TÍTULO CHAMATIVO (SEO amigável).
        2. Introdução destacando que o produto é impresso em 3D profissional (Bambu Lab A1) com PLA de alta qualidade.
        3. 5 Benefícios em bullet points (acabamento impecável, resistência, precisão, etc).
        4. FICHA TÉCNICA (Material, Impressora, Marca Alphafest).
        5. Garantia e chamada para ação.
        
        Escreva de forma persuasiva, direta e focada em quem lê pelo celular.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
# Novo campo manual para garantir que a IA saiba exatamente o que vender
nome_manual = st.text_input("Nome do Produto (se o robô não achar, digite aqui):")

if st.button("Gerar Anúncio Profissional"):
    with st.spinner("Gerando copy de vendas..."):
        texto = gerar_anuncio(nome_manual)
        st.info(texto)
