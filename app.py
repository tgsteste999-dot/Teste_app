import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cruzador Universal de Bases", layout="centered")

st.title("📊 Cruzador & Calculador Universal")

st.subheader("1. Selecione os Arquivos (Qualquer formato de tabela)")
arquivo_a = st.file_uploader("Base A", type=None)
arquivo_b = st.file_uploader("Base B", type=None)


@st.cache_data
def carregar_qualquer_arquivo(file):
    ext = os.path.splitext(file.name)[1].lower()

    if ext == ".csv":
        # Tenta diferentes separadores comuns
        try:
            return pd.read_csv(file)
        except Exception:
            file.seek(0)
            return pd.read_csv(file, sep=";")
    elif ext in [".xlsx", ".xls", ".xlsm"]:
        return pd.read_excel(file)
    elif ext in [".txt", ".tsv"]:
        return pd.read_csv(file, sep=None, engine="python")
    elif ext == ".json":
        return pd.read_json(file)
    elif ext == ".parquet":
        return pd.read_parquet(file)
    elif ext == ".html":
        return pd.read_html(file)[0]
    else:
        # Tenta carregar como CSV padrão se for formato desconhecido
        try:
            return pd.read_csv(file)
        except Exception:
            file.seek(0)
            return pd.read_excel(file)


if arquivo_a and arquivo_b:
    try:
        df_a = carregar_qualquer_arquivo(arquivo_a)
        df_b = carregar_qualquer_arquivo(arquivo_b)

        st.success("Bases carregadas e indexadas na memória com sucesso!")

        # 2. Configuração do Cruzamento
        st.subheader("2. Chaves de Cruzamento")
        col1, col2 = st.columns(2)
        with col1:
            chave_a = st.selectbox("Chave na Base A:", df_a.columns)
        with col2:
            chave_b = st.selectbox("Chave na Base B:", df_b.columns)

        merged = pd.merge(
            df_a, df_b, left_on=chave_a, right_on=chave_b, suffixes=("_A", "_B")
        )

        # 3. Operações Matemáticas
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
                col_a_real = (
                    f"{col_num_a}_A" if col_num_a in df_b.columns else col_num_a
                )
                col_b_real = (
                    f"{col_num_b}_B" if col_num_b in df_a.columns else col_num_b
                )

                val_a = pd.to_numeric(merged[col_a_real], errors="coerce").fillna(0)
                val_b = pd.to_numeric(merged[col_b_real], errors="coerce").fillna(0)

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

                # Opções de Download do Resultado
                st.subheader("4. Baixar Resultado Tratado")
                formato_download = st.radio(
                    "Escolha o formato do arquivo para baixar:",
                    ["CSV (.csv)", "Excel (.xlsx)"],
                )

                if formato_download == "CSV (.csv)":
                    csv_data = merged.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Baixar em CSV",
                        data=csv_data,
                        file_name="resultado_cruzamento.csv",
                        mime="text/csv",
                    )
                else:
                    import io

                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        merged.to_excel(writer, index=False)
                    st.download_button(
                        "📥 Baixar em Excel",
                        data=buffer.getvalue(),
                        file_name="resultado_cruzamento.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            except Exception as e:
                st.error(f"Erro ao realizar o cálculo: {e}")
    except Exception as e:
        st.error(f"Erro ao ler os arquivos enviados: {e}")
