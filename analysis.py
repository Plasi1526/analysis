import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.linear_model import LinearRegression

# Стили
st.markdown("""
<style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    .stPlotlyChart {
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Загрузка данных
df = pd.read_csv("sales_data.csv")
df["Sale_Date"] = pd.to_datetime(df["Sale_Date"])
df["Month"] = df["Sale_Date"].dt.month_name()

# Фильтр по региону
регион = st.selectbox("Выберите регион", df["Region"].unique())

#Фильтры по продуктам
продукты = st.multiselect("Выберите продукты", df["Product_Category"].unique(), default=df["Product_Category"].unique())

# Фильтруем данные
отфильтрованный = df[
    (df["Region"] == регион) &
    (df["Product_Category"].isin(продукты))
]
# Группировка по месяцам (только по отфильтрованным данным)
месячная_статистика = (
    отфильтрованный.groupby(отфильтрованный["Sale_Date"].dt.month_name())
    ["Sales_Amount"].mean()
    .reset_index()
)
# Сортировка месяцев
месяца_по_порядку = pd.CategoricalDtype(
    categories=[
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    ordered=True
)

месячная_статистика["Month"] = месячная_статистика["Sale_Date"].astype(месяца_по_порядку)
месячная_статистика = месячная_статистика.sort_values("Month")

# Прогноз на следующий месяц
if len(месячная_статистика) >1:
    месячная_статистика["месяц_число"] = range(len(месячная_статистика))
    модель = LinearRegression()
    модель.fit(месячная_статистика[["месяц_число"]], месячная_статистика["Sales_Amount"])
    следующий_месяц = len(месячная_статистика)
    прогноз = модель.predict([[следующий_месяц]])
    st.metric("Прогноз на следующий месяц", f"{прогноз[0]:.2f} руб.")


# График по месяцам
st.title("📊 Анализ продаж")
fig1 = px.line(месячная_статистика, x="Month", y="Sales_Amount", title="Средние продажи по месяцам")
st.plotly_chart(fig1)

st.markdown("## 📈 Продажи по каналам")
каналы_статистика = отфильтрованный.groupby(["Month", "Sales_Channel"])["Sales_Amount"].mean().reset_index()
fig2 = px.line(каналы_статистика, x="Month", y="Sales_Amount", color="Sales_Channel", title="Продажи по каналам")
st.plotly_chart(fig2)

st.write("### 📄 Таблица (первые 5 строк):")
st.dataframe(df.head())

st.metric("Средние продажи", f"{месячная_статистика['Sales_Amount'].mean():.2f} руб.")


# Делаем график в Plotly
fig = px.line(месячная_статистика, x="Month", y="Sales_Amount", title="Средние продажи по месяцам")
fig.update_traces(mode="markers+lines")
st.plotly_chart(fig)