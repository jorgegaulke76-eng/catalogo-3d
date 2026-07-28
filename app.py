import streamlit as st
import os

# --- DEBUG: Verifica onde o Streamlit está rodando ---
# Isso vai aparecer no seu log do terminal/console
print(f"Diretório atual de trabalho: {os.getcwd()}")
print(f"Arquivos no diretório: {os.listdir('.')}")

def carregar_imagem(caminho_relativo):
    """
    Função robusta para carregar imagens independente do diretório de execução.
    """
    # Garante que o caminho é tratado corretamente pelo sistema
    caminho_corrigido = os.path.join(os.getcwd(), caminho_relativo)
    
    if os.path.exists(caminho_corrigido):
        return caminho_corrigido
    else:
        # Tenta procurar sem o caminho absoluto, caso o arquivo esteja na raiz
        if os.path.exists(caminho_relativo):
            return caminho_relativo
        else:
            return None

# --- APLICAÇÃO ---

# Exemplo de como usar a correção na linha onde estava o erro (ex: linha 148):
# Supondo que 'imgs[0]' seja o nome do arquivo (ex: 'foto.jpg')
nome_arquivo = imgs[0]
caminho_final = carregar_imagem(nome_arquivo)

if caminho_final:
    # Se encontrou o arquivo, exibe
    c_row1.image(caminho_final, width=88)
else:
    # Se não encontrou, evita o erro e avisa no app
    st.error(f"O Streamlit não encontrou o arquivo: {nome_arquivo}")
    st.write(f"Verifique se o arquivo está na pasta raiz. Onde ele está procurando: {os.getcwd()}")

# ... Resto do seu código original continua aqui abaixo ...
