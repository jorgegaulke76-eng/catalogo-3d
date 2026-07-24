import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Puxa a chave da API
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

def gerar_anuncio(nome_produto):
    try:
        # FORÇAMOS o uso do modelo 'gemini-1.5-flash', que é o padrão atual suportado.
        # Estamos ignorando a lista automática para evitar o modelo 2.5 que está bloqueado.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Você é um copywriter da Alphafest (fundada por Anna Lucia Zepelini).
        Escreva um anúncio de vendas persuasivo para o Mercado Livre sobre: {nome_produto}.
        Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável.
        Estrutura: Título chamativo, introdução, 5 benefícios (bullet points), ficha técnica.
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
        st.warning("Configure a chave da API no 'Manage App'.")
    else:
        with st.spinner("Gerando com modelo 1.5-flash..."):
            texto = gerar_anuncio(nome_produto)
            st.info(texto)
