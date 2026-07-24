import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gerador Alphafest", layout="wide")
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

def gerar_anuncio(nome_produto):
    try:
        # A MÁGICA: Em vez de escrever o nome, pedimos ao servidor para listar o que ele aceita
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Filtra para pegar apenas os modelos que funcionam para texto (evita modelos de imagem/vision)
        text_models = [m for m in models if 'vision' not in m and 'embedding' not in m]
        
        if not text_models:
            return f"Erro: Nenhum modelo de texto encontrado. Modelos disponíveis na conta: {models}"
            
        # Pega o primeiro modelo válido da lista automática
        model = genai.GenerativeModel(text_models[0])
        
        prompt = f"""
        Você é um copywriter da Alphafest (fundada por Anna Lucia Zepelini).
        Escreva um anúncio de vendas persuasivo para o Mercado Livre sobre: {nome_produto}.
        Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável.
        Estrutura: Título, introdução, 5 benefícios (bullet points), ficha técnica.
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
        with st.spinner("Conectando ao modelo disponível..."):
            texto = gerar_anuncio(nome_produto)
            st.info(texto)
