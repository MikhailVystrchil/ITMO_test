"""
Каково среднее для всех немошеннических операций при пересчете в доллары США?
Округлите ответ до целых значений вверх, например 105
"""

import pandas as pd
import math

# Загрузка данных
transactions = pd.read_parquet('../../free_analysis/src/transaction_fraud_data.parquet')
exchange_rates = pd.read_parquet('../../free_analysis/src/historical_currency_exchange.parquet')

# Фильтрация немошеннических операций
legit_trans = transactions[transactions['is_fraud'] == False]

# Добавляем дату для объединения
legit_trans['date'] = legit_trans['timestamp'].dt.date

# Объединяем с курсами валют
merged = legit_trans.merge(exchange_rates, on='date', how='left')

# Конвертация в USD (если валюта не USD)
merged['amount_usd'] = merged.apply(
    lambda row: row['amount'] / row[row['currency']] if row['currency'] != 'USD' else row['amount'],
    axis=1
)

# Расчет среднего и округление вверх
avg_amount_usd = merged['amount_usd'].mean()
rounded_avg = math.ceil(avg_amount_usd)

print(f"Средняя сумма немошеннических операций в USD: {rounded_avg}")
print(avg_amount_usd)
