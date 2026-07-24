import streamlit as st
from groq import Groq
import urllib.parse

st.set_page_config(page_title="Gerador Alphafest Pro", layout="wide")

# Configuração da Chave
if "GROQ_API_KEY" not in st.secrets:
    st.error("Configure a chave GROQ_API_KEY nos Settings > Secrets.")
    st.stop()

groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def gerar_anuncio_correto(nome_produto):
    # Prompt FORÇADO para focar no produto e não na impressora
    prompt_sistema = """Você é o copywriter da ALPHAFEST ITATIBA.
    REGRA 1: Você NUNCA vende a impressora. Você vende a PEÇA final impressa em 3D.
    REGRA 2: Destaque que a peça foi fabricada pela Alphafest com alta precisão (Bambu Lab A1).
    REGRA 3: O texto deve ser profissional, pronto para o Mercado Livre.
    REGRA 4: Inclua: Título, Descrição, Características e Preço sugerido."""
    
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Crie um anúncio de venda para a peça impressa em 3D: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

st.title("📦 Gerador de Catálogo Alphafest")
nome_produto = st.text_input("Digite o nome ou link do produto:")

if st.button("Gerar Anúncio"):
    if nome_produto:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            with st.spinner("Gerando anúncio focado no produto..."):
                st.markdown(gerar_anuncio_correto(nome_produto))
        
        with col2:
            # Corrigindo a exibição da imagem
            nome_limpo = nome_produto.split('/')[-1].replace('-', ' ').split('?')[0]
            # Usando uma URL de imagem que é mais compatível com navegadores
            st.write("### Imagem do Produto")
            st.image(f"https://pollinations.ai/p/{urllib.parse.quote(nome_limpo)}?width=800&height=800&seed=1")
    else:
        st.warning("Digite algo primeiro.")
