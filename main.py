import pandas as pd

hce_df = pd.read_parquet('free_analysis/src/historical_currency_exchange.parquet', engine='pyarrow')
tfd_df = pd.read_parquet('free_analysis/src/transaction_fraud_data.parquet', engine='pyarrow')

print(hce_df)
print(tfd_df)