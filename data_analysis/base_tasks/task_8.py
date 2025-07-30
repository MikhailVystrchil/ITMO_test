"""
Каково среднеквадратичное отклонение среди всех немошеннических операций при пересчете в доллары США?
Округлите ответ до целых значений вверх, например 105

ПРОВЕРИТЬ!
"""

import pandas as pd
import math

# Загрузка данных
transactions = pd.read_parquet('../../free_analysis/src/transaction_fraud_data.parquet')
exchange_rates = pd.read_parquet('../../free_analysis/src/historical_currency_exchange.parquet')

# Фильтрация немошеннических операций
legit_trans = transactions[transactions['is_fraud'] == False].copy()

# Добавление даты и объединение с курсами
legit_trans['date'] = legit_trans['timestamp'].dt.date
merged = legit_trans.merge(exchange_rates, on='date', how='left')

# Конвертация в USD
merged['amount_usd'] = merged.apply(
    lambda row: row['amount'] / row[row['currency']] if row['currency'] != 'USD' else row['amount'],
    axis=1
)

# Расчет стандартного отклонения и округление
std_usd = merged['amount_usd'].std()
rounded_std = math.ceil(std_usd)

print(f"Стандартное отклонение сумм в USD: {rounded_std}")
