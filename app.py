import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Catálogo 3D", layout="wide")

# Puxa a chave da API e remove espaços invisíveis por segurança (.strip)
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Atenção: A chave da API do Google não foi encontrada nas configurações.")
else:
    genai.configure(api_key=api_key)

def raspar_makerworld(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        imagem = soup.find("meta", property="og:image")
        titulo = soup.find("meta", property="og:title")
        
        url_imagem = imagem["content"] if imagem else "https://via.placeholder.com/400?text=Sem+Imagem"
        texto_titulo = titulo["content"] if titulo else "Produto 3D"
        
        return url_imagem, texto_titulo
    except Exception:
        return "https://via.placeholder.com/400?text=Erro+ao+buscar", "Produto"

def gerar_anuncio(nome_produto):
    try:
        # Modelo mais atual e rápido do Google
        modelo = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Atue como um vendedor Elite do Mercado Livre. Crie uma descrição de vendas persuasiva para: {nome_produto}.
        Destaque que a peça é fabricada em PLA de alta qualidade, garantindo resistência. Mencione também que o produto é feito utilizando uma impressora Bambu Lab A1, o que garante precisão milimétrica e um acabamento impecável.
        
        Estrutura:
        1. Título chamativo.
        2. Breve introdução.
        3. 5 Benefícios em bullet points.
        4. Ficha técnica.
        """
        resposta = modelo.generate_content(prompt)
        return resposta.text
    except Exception as e:
        # Se a chave estiver inválida, vai mostrar esta mensagem amigável no lugar da tela vermelha.
        return f"🚨 Erro do Google: {e}\n\nPor favor, verifique se a sua Chave da API foi copiada corretamente e colada sem espaços extras no Streamlit."

# --- INTERFACE DO USUÁRIO ---
st.title("📦 Gerador de Catálogo - Impressão 3D")

url_input = st.text_input("Cole o link do MakerWorld para extrair:")

if st.button("Gerar Card do Produto"):
    if not api_key:
        st.warning("Configure a chave da API no 'Manage App' do Streamlit antes de continuar.")
    else:
        with st.spinner("Buscando dados e gerando descrição..."):
            img_url, titulo = raspar_makerworld(url_input)
            texto_vendas = gerar_anuncio(titulo)
            
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(img_url, caption=titulo, use_column_width=True)
                
            with col2:
                st.subheader("Descrição Gerada (Mercado Livre)")
                st.info(texto_vendas)
