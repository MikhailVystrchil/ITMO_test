"""
В каком городе наибольшая средняя сумма транзакций?
Для ответа напишите название города как в датасете.
"""

import pandas as pd

# Загрузка данных
transactions = pd.read_parquet('../src/transaction_fraud_data.parquet')

# Фильтрация: исключаем 'Unknown City'
filtered_transactions = transactions[transactions['city'] != 'Unknown City']

# Расчет средней суммы по городам
avg_amount_by_city = filtered_transactions.groupby('city')['amount'].mean()

# Город с максимальной средней суммой
city_with_max_avg = avg_amount_by_city.idxmax()

print(f"Город с наибольшей средней суммой транзакций: {city_with_max_avg}")
