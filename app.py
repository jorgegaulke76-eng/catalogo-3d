import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Puxa a chave da API
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

def gerar_anuncio(nome_produto):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Atue como um copywriter de elite da Alphafest (fundada por Anna Lucia Zepelini).
        Escreva um anúncio de vendas persuasivo para o Mercado Livre sobre o produto: {nome_produto}.
        
        Destaque sempre:
        - Fabricação em PLA de alta qualidade (resistência e durabilidade).
        - Impressão em impressora Bambu Lab A1 (precisão milimétrica e acabamento impecável).
        
        Estrutura obrigatória do anúncio:
        1. Título chamativo para Mercado Livre.
        2. Breve introdução focada na marca Alphafest.
        3. 5 Benefícios em bullet points (ex: resistente, design exclusivo, acabamento premium, etc).
        4. Ficha técnica (Material, Tecnologia de Impressão, Marca).
        5. Chamada para ação e garantia.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    if not api_key:
        st.warning("Configure a chave da API no 'Manage App' do seu aplicativo no Streamlit.")
    else:
        with st.spinner("Gerando anúncio de alta performance..."):
            texto = gerar_anuncio(nome_produto)
            st.info(texto)
