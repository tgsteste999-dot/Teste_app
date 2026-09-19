import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cruzador de Bases", layout="centered")

st.title("📊 Cruzador & Calculador Móvel")

# 1. Carregamento dos Arquivos (RAM)
st.subheader("1. Selecione os Arquivos (CSV ou Excel)")
arquivo_a = st.file_uploader("Base A", type=["csv", "xlsx"])
arquivo_b = st.file_uploader("Base B", type=["csv", "xlsx"])


@st.cache_data
def carregar_dados(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)


if arquivo_a and arquivo_b:
    df_a = carregar_dados(arquivo_a)
    df_b = carregar_dados(arquivo_b)

    st.success("Bases carregadas e indexadas na memória com sucesso!")

    # 2. Configuração do Cruzamento (Join / Tabela Hash)
    st.subheader("2. Chaves de Cruzamento")
    col1, col2 = st.columns(2)
    with col1:
        chave_a = st.selectbox("Chave na Base A:", df_a.columns)
    with col2:
        chave_b = st.selectbox("Chave na Base B:", df_b.columns)

    # Realiza o cruzamento instantâneo
    merged = pd.merge(
        df_a, df_b, left_on=chave_a, right_on=chave_b, suffixes=("_A", "_B")
    )

    # 3. Operações Matemáticas entre Colunas
    st.subheader("3. Calculadora de Colunas")

    col_num_a = st.selectbox("Coluna da Base A:", df_a.columns)
    operacao = st.selectbox(
        "Operação:",
        [
            "Soma (+)",
            "Subtração (-)",
            "Multiplicação (*)",
            "Divisão (/)",
            "Porcentagem A de B (%)",
        ],
    )
    col_num_b = st.selectbox("Coluna da Base B:", df_b.columns)

    if st.button("Executar Cálculo"):
        try:
            val_a = pd.to_numeric(
                merged[f"{col_num_a}_A" if col_num_a in df_b.columns else col_num_a]
            )
            val_b = pd.to_numeric(
                merged[f"{col_num_b}_B" if col_num_b in df_a.columns else col_num_b]
            )

            if operacao == "Soma (+)":
                merged["Resultado"] = val_a + val_b
            elif operacao == "Subtração (-)":
                merged["Resultado"] = val_a - val_b
            elif operacao == "Multiplicação (*)":
                merged["Resultado"] = val_a * val_b
            elif operacao == "Divisão (/)":
                merged["Resultado"] = val_a / val_b
            elif operacao == "Porcentagem A de B (%)":
                merged["Resultado"] = (val_a / val_b) * 100

            st.write("### Resultado do Cruzamento e Cálculo")
            st.dataframe(merged)

            # Botão para baixar o resultado em CSV
            csv = merged.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Baixar Resultado (CSV)",
                data=csv,
                file_name="resultado.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(
                f"Erro no cálculo: Certifique-se de que as colunas selecionadas contêm números. Detalhes: {e}"
            )
