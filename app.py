import streamlit as st
import pandas as pd
import plotly.express as px
import speech_recognition as sr
from packaging.version import Version

# Function to process user queries
def process_query(query, data):
    """Process user queries regarding the DataFrame and return visualizations."""
    query = query.lower()
    response_text = ""
    graph = None

    try:
        if "total sales" in query and "by" not in query:
            total_sales = data['Sales'].sum()
            response_text = f"Total Sales: ${total_sales:,.2f}"
            graph = px.bar(x=["Total Sales"], y=[total_sales], title="Total Sales")

        elif "total quantity" in query:
            total_quantity = data['Quantity'].sum()
            response_text = f"Total Quantity: {total_quantity}"
            graph = px.bar(x=["Total Quantity"], y=[total_quantity], title="Total Quantity")

        elif "total profit" in query:
            total_profit = data['Profit'].sum()
            response_text = f"Total Profit: ${total_profit:,.2f}"
            graph = px.bar(x=["Total Profit"], y=[total_profit], title="Total Profit")

        elif "average delivery days" in query:
            average_delivery_days = data['Delivery Days'].mean()
            response_text = f"Average Delivery Days: {average_delivery_days:.2f}"

        elif "total sales by payment mode" in query:
            sales_by_payment = data.groupby('Payment Mode')['Sales'].sum().reset_index()
            response_text = "Total Sales by Payment Mode:"
            graph = px.bar(sales_by_payment, x='Payment Mode', y='Sales', title='Total Sales by Payment Mode')

        elif "total sales by segment" in query:
            sales_by_segment = data.groupby('Segment')['Sales'].sum().reset_index()
            response_text = "Total Sales by Segment:"
            graph = px.bar(sales_by_segment, x='Segment', y='Sales', title='Total Sales by Segment')

        elif "total sales by ship mode" in query:
            sales_by_ship_mode = data.groupby('Ship Mode')['Sales'].sum().reset_index()
            response_text = "Total Sales by Ship Mode:"
            graph = px.bar(sales_by_ship_mode, x='Ship Mode', y='Sales', title='Total Sales by Ship Mode')

        elif "total sales by category" in query:
            sales_by_category = data.groupby('Category')['Sales'].sum().reset_index()
            response_text = "Total Sales by Category:"
            graph = px.bar(sales_by_category, x='Category', y='Sales', title='Total Sales by Category')

        elif "total sales by sub-category" in query:
            sales_by_sub_category = data.groupby('Sub-Category')['Sales'].sum().reset_index()
            response_text = "Total Sales by Sub-Category:"
            graph = px.bar(sales_by_sub_category, x='Sub-Category', y='Sales', title='Total Sales by Sub-Category')

        elif "monthly sales by year" in query:
            data['Order Date'] = pd.to_datetime(data['Order Date'])
            monthly_sales = data.groupby(data['Order Date'].dt.to_period("M"))['Sales'].sum().reset_index()
            monthly_sales['Order Date'] = monthly_sales['Order Date'].astype(str)
            response_text = "Monthly Sales by Year:"
            graph = px.line(monthly_sales, x='Order Date', y='Sales', title='Monthly Sales')

        elif "monthly profits by year" in query:
            data['Order Date'] = pd.to_datetime(data['Order Date'])
            monthly_profits = data.groupby(data['Order Date'].dt.to_period("M"))['Profit'].sum().reset_index()
            monthly_profits['Order Date'] = monthly_profits['Order Date'].astype(str)
            response_text = "Monthly Profits by Year:"
            graph = px.line(monthly_profits, x='Order Date', y='Profit', title='Monthly Profits')

        elif "total sales & profit by state" in query:
            sales_profit_by_state = data.groupby('State').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
            response_text = "Total Sales & Profit by State:\n"
            for index, row in sales_profit_by_state.iterrows():
                response_text += f"{row['State']}: Sales = ${row['Sales']:,.2f}, Profit = ${row['Profit']:,.2f}\n"
            graph = px.bar(sales_profit_by_state, 
                           x='State', 
                           y=['Sales', 'Profit'], 
                           title='Total Sales & Profit by State',
                           labels={'value': 'Amount', 'variable': 'Metric'})

        else:
            response_text = "Sorry, I could not process that query. Please try asking in a different way."

    except Exception as e:
        response_text = f"An error occurred: {str(e)}"

    return response_text, graph

# Function for voice recognition
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio)
        st.success(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")

# Streamlit app code
st.set_page_config(layout='wide')
st.title("Chat with Your Data")
input_file = st.file_uploader("Upload your CSV or XLSX file", type=['csv', 'xlsx'])

if input_file is not None:
    data = pd.read_csv(input_file) if input_file.name.endswith('.csv') else pd.read_excel(input_file)
    st.success("File uploaded successfully!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Ask by Voice"):
            user_query = voice_input()
            if user_query:
                response_text, graph = process_query(user_query, data)
                st.success(response_text)

                if graph is not None:
                    st.plotly_chart(graph)
                else:
                    st.warning("No graph available for this query.")

    with col2:
        user_query_text = st.text_input("Or type your query:")
        if st.button("Send"):
            if user_query_text:
                response_text, graph = process_query(user_query_text, data)
                st.success(response_text)

                if graph is not None:
                    st.plotly_chart(graph)
                else:
                    st.warning("No graph available for this query.")
