from typing import Any
from mcp.server.fastmcp import FastMCP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime
import warnings

# Initialize FastMCP server
mcp = FastMCP("forecast")

# Constants
# NWS_API_BASE = "https://api.weather.gov"
# USER_AGENT = "weather-app/1.0"

@mcp.tool()
def forecast(sales_data: list[float], start_date: str, forecast_steps: int, growth_model: str) -> str:
    """
    Forecast future sales using Prophet for small datasets, returning Python code to plot results.
    """

    warnings.filterwarnings('ignore')
    class ProphetSalesForecast:
        def __init__(self):
            self.time_series = None
            self.prophet_model = None
            self.prophet_forecast = None
            self.report = {
                'data_exploration': {},
                'prophet': {},
                'best_model': {'name': 'Prophet', 'reason': 'Optimized for small datasets'}
            }
        def load_data_from_list(self, sales_data, start_date):
            start_date = pd.to_datetime(start_date)
            date_range = pd.date_range(start=start_date, periods=len(sales_data), freq='MS')
            self.time_series = pd.Series(sales_data, index=date_range)
            return self.time_series
        def quick_data_exploration(self, plot=True):
            time_series = self.time_series
            stats = time_series.describe()
            missing_values = time_series.isnull().sum()
            self.report['data_exploration'] = {
                'stats': stats.to_dict(),
                'missing_values': int(missing_values),
                'data_points': len(time_series)
            }
            return self.report['data_exploration']
        def preprocess_data(self, transform_method='log'):
            time_series = self.time_series
            if transform_method == 'log':
                transformed_data = np.log1p(time_series)
            elif transform_method == 'sqrt':
                transformed_data = np.sqrt(time_series)
            else:
                transformed_data = time_series
            return transformed_data
        def run_prophet_model(self, forecast_steps=12, growth='linear', seasonality_mode='additive'):
            time_series = self.time_series
            df_prophet = pd.DataFrame({
                'ds': time_series.index,
                'y': time_series.values
            })
            self.prophet_model = Prophet(
                growth=growth,
                seasonality_mode=seasonality_mode,
                yearly_seasonality='auto',
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                holidays_prior_scale=10.0,
                mcmc_samples=0,
                interval_width=0.95
            )
            if len(time_series) > 12:
                self.prophet_model.add_seasonality(
                    name='monthly',
                    period=30.5,
                    fourier_order=3
                )
            self.prophet_model.fit(df_prophet)
            freq = pd.infer_freq(time_series.index) or 'MS'
            future = self.prophet_model.make_future_dataframe(
                periods=forecast_steps,
                freq=freq,
                include_history=True
            )
            self.prophet_forecast = self.prophet_model.predict(future)
            historical = self.prophet_forecast[self.prophet_forecast['ds'] <= time_series.index.max()]
            mae = mean_absolute_error(time_series, historical['yhat'])
            rmse = np.sqrt(mean_squared_error(time_series, historical['yhat']))
            self.report['prophet'] = {
                'forecast_steps': int(forecast_steps),
                'forecast_mean': self.prophet_forecast['yhat'][-forecast_steps:].tolist(),
                'lower_95': self.prophet_forecast['yhat_lower'][-forecast_steps:].tolist(),
                'upper_95': self.prophet_forecast['yhat_upper'][-forecast_steps:].tolist(),
                'mae': float(mae),
                'rmse': float(rmse),
                'growth_model': growth,
                'seasonality_mode': seasonality_mode
            }
            return self.prophet_forecast
        def plot_forecast(self, title=None, figsize=(12, 6)):
            time_series = self.time_series
            forecast_dates = self.prophet_forecast['ds']
            forecast_values = self.prophet_forecast['yhat']
            lower_bound = self.prophet_forecast['yhat_lower']
            upper_bound = self.prophet_forecast['yhat_upper']
            history_mask = forecast_dates <= time_series.index.max()
            future_mask = forecast_dates > time_series.index.max()
            historical_dates = time_series.index.strftime('%Y-%m-%d').tolist()
            historical_values = time_series.values.tolist()
            forecast_dates_str = forecast_dates.dt.strftime('%Y-%m-%d').tolist()
            forecast_values_list = forecast_values.tolist()
            lower_bound_list = lower_bound.tolist()
            upper_bound_list = upper_bound.tolist()
            plot_code = f'''
# Forecast plot code
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
historical_dates = {historical_dates}
historical_values = {historical_values}
forecast_dates = {forecast_dates_str}
forecast_values = {forecast_values_list}
lower_bound = {lower_bound_list}
upper_bound = {upper_bound_list}
historical_dates = [datetime.strptime(date, "%Y-%m-%d") for date in historical_dates]
forecast_dates = [datetime.strptime(date, "%Y-%m-%d") for date in forecast_dates]
history_mask = [date <= max(historical_dates) for date in forecast_dates]
future_mask = [date > max(historical_dates) for date in forecast_dates]
history_dates = [forecast_dates[i] for i in range(len(forecast_dates)) if history_mask[i]]
history_values = [forecast_values[i] for i in range(len(forecast_values)) if history_mask[i]]
future_dates = [forecast_dates[i] for i in range(len(forecast_dates)) if future_mask[i]]
future_values = [forecast_values[i] for i in range(len(forecast_values)) if future_mask[i]]
plt.figure(figsize={figsize})
plt.plot(historical_dates, historical_values, 'b-', label='Historical Sales')
plt.plot(history_dates, history_values, 'g--', label='Model Fit')
plt.plot(future_dates, future_values, 'r--', label='Forecasted Sales')
plt.fill_between(forecast_dates, lower_bound, upper_bound, color='gray', alpha=0.2, label='95% Confidence Interval')
plt.title('{title or "Sales Forecast"}')
plt.xlabel('Date')
plt.ylabel('Sales Volume')
plt.legend()
plt.grid(True)
from matplotlib.ticker import ScalarFormatter
ax = plt.gca()
ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.show()
'''
            return plot_code
    forecast_system = ProphetSalesForecast()
    forecast_system.load_data_from_list(sales_data, start_date)
    forecast_system.quick_data_exploration()
    forecast_system.run_prophet_model(forecast_steps, growth=growth_model)
    plot_code = forecast_system.plot_forecast()
    return plot_code


def main() -> None:
    mcp.run(transport = "stdio")
