import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Catálogo 3D", layout="wide")

# Puxa a chave da API
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not api_key:
    st.error("⚠️ Atenção: A chave da API do Google não foi encontrada.")
else:
    genai.configure(api_key=api_key)

def raspar_makerworld(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        resposta = requests.get(url, headers=headers)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        imagem = soup.find("meta", property="og:image")
        titulo = soup.find("meta", property="og:title")
        
        url_imagem = imagem["content"] if imagem else "https://cdn-icons-png.flaticon.com/512/3063/3063822.png"
        texto_titulo = titulo["content"] if titulo else "Produto 3D"
        
        return url_imagem, texto_titulo
    except Exception:
        return "https://cdn-icons-png.flaticon.com/512/3063/3063822.png", "Produto"

def gerar_anuncio(nome_produto):
    try:
        # Pede a lista de modelos que conseguem gerar conteúdo
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not modelos_disponiveis:
            return "Erro: Nenhum modelo de IA encontrado para esta chave no momento. Verifique sua cota no Google AI Studio."
            
        # Pega exatamente o primeiro modelo da lista, ignorando se é 1.5, 2.5 ou pro.
        # Filtramos apenas para garantir que não estamos pegando um modelo exclusivo para imagens (vision).
        modelo_escolhido = None
        for m in modelos_disponiveis:
            if 'vision' not in m.lower():
                modelo_escolhido = m
                break
                
        if not modelo_escolhido:
            # Se por acaso todos tiverem vision no nome, pega o primeiro da lista.
            modelo_escolhido = modelos_disponiveis[0]

        # Inicializa a IA com o modelo que foi aceito
        modelo = genai.GenerativeModel(modelo_escolhido)
        
        # Ajustei o prompt para destacar a Anna Lucia Zepelini, já que ela é a fundadora da Alphafest!
        prompt = f"""
        Atue como um vendedor Elite do Mercado Livre da loja Alphafest (fundada por Anna Lucia Zepelini). Crie uma descrição de vendas persuasiva para: {nome_produto}.
        Destaque que a peça é fabricada em PLA de alta qualidade, garantindo resistência. Mencione também que o produto é feito utilizando uma impressora Bambu Lab A1, o que garante precisão milimétrica e um acabamento impecável em cada peça.
        
        Estrutura:
        1. Título chamativo.
        2. Breve introdução.
        3. 5 Benefícios em bullet points.
        4. Ficha técnica.
        """
        resposta = modelo.generate_content(prompt)
        return resposta.text
    except Exception as e:
        return f"🚨 Erro na Geração: {e}"

# --- INTERFACE DO USUÁRIO ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")

url_input = st.text_input("Cole o link do MakerWorld para extrair:")

if st.button("Gerar Card do Produto"):
    if not api_key:
        st.warning("Configure a chave da API no 'Manage App' do Streamlit antes de continuar.")
    else:
        with st.spinner("Buscando dados e conectando à IA..."):
            img_url, titulo = raspar_makerworld(url_input)
            texto_vendas = gerar_anuncio(titulo)
            
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(img_url, caption=titulo, use_column_width=True)
                
            with col2:
                st.subheader("Descrição Gerada (Mercado Livre)")
                st.info(texto_vendas)
