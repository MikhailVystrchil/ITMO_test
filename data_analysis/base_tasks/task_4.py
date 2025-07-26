"""
Сколько транзакций в среднем совершает один клиент за час?
Округлите до 2 знаков после запятой вверх и напишите через точку, например 0.05

ПРОВЕРИТЬ!!!
"""

import pandas as pd
import math

# Загрузка данных
transactions = pd.read_parquet('../src/transaction_fraud_data.parquet')

# Добавляем столбец с часом
transactions['hour'] = transactions['timestamp'].dt.hour

# Группируем по клиенту и часу, считаем транзакции
trans_per_hour = transactions.groupby(['customer_id', 'hour'])['transaction_id'].count()

# Вычисляем среднее значение
avg_trans = trans_per_hour.mean()

# Округление вверх до 2 знаков
rounded_avg = math.ceil(avg_trans * 100) / 100

print(f"Среднее количество транзакций на клиента в час: {rounded_avg}")
