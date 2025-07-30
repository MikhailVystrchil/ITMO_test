"""
В каком городе выше всего средний чек по операциям, связанным с fast_food?
Для ответа напишите название города как в датасете.
"""

import pandas as pd

# Загрузка данных
transactions = pd.read_parquet('../../free_analysis/src/transaction_fraud_data.parquet')

# Фильтрация fast_food и исключение Unknown City
fast_food_trans = transactions[
    (transactions['vendor_type'] == 'fast_food') &
    (transactions['city'] != 'Unknown City')
]

# Расчет среднего чека по городам
avg_fast_food = fast_food_trans.groupby('city')['amount'].mean()

# Город с максимальным средним чеком
city_max_avg = avg_fast_food.idxmax()

print(f"Город с самым высоким средним чеком в fast_food: {city_max_avg}")
