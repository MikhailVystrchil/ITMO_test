"""
Какая доля всех транзакций — мошеннические?
Округлите до 1 знака после запятой вверх и напишите через точку, например 0.5
"""

import pandas as pd

# Загрузка данных
transactions = pd.read_parquet('../src/transaction_fraud_data.parquet')

# Расчет доли
total_transactions = len(transactions)
fraud_transactions = transactions['is_fraud'].sum()
fraud_ratio = fraud_transactions / total_transactions

# Округление вверх до 1 знака после запятой
import math
rounded_ratio = math.ceil(fraud_ratio * 10) / 10

print(f"Доля мошеннических транзакций: {rounded_ratio}")

print(total_transactions)
print(fraud_transactions)
print(fraud_ratio)
