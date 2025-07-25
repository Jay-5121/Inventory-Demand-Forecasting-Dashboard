import streamlit as st
import pandas as pd
from src.abc_segmentation import abc_segmentation
from src.forecasting import forecast_item_demand
import plotly.express as px

st.set_page_config(layout="wide") # Use wide layout for better visualization

st.title('🛒 Inventory Segmentation and Forecasting Dashboard')

st.markdown("""
    This dashboard helps you analyze your inventory data, segment items using ABC analysis,
    and forecast future demand for selected items.
""")

# --- File Uploader for the Excel file ---
uploaded_file = st.file_uploader('Upload your Online Retail Excel file (e.g., "Online Retail.xlsx")', type=['xlsx'])

df = pd.DataFrame() # Initialize df to an empty DataFrame

if uploaded_file:
    try:
        # Read the Excel file from the uploader
        df = pd.read_excel(uploaded_file)

        # --- Initial Data Cleaning and Preparation ---
        # Ensure 'StockCode' is treated as a string to avoid type conversion issues with pyarrow
        df['StockCode'] = df['StockCode'].astype(str)

        # Ensure 'InvoiceDate' is datetime for time series analysis
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

        # Ensure 'Quantity' and 'UnitPrice' are numeric and handle potential errors
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')

        # Drop rows where Quantity or UnitPrice are NaN after coercion (e.g., non-numeric entries)
        # Also ensure InvoiceDate and StockCode are not NaN as they are critical for analysis
        df.dropna(subset=['Quantity', 'UnitPrice', 'InvoiceDate', 'StockCode'], inplace=True)

        # Filter out rows with negative or zero quantities/unit prices (returns/cancellations, free items)
        df = df[df['Quantity'] > 0]
        df = df[df['UnitPrice'] > 0]

        # Calculate TotalValue for ABC analysis
        df['TotalValue'] = df['Quantity'] * df['UnitPrice']

        st.subheader('1. Raw Data Preview')
        st.write(df.head())

        # --- ABC Segmentation Section ---
        st.subheader('2. Performing ABC Segmentation')
        abc_df = abc_segmentation(df, value_column='TotalValue', item_column='StockCode')

        st.write('### ABC Segmentation Results (Top 20 Items)')
        st.dataframe(abc_df.head(20))

        st.write('### ABC Category Distribution')
        category_counts = abc_df['ABC_Category'].value_counts().sort_index()
        fig_abc = px.bar(category_counts, x=category_counts.index, y=category_counts.values,
                         labels={'x': 'ABC Category', 'y': 'Number of Items'},
                         title='Distribution of Items by ABC Category')
        st.plotly_chart(fig_abc, use_container_width=True)

        st.subheader('3. Key Insights from ABC Analysis')
        total_revenue = abc_df['TotalValue'].sum()
        st.write(f"Total Revenue from Analyzed Items: **£{total_revenue:,.2f}**")

        for category in ['A', 'B', 'C']:
            cat_df = abc_df[abc_df['ABC_Category'] == category]
            num_items = len(cat_df)
            value_contribution = cat_df['TotalValue'].sum()
            percentage_value = (value_contribution / total_revenue) * 100
            st.markdown(f"**Category {category}:**")
            st.markdown(f"- Number of items: **{num_items}**")
            st.markdown(f"- Total value contribution: **£{value_contribution:,.2f}** ({percentage_value:,.2f}%)")
            st.markdown(f"- Percentage of total items: **{(num_items / len(abc_df)) * 100:,.2f}%**")

        st.info("Remember: 'A' items are high-value, 'B' are medium, and 'C' are low. Different management strategies are typically applied to each category.")

        # --- Demand Forecasting Section ---
        st.subheader('🔮 Demand Forecasting for Top A Items')

        # Get top A items for selection
        top_a_items = abc_df[abc_df['ABC_Category'] == 'A']['StockCode'].tolist()

        if not top_a_items:
            st.warning("No 'A' category items found for forecasting. Please check your data or ABC thresholds.")
        else:
            selected_item = st.selectbox('Select an A-category item to forecast:', top_a_items)
            forecast_periods = st.slider('Select forecast period (days into future):', 7, 365, 30)

            if st.button('Run Forecast'):
                with st.spinner(f'Generating forecast for {selected_item}...'):
                    forecast_df, model, fig = forecast_item_demand(
                        df,
                        item_code=selected_item,
                        date_column='InvoiceDate',
                        value_column='Quantity',
                        periods=forecast_periods
                    )

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        st.write(f"### Forecasted Demand for {selected_item} (Next {forecast_periods} Days)")
                        future_forecast = forecast_df[forecast_df['ds'] > df['InvoiceDate'].max()]
                        st.dataframe(future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
                    else:
                        st.warning(f"Not enough historical data or an issue occurred for item '{selected_item}' to generate a reliable forecast. Check terminal for details.")

    except Exception as e:
        st.error(f"An error occurred while processing the uploaded file: {e}")
        st.warning("Please ensure your Excel file has 'Quantity', 'UnitPrice', 'StockCode', and 'InvoiceDate' columns and is not corrupted.")
else:
    st.info('Please upload the Online Retail Excel file to get started.')


st.markdown("---")
st.markdown("Developed for Inventory Demand Segmentation and Forecasting Project")
