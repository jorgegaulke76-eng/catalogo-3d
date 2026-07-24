import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

def gerar_anuncio(nome_produto):
    try:
        # A MÁGICA: Listamos todos os modelos disponíveis para SUA chave
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            return "Erro: Nenhum modelo disponível para esta chave."
            
        # Pegamos o primeiro modelo da lista que o Google nos der (seja ele qual for)
        model = genai.GenerativeModel(models[0].name)
        
        prompt = f"""
        Você é copywriter da Alphafest. Escreva um anúncio persuasivo para Mercado Livre sobre: {nome_produto}.
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
        with st.spinner("Conectando ao seu modelo liberado..."):
            texto = gerar_anuncio(nome_produto)
            st.info(texto)
