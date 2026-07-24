import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

# Configuração da página (deve ser a primeira coisa)
st.set_page_config(page_title="Catálogo 3D", layout="wide")

# Puxa a chave da API das configurações secretas do Streamlit
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Função para tentar raspar a imagem do MakerWorld (busca a imagem de compartilhamento)
def raspar_makerworld(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # Tenta pegar a imagem principal (og:image)
        imagem = soup.find("meta", property="og:image")
        titulo = soup.find("meta", property="og:title")
        
        url_imagem = imagem["content"] if imagem else "https://via.placeholder.com/400?text=Imagem+Nao+Encontrada"
        texto_titulo = titulo["content"] if titulo else "Produto 3D"
        
        return url_imagem, texto_titulo
    except:
        return "https://via.placeholder.com/400?text=Erro+ao+buscar", "Produto Manual"

# Função para gerar o texto estilo Mercado Livre com a IA
def gerar_anuncio(nome_produto):
    if not api_key:
        return "Erro: Chave da API não configurada."
    
    modelo = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    Atue como um vendedor Elite do Mercado Livre. Crie uma descrição de vendas persuasiva para: {nome_produto}.
    Destaque que a peça é fabricada em PLA de alta qualidade, garantindo resistência. Mencione também que o produto é feito utilizando uma impressora Bambu Lab A1, o que garante precisão milimétrica e um acabamento impecável.
    
    Estrutura:
    1. Título chamativo.
    2. Breve introdução focada na qualidade de fabricação.
    3. 5 Benefícios em bullet points.
    4. Ficha técnica (Material: PLA).
    """
    resposta = modelo.generate_content(prompt)
    return resposta.text

# --- INTERFACE DO USUÁRIO ---
st.title("📦 Gerador de Catálogo - Impressão 3D")

url_input = st.text_input("Cole o link do MakerWorld para extrair:")

if st.button("Gerar Card do Produto"):
    with st.spinner("Buscando dados e gerando descrição..."):
        # 1. Busca a Imagem
        img_url, titulo = raspar_makerworld(url_input)
        
        # 2. Gera o Texto
        texto_vendas = gerar_anuncio(titulo)
        
        # 3. Monta o Card na Tela
        st.divider()
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img_url, caption=titulo, use_column_width=True)
            
        with col2:
            st.subheader("Descrição Gerada (Mercado Livre)")
            st.markdown(texto_vendas)
