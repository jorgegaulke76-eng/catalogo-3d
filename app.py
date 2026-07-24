import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Gerador Alphafest", layout="wide")

# Configura o cliente OpenAI com a chave dos Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def gerar_anuncio_openai(nome_produto):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing da Alphafest 3D."},
                {"role": "user", "content": f"Escreva um anúncio de vendas persuasivo para Mercado Livre sobre: {nome_produto}. Destaque: PLA de alta qualidade, precisão da Bambu Lab A1, acabamento impecável."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na conexão com a OpenAI: {str(e)}"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo - Alphafest 3D (Via OpenAI)")
nome_produto = st.text_input("Digite o nome ou link do produto:")

if st.button("Gerar Anúncio"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    else:
        with st.spinner("Gerando anúncio..."):
            resultado = gerar_anuncio_openai(nome_produto)
            st.info(resultado)
