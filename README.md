# Inventory Demand Segmentation and Forecasting Dashboard
An interactive Streamlit dashboard for inventory management, featuring ABC segmentation of retail sales data and demand forecasting for key 'A' category items using the Prophet model. Designed to optimize stock levels and improve supply chain efficiency.

## How to Run

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Start the Streamlit app:
    ```bash
    streamlit run main.py
    ```
3.  Ensure your `Online Retail.xlsx` file is located at `J:/PROJECT I/Online Retail.xlsx` as the app directly loads it from this path.

## Features
- ABC segmentation of inventory items
- Interactive data exploration
- Demand forecasting for top 'A' items (using Prophet)

## To Do
- Enhance visualizations
- Add filtering by date or other fields
- Implement XYZ analysis for further segmentation
- Explore more advanced forecasting models (e.g., LSTM)
