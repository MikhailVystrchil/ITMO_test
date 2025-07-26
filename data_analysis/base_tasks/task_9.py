"""
Каково среднее для всех мошеннических операций при пересчете в доллары США?
Округлите ответ до целых значений вверх, например 105
"""

import pandas as pd
import math

# Загрузка данных
transactions = pd.read_parquet('../src/transaction_fraud_data.parquet')
exchange_rates = pd.read_parquet('../src/historical_currency_exchange.parquet')

# Фильтрация мошеннических операций
fraud_trans = transactions[transactions['is_fraud'] == True].copy()

# Добавление даты и объединение с курсами
fraud_trans['date'] = fraud_trans['timestamp'].dt.date
merged = fraud_trans.merge(exchange_rates, on='date', how='left')

# Конвертация в USD
merged['amount_usd'] = merged.apply(
    lambda row: row['amount'] / row[row['currency']] if row['currency'] != 'USD' else row['amount'],
    axis=1
)

# Расчет среднего и округление
avg_usd = merged['amount_usd'].mean()
rounded_avg = math.ceil(avg_usd)

print(f"Средняя сумма мошеннических операций в USD: {rounded_avg}")
