import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
import logging

# Set up basic logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def forecast_item_demand(df: pd.DataFrame, item_code: str, date_column: str, value_column: str, periods: int = 30) -> tuple:
    """
    Forecast demand for a specific item using Prophet.

    Args:
        df (pd.DataFrame): DataFrame with sales data.
        item_code (str): The StockCode to forecast.
        date_column (str): Name of the date column in the DataFrame.
        value_column (str): Name of the value/quantity column in the DataFrame.
        periods (int): Number of future periods (days) to forecast.

    Returns:
        tuple: A tuple containing:
            - forecast_df (pd.DataFrame): DataFrame with forecast.
            - model (Prophet): Fitted Prophet model.
            - fig (plotly.graph_objs._figure.Figure): Plotly figure of the forecast.
            Returns (None, None, None) if forecasting fails or data is insufficient.
    """
    # Filter for the specific item
    item_df = df[df['StockCode'] == item_code].copy()

    # Ensure date_column is datetime
    item_df[date_column] = pd.to_datetime(item_df[date_column])

    # Aggregate daily demand
    daily = item_df.groupby(date_column)[value_column].sum().reset_index()
    daily = daily.rename(columns={date_column: 'ds', value_column: 'y'})

    # Prophet requires at least two data points to fit the model
    # For more reliable forecasts, more data is usually needed, especially for seasonality.
    if len(daily) < 2:
        logging.warning(f"Not enough data points ({len(daily)}) for item '{item_code}' to perform forecasting. Returning None.")
        # Debugging: Log what's being returned
        logging.info(f"Returning tuple of length 3: (None, None, None) due to insufficient data for {item_code}")
        return None, None, None

    try:
        # Initialize and fit Prophet model
        # seasonality_mode='multiplicative' is often good for retail data where seasonal
        # fluctuations increase with the overall sales volume.
        model = Prophet(
            seasonality_mode='multiplicative',
            yearly_seasonality=True,  # Enable yearly seasonality detection
            weekly_seasonality=True,  # Enable weekly seasonality detection
            daily_seasonality=False   # Disable daily seasonality unless intra-day patterns are significant
        )
        # You can uncomment and use model.add_country_holidays(country_name='UK')
        # if you want to include UK public holidays in the forecast,
        # but it requires the 'holidays' package to be installed.

        model.fit(daily) # Fit the model to the historical daily demand data

        # Create a DataFrame with future dates for which to make predictions
        future = model.make_future_dataframe(periods=periods)

        # Make predictions using the fitted model
        forecast = model.predict(future)

        # Generate a Plotly figure to visualize the forecast
        fig = plot_plotly(model, forecast)

        # Validate if plot_plotly returned a valid Plotly Figure object
        if not isinstance(fig, go.Figure):
            logging.error(f"plot_plotly did not return a valid Plotly Figure for item '{item_code}'. Type: {type(fig)}")
            # Debugging: Log what's being returned
            logging.info(f"Returning tuple of length 3: (None, None, None) due to invalid figure for {item_code}")
            return None, None, None

        fig.update_layout(
            title=f'Demand Forecast for {item_code} (Next {periods} Days)', # Dynamic title
            xaxis_title='Date',
            yaxis_title='Quantity',
            hovermode='x unified' # Allows hovering over the plot to see values across all traces
        )
        # Add a date range selector to the plot for easier navigation
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        # Debugging: Log what's being returned
        logging.info(f"Returning tuple of length 3: (forecast, model, fig) for {item_code}")
        return forecast, model, fig # Return the forecast DataFrame, the fitted model, and the Plotly figure

    except Exception as e:
        # Log the actual error for debugging
        logging.error(f"Error during Prophet forecasting for item '{item_code}': {e}")
        # Debugging: Log what's being returned
        logging.info(f"Returning tuple of length 3: (None, None, None) due to exception for {item_code}")
        # Return None values to ensure consistent unpacking in main.py
        return None, None, None
