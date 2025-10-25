
#app.py
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
from database import init_db, update_stock, get_stock, add_history, get_history
from detector import detect_item  # Nosso detector com SavedModel

# ===================== Inicializar banco =====================
init_db()

# ===================== Configuração da página =====================
st.set_page_config(page_title="Controle de Estoque Hospitalar", layout="wide")
st.sidebar.title("Menu")
st.image("img.png", width=200 )
st.title("StockEye")
menu = st.sidebar.radio("Navegar", ["Dashboard", "Capturar", "Gerenciar Estoque", "Relatórios"])

# ===================== DASHBOARD =====================
if menu == "Dashboard":
    st.title("📊 Dashboard do Estoque")
    df = pd.DataFrame(get_stock(), columns=["Item", "Quantidade"])

    if not df.empty:
        fig = px.bar(df, x="Item", y="Quantidade", text="Quantidade",
                     title="Nível de Estoque Atual", color="Item")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)
    else:
        st.info("Nenhum item no estoque ainda.")

# ===================== CAPTURAR =====================
elif menu == "Capturar":
    st.title("📷 Captura por Câmera")
    img_file = st.camera_input("Tire uma foto do item")

    if img_file is not None:
        image = Image.open(img_file).convert("RGB")

        # Detectar item usando SavedModel
        item = detect_item(image)

        if item:
            st.success(f"Item detectado: {item}")

            col1, col2, col3 = st.columns(3)

            # Confirmar
            with col1:
                if st.button("✅ Confirmar"):
                    update_stock(item, -1)
                    add_history(item, "Saída", 1)
                    st.success(f"{item} baixado (-1) do estoque.")

            # Editar
            with col2:
                qtd = st.number_input("Quantidade a baixar", min_value=1, step=1)
                if st.button("✏️ Salvar"):
                    update_stock(item, -qtd)
                    add_history(item, "Saída", qtd)
                    st.success(f"{item} baixado (-{qtd}) do estoque.")

            # Apagar
            with col3:
                if st.button("🗑️ Apagar"):
                    st.warning("Captura descartada. Nenhuma alteração no estoque.")
        else:
            st.error("Não foi possível identificar o item.")

# ===================== GERENCIAR ESTOQUE =====================
elif menu == "Gerenciar Estoque":
    st.title("📦 Gerenciar Estoque")
    action = st.radio("Ação", ["Entrada", "Saída"])

    # Itens existentes
    from database import listar_itens_existentes
    itens_existentes = listar_itens_existentes()
    novo_item = "Adicionar novo item"
    item = st.selectbox("Selecione o item", options=[novo_item] + itens_existentes)

    if item == novo_item:
        item = st.text_input("Digite o nome do novo item")

    qtd = st.number_input("Quantidade", min_value=1, step=1)

    if st.button("Registrar"):
        if item:
            if action == "Entrada":
                update_stock(item, qtd)
                add_history(item, "Entrada", qtd)
                st.success(f"{qtd} unidades de {item} adicionadas ao estoque.")
            else:
                update_stock(item, -qtd)
                add_history(item, "Saída", qtd)
                st.success(f"{qtd} unidades de {item} removidas do estoque.")
        else:
            st.error("Digite ou selecione o nome do item.")

# ===================== RELATÓRIOS =====================
elif menu == "Relatórios":
    st.title("📑 Relatórios de Movimentações")
    df = pd.DataFrame(get_history(), columns=["ID", "Item", "Ação", "Quantidade", "Data"])

    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Nenhuma movimentação registrada ainda.")





# streamlit run app.py