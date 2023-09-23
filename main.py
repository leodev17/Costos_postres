import streamlit as st
import pandas as pd
if 'lista_pedidos' not in st.session_state:
    st.session_state.lista_pedidos = []

#Creacion de df
df_ing = pd.read_excel("tabla_base.xlsx", sheet_name="Ingredientes", header=0)
df_rec = pd.read_excel("tabla_base.xlsx", sheet_name="Recetas", header=0)
df_join = pd.merge(df_ing, df_rec, left_on='ID', right_on='ID_Ingrediente')
# Agregar costo parcial de cada ingrediente
df_join['Costo parcial'] = df_join['Precio_u'] * (df_join['Cantidad_us'] / df_join['Cantidad_u'])


def obtener_info_postres():
    lista_df = []
    for postre in df_join['Postre'].unique():
        lista_df.append(df_join.loc[df_join['Postre'] == postre])
    return lista_df


def obtener_costo_postre():
    df_join2 = df_join.copy()
    df_join2 = df_join2.groupby('Postre')['Costo parcial'].sum()
    df_join2 = df_join2.rename(columns={'Costo parcial': 'Costo total'})
    return df_join2


def obtener_total_ing(lista_tuplas): #Parametro es [(Nombre_Postre, Cantidad de dicho postre)]
    df_join2 = df_join.copy()
    df_join2['Cantidad postres'] = 0
    for p, cant in lista_tuplas:
        df_join2.loc[df_join2['Postre'] == p, 'Cantidad postres'] += cant
    df_join2['Cantidad_us'] = df_join2['Cantidad_us']*df_join2['Cantidad postres']
    df_join2['Costo parcial'] = df_join2['Costo parcial'] * df_join2['Cantidad postres']
    df_join2 = df_join2.groupby('Nombre').agg({'Cantidad_us': 'sum', 'Costo parcial': 'sum'})
    df_join2 = df_join2.loc[df_join2['Cantidad_us'] > 0]
    return df_join2


def obtener_info_pedido(lista_tuplas):
    df_join2 = df_join.copy()
    df_join2['Cantidad postres'] = 0
    for p, cant in lista_tuplas:
        df_join2.loc[df_join2['Postre'] == p, 'Cantidad postres'] += cant
    df_join2['Cantidad_us'] = df_join2['Cantidad_us'] * df_join2['Cantidad postres']
    df_join2['Costo parcial'] = df_join2['Costo parcial'] * df_join2['Cantidad postres']
    df_join2['Precio_venta'] = df_join2['Precio_venta'] * df_join2['Cantidad postres']
    st.dataframe(df_join2)
    df_join2 = df_join2.groupby(['Postre', 'Precio_venta'])['Costo parcial'].sum().reset_index()
    df_join2 = df_join2.rename(columns={'Costo parcial': 'Costo total'})
    df_join2['% de ganancia sobre la venta'] = 100*(df_join2['Precio_venta']-df_join2['Costo total'])/df_join2['Precio_venta']
    st.dataframe(df_join2.loc[df_join2['Costo total'] > 0], hide_index=True)
    st.write("Se estima que el costo total de los pedidos son " + str(df_join2['Costo total'].sum()) + " mientras "
    "que la venta total es de " + str(df_join2['Precio_venta'].sum()) + " por lo tanto la ganancia esperada es de "
    + str(df_join2['Precio_venta'].sum() - df_join2['Costo total'].sum()))


# Configura la barra lateral con las opciones del menú
menu_option = st.sidebar.radio("Menú", ["Ver resumen de los datos", "Visualizar pedido"])

# Página de inserción de postre
if menu_option == "Ver resumen de los datos":
    st.title("Datos considerados para los calculos")
    st.header("Datos de los ingredientes")
    st.dataframe(df_ing, hide_index=True)
    st.header("Datos de las recetas")
    for i in obtener_info_postres():
        st.subheader("Informacion del postre " + str(i.iloc[0, 4]) + " cuyo precio de "
        "venta es " + str(i.iloc[0,5]))
        st.dataframe(i[['Nombre', 'Cantidad_us']], hide_index=True)

if menu_option == "Visualizar pedido":
    st.title("Hola")
    lista_pedidos = []
    dict_postres=df_rec
    option = st.selectbox(
        'Cual de los postres quieres agregar al pedido?',
         df_join['Postre'].unique())
    cantidad = st.number_input("Que cantidad usaras?", min_value=1, step=1)
    if st.button("Agregar al pedido"):
        if option and cantidad:
            st.session_state.lista_pedidos.append((option, cantidad))
            st.success("Se agrego el postre al pedido con exito")
    if st.button("Limpiar pedidos"):
        st.session_state.lista_pedidos=[]
        st.success("Se vacio la lista total del pedido")
    if st.button("Visualizar pedido total"):
        st.write("Los ingredientes totales serian:")
        st.dataframe(obtener_total_ing(st.session_state.lista_pedidos))
        st.write("Costos y ganancias:")
        obtener_info_pedido(st.session_state.lista_pedidos)
