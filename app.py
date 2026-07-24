import streamlit as st
from groq import Groq

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Inicializa o cliente Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_anuncio_groq(nome_produto):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing da Alphafest 3D."},
                {"role": "user", "content": f"Escreva um anúncio de vendas persuasivo para Mercado Livre sobre: {nome_produto}. Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável. Estrutura: Título, introdução, 5 benefícios (bullet points) e ficha técnica."}
            ],
            model="llama3-8b-8192", # Modelo gratuito e super rápido
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na conexão com o Groq: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D (Gratuito)")
nome_produto = st.text_input("Digite o nome ou link do produto:")

if st.button("Gerar Anúncio"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    else:
        with st.spinner("Gerando anúncio com Groq..."):
            resultado = gerar_anuncio_groq(nome_produto)
            st.info(resultado)
