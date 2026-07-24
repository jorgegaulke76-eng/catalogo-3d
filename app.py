import streamlit as st
from groq import Groq
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Alphafest Pro", layout="wide")

# --- INICIALIZAÇÃO DOS CLIENTES ---
# Certifique-se de que GROQ_API_KEY esteja configurada no "Secrets" do Streamlit
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Erro ao carregar chave de API. Verifique os 'Secrets' no seu painel.")
    st.stop()

# --- FUNÇÃO DE TEXTO (GROQ) ---
def gerar_anuncio_groq(nome_produto):
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos, profissionais, focados em venda e qualidade da Bambu Lab A1."},
                {"role": "user", "content": f"Crie um anúncio de vendas persuasivo para o produto: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar texto: {str(e)}"

# --- FUNÇÃO DE IMAGEM (POLLINATIONS) ---
def gerar_url_imagem(nome_produto):
    # Extrai apenas o nome do produto caso seja um link do MakerWorld
    # Ex: .../models/123-nome-do-produto -> 'nome do produto'
    nome_limpo = nome_produto.split('/')[-1].replace('-', ' ').split('?')[0]
    
    # Cria prompt profissional para IA de imagem
    prompt = f"{nome_limpo} 3d printed action figure high quality product photography studio white background"
    
    # Codifica a URL corretamente para evitar erros de caracteres especiais
    encoded_prompt = urllib.parse.quote(prompt)
    
    return f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"

# --- INTERFACE ---
st.title("📦 Gerador de Catálogo Alphafest")
nome_produto = st.text_input("Digite o nome ou link do produto:")

if st.button("Gerar Catálogo Completo"):
    if not nome_produto:
        st.warning("Por favor, digite o nome do produto.")
    else:
        # Colunas para organizar o conteúdo
        col1, col2 = st.columns([1, 1])
        
        with col1:
            with st.spinner("Gerando texto com GROQ..."):
                texto = gerar_anuncio_groq(nome_produto)
                st.markdown(texto)
        
        with col2:
            with st.spinner("Preparando imagem..."):
                imagem_url = gerar_url_imagem(nome_produto)
                st.image(imagem_url, caption=f"Imagem sugerida para: {nome_produto}", use_container_width=True)
