import streamlit as st
import pandas as pd
import io
import urllib.parse
from groq import Groq

# --- CONFIGURAÇÕES ---
# Lembre-se: GROQ_API_KEY deve estar em Settings > Secrets
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---

def extrair_nome_do_link(link):
    """Extrai um nome legível a partir de um link do MakerWorld."""
    # Pega a última parte da URL, remove caracteres especiais e formata
    nome = link.split('/')[-1].split('?')[0].replace('-', ' ')
    return nome.title()

def gerar_url_imagem(nome_produto):
    """Gera URL simplificada para imagem."""
    # Usa o nome limpo para gerar a imagem
    prompt = f"{nome_produto} 3d printed object"
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true"

def calcular_preco(peso_g, tempo_h, preco_kg, margem_lucro, custo_hora, complexidade):
    custo_filamento = (peso_g / 1000) * preco_kg
    custo_operacional = (custo_hora * tempo_h) * complexidade
    custo_total = custo_filamento + custo_operacional + 1.50
    preco_venda = custo_total * (1 + (margem_lucro / 100))
    return round(custo_total, 2), round(preco_venda, 2)

def gerar_anuncio_ia(nome_produto):
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o especialista de marketing da ALPHAFEST ITATIBA. Escreva anúncios persuasivos para peças 3D. Máximo 2 parágrafos."},
                {"role": "user", "content": f"Crie um anúncio de vendas para: {nome_produto}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except:
        return "Peça 3D Alphafest de alta precisão."

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
st.title("📦 ALPHAFEST ITATIBA - Gerador de Catálogo")

with st.sidebar:
    st.header("Configurações")
    preco_kg = st.number_input("Preço Kg Filamento (R$)", value=90.00)
    margem = st.number_input("Margem Lucro (%)", value=200.0)
    custo_hora = st.number_input("Custo Máquina/Hora (R$)", value=1.10)
    complexidade = st.slider("Fator Complexidade", 1.0, 2.0, 1.0)

nome_lote = st.text_input("Nome do Lote:", "Lote Geral")
links_input = st.text_area("Cole os nomes ou links (um por linha):")

if st.button("Gerar Catálogo"):
    if not links_input:
        st.warning("Insira ao menos um produto!")
    else:
        linhas = links_input.split('\n')
        dados_catalogo = []
        
        with st.spinner("Gerando dados e imagens..."):
            for i, item in enumerate(linhas):
                if not item.strip(): continue
                link = item.strip()
                
                # Nome limpo para exibir na tela e gerar a imagem
                nome_exibicao = extrair_nome_do_link(link)
                
                peso, tempo = 100.0, 2.0 
                custo_total, preco_venda = calcular_preco(peso, tempo, preco_kg, margem, custo_hora, complexidade)
                
                dados_catalogo.append({
                    "Nome_Exibicao": nome_exibicao,
                    "Imagem": gerar_url_imagem(nome_exibicao),
                    "Descrição": gerar_anuncio_ia(nome_exibicao),
                    "Custo (R$)": custo_total,
                    "Preço Venda (R$)": preco_venda
                })

            df = pd.DataFrame(dados_catalogo)
            
            # Botão Excel
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            st.download_button("📥 Baixar Excel", buffer, f"catalogo_{nome_lote}.xlsx", "application/vnd.ms-excel")
            
            # Layout em Cartões
            st.subheader("Catálogo Gerado")
            for _, row in df.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        # Usando a nova URL mais estável da Pollinations
                        st.image(row["Imagem"], use_container_width=True)
                    with c2:
                        st.write(f"### {row['Nome_Exibicao']}")
                        st.write(row['Descrição'])
                    with c3:
                        st.metric("Custo", f"R$ {row['Custo (R$)']:.2f}")
                        st.metric("Venda", f"R$ {row['Preço Venda (R$)']:.2f}")
            
            st.success("Catálogo gerado com sucesso!")
