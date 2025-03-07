import streamlit as st
from transformers import pipeline
import fitz  # PyMuPDF
from docx import Document

# Carregar modelos
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


# Variável para armazenar o histórico de resumos, o texto atual e o histórico de conversas
if 'summary_history' not in st.session_state:
    st.session_state.summary_history = []
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'page' not in st.session_state:
    st.session_state.page = "Gerador de Resumo"

def summarize(text, max_chars):
    """Gera um resumo do texto inserido pelo usuário com base no número de caracteres."""
    if not text.strip():
        return "Erro: O texto está vazio."

    # Ajustar o comprimento máximo do resumo com base no número de caracteres
    max_length = max_chars // 4  # Aproximadamente 4 caracteres por token
    summary_list = summarizer(text, max_length=max_length, min_length=min(50, max_length // 2), length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = summary_list[0]['summary_text']

    # Ajustar o resumo para atingir o número de caracteres desejado
    if len(summary) > max_chars:
        summary = summary[:max_chars]

    return summary

def read_pdf(file):
    """Lê o conteúdo de um arquivo PDF."""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    return text

def read_docx(file):
    """Lê o conteúdo de um arquivo DOCX."""
    doc = Document(file)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text

def main_page():
    """Página principal para o Gerador de Resumo."""
    st.title("📝 Gerador de Resumo com IA")
    st.markdown("""
    Bem-vindo ao Gerador de Resumo com IA! Esta ferramenta permite que você faça o upload de arquivos PDF ou DOCX,
    insira texto diretamente e obtenha um resumo personalizado. Além disso, você pode usar o chatbot para fazer perguntas
    sobre o conteúdo do arquivo. Foi feito com o modelo BART do Facebook.
    
    """)

    # Opção para o usuário fazer upload de arquivos
    uploaded_file = st.file_uploader("Faça o upload de um arquivo PDF ou DOCX:", type=["pdf", "docx"])

    # Caixa de texto para entrada do usuário
    user_input = st.text_area("Digite o texto que deseja resumir:", height=200)

    # Controle deslizante para ajustar o número de caracteres do resumo
    max_chars = st.slider("Ajuste o número de caracteres do resumo:", min_value=50, max_value=1000, value=150, step=10)

    # Botão para gerar o resumo
    if st.button("Gerar Resumo"):
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                st.session_state.current_text = read_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.session_state.current_text = read_docx(uploaded_file)
            else:
                st.warning("Tipo de arquivo não suportado.")
                st.session_state.current_text = ""
        elif user_input.strip():
            st.session_state.current_text = user_input
        else:
            st.warning("Por favor, digite um texto ou faça o upload de um arquivo antes de gerar o resumo.")
            st.session_state.current_text = ""

        if st.session_state.current_text:
            summary = summarize(st.session_state.current_text, max_chars)
            st.session_state.summary_history.append(summary)
            st.write("### ✨ Resumo Gerado:")
            st.write(summary)

            # Opção para baixar o resumo
            st.download_button("Baixar Resumo", summary, "resumo.txt")

    # Exibir histórico de resumos
    if st.session_state.summary_history:
        st.write("### Histórico de Resumos:")
        for idx, summary in enumerate(st.session_state.summary_history):
            st.write(f"**Resumo {idx + 1}:**")
            st.write(summary)


# Configuração das páginas
pages = {
    "Gerador de Resumo": main_page,
    
}

# Navegação com botões na barra lateral
st.sidebar.title("Navegação")
for page_name in pages.keys():
    if st.sidebar.button(page_name):
        st.session_state.page = page_name

# Exibir a página selecionada
pages[st.session_state.page]()
