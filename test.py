import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime




@st.cache_data
def init_data():
    # Fetch data from URL here, and then clean it up.
    sales = pd.read_excel(io='https://github.com/asufyanov/pa_workshop/blob/054bf7fc8eaee21a25bcad3d9043c5836930977b/budget_sales.xlsx', sheet_name='рПродажиФакт', engine='openpyxl')
    products = pd.read_excel(io='https://github.com/asufyanov/pa_workshop/blob/054bf7fc8eaee21a25bcad3d9043c5836930977b/budget_sales.xlsx', sheet_name='спрТовары', engine='openpyxl')
    sales_original_names = sales.columns
    sales_english_names = \
    ['check_num', 'date', 'time', 'product', 'amount', 'price', 'total_sum', 
     'payment_method', 'buyer', 'shop', 'cost_of_sales', 'shipment_date']
    sales = sales.rename(columns=dict(zip(sales_original_names, sales_english_names)))

    product_original_names = products.columns
    product_english_names =['product', 'brand', 'subcategory',
        'category', 'size', 'color', 'gender'] 
    products = products.rename(columns=dict(zip(product_original_names,product_english_names)))
    sales['date_month'] = sales.date.dt.strftime('%Y-%m')
    sales['date_week'] = sales.date.dt.strftime('%Y-%W')

    sales = \
    sales.merge(right = products, on = 'product' )

   



    return sales
    

sales = init_data()
shop_list = sorted( list(sales.shop.unique()) )

min_date = sales.date.min()
max_date = sales.date.max()

with st.sidebar:
    add_radio = st.radio(
        "Choose a shipping method",
        ("Daily", "Weekly", "Monthly")
    )


date_picker_min = st.date_input(
    "Select min date",
    min_date)

date_picker_max = st.date_input(
    "Select max date",
    max_date)

st.write(date_picker_max)


options = st.multiselect(
    'What are your favorite colors',
   options = shop_list,
   default=shop_list[:2]
   
   )

#st.write('You selected:', options)

sales_by_month_shop = sales\
    .query('date >= @date_picker_min & date <= @date_picker_max & shop in @options')\
    .groupby(['shop', 'date_month'], as_index=False)\
    .agg(   total_sum = ('total_sum', pd.Series.sum),
            amount = ('amount', pd.Series.sum))


sales_by_month_total = sales_by_month_shop\
    .groupby('date_month', as_index=False)\
    .agg( total_sum = ('total_sum', pd.Series.sum) )

n = 10

sales_top_n_categories = sales\
    .query('date >= @date_picker_min & date <= @date_picker_max & shop in @options')\
    .groupby('category', as_index=False)\
    .agg( total_sum = ('total_sum', pd.Series.sum) )\
    .sort_values('total_sum', ascending=False)\
    .head(10).round(0)

sales_top_n_products = sales\
    .groupby('product', as_index=False)\
    .agg( total_sum = ('total_sum', pd.Series.sum) )\
    .sort_values('total_sum', ascending=False)\
    .head(10).round(0)






st.bar_chart(data = sales_by_month_total, x='date_month',
    y='total_sum')


st.dataframe(sales_by_month_total)

st.dataframe(sales_top_n_products)

top_product_chart = alt.Chart(sales_top_n_products).mark_bar().encode(
    x='total_sum',
    y='product',
    #color='category',
    
)

st.altair_chart(top_product_chart)

top_category_chart = alt.Chart(sales_top_n_categories).mark_arc(innerRadius=50).encode(
   theta=alt.Theta(field="total_sum", type="quantitative"),
    color=alt.Color(field="category", type="nominal"),
    
)

st.altair_chart(top_category_chart)

sales_by_month_total = sales_by_month_shop\
    .groupby('date_month', as_index=False)\
    .agg( total_sum = ('total_sum', pd.Series.sum) )

st.bar_chart(data = sales_by_month_total, x='date_month',
    y='total_sum')


