import streamlit as st
from groq import Groq

st.set_page_config(page_title="Gerador Alphafest Pro", layout="wide")

# Inicializa o cliente Groq
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_anuncio_groq(nome_produto):
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing da Alphafest 3D."},
                {"role": "user", "content": f"Escreva um anúncio de vendas persuasivo para Mercado Livre sobre: {nome_produto}. Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável."}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro no GROQ: {str(e)}"

# A URL do Pollinations gera imagens automaticamente com base no texto
def gerar_url_imagem(nome_produto):
    # O Pollinations transforma texto em imagem instantaneamente via URL
    prompt_limpo = nome_produto.replace(" ", "%20")
    return f"https://pollinations.ai/p/{prompt_limpo}%203d%20printed%20product%20high%20quality%20studio%20lighting?width=1024&height=1024&seed=42"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo Alphafest")
nome_produto = st.text_input("Digite o nome ou link do produto:")

if st.button("Gerar Catálogo Completo"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    else:
        col1, col2 = st.columns(2)
        
        with st.spinner("Gerando anúncio (GROQ)..."):
            texto = gerar_anuncio_groq(nome_produto)
            col1.markdown(texto)
            
        with st.spinner("Preparando imagem..."):
            imagem_url = gerar_url_imagem(nome_produto)
            col2.image(imagem_url, caption=f"Imagem sugerida para {nome_produto}")
