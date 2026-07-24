import streamlit as st
import google.generativeai as genai

# Configuração
st.set_page_config(page_title="Catálogo 3D - Alphafest", layout="wide")
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

def gerar_anuncio(nome_produto):
    try:
        # Busca a lista real de modelos autorizados para sua chave
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            return "Erro: Nenhum modelo disponível para esta chave."
        
        # Pega o primeiro modelo que NÃO seja de visão (usamos o primeiro da lista retornada pelo Google)
        modelo_escolhido = models[0]
        model = genai.GenerativeModel(modelo_escolhido)
        
        prompt = f"""
        Você é um copywriter de elite da Alphafest (fundada por Anna Lucia Zepelini).
        Escreva um anúncio de vendas persuasivo para Mercado Livre sobre: {nome_produto}.
        Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável.
        Estrutura: Título chamativo, introdução, 5 benefícios (bullet points), ficha técnica.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D")
nome_produto = st.text_input("Digite o nome do produto:")

if st.button("Gerar Anúncio"):
    if not api_key:
        st.warning("Configure a chave da API no 'Manage App'.")
    else:
        with st.spinner("Gerando com modelo automático..."):
            texto = gerar_anuncio(nome_produto)
            st.info(texto)
