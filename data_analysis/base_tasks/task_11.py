"""
Определите, сколько клиентов демонстрируют потенциально опасное поведение: для каждого клиента возьмите медианное значение числа уникальных продавцов из показателя активности «за последний час» на момент транзакции и посчитайте, сколько клиентов строго превышают 95-ый квантиль от этого показателя.
В ответе напишите единственное целое число — количество таких клиентов.
"""

import pandas as pd
import numpy as np

# Загрузка данных
transactions = pd.read_parquet('../src/transaction_fraud_data.parquet')

# Извлечение количества уникальных продавцов за последний час
transactions['unique_merchants'] = transactions['last_hour_activity'].apply(lambda x: x['unique_merchants'])

# Расчет медианного значения unique_merchants для каждого клиента
median_per_customer = transactions.groupby('customer_id')['unique_merchants'].median()

# Вычисление 95-го квантиля по всем клиентам
quantile_95 = median_per_customer.quantile(0.95)

# Подсчет клиентов, чья медиана строго превышает квантиль
dangerous_customers = median_per_customer[median_per_customer > quantile_95].count()

print(f"Количество клиентов с опасным поведением: {dangerous_customers}")
