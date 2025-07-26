"""
В каких топ-5 странах зафиксировано больше всего мошеннических транзакций?
Ответ должен быть в формате строки с перечислением стран через запятую без пробелов. Пример:
Brazil,UK,Japan,Australia,Nigeria
"""
import pandas as pd

# Загрузка данных
transactions = pd.read_parquet('../src/transaction_fraud_data.parquet')

# Фильтрация и подсчет
fraud_by_country = transactions[transactions['is_fraud']].groupby('country').size()
top_5_countries = fraud_by_country.sort_values(ascending=False).head(5).index.tolist()

# Форматирование ответа
result = ",".join(top_5_countries)
print(result)
print(fraud_by_country.sort_values(ascending=False))
