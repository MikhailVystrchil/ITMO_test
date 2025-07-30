"""
Каково среднеквадратичное отклонение среди всех мошеннических операций при пересчете в доллары США?
Округлите ответ до целых значений вверх, например 105
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math

# Загрузка данных
transactions = pd.read_parquet('../../free_analysis/src/transaction_fraud_data.parquet')
exchange_rates = pd.read_parquet('../../free_analysis/src/historical_currency_exchange.parquet')

# Фильтрация мошеннических операций
fraud_trans = transactions[transactions['is_fraud']].copy()

# Добавление даты и объединение с курсами
fraud_trans['date'] = fraud_trans['timestamp'].dt.date
merged = fraud_trans.merge(exchange_rates, on='date', how='left')

# Конвертация в USD
merged['amount_usd'] = merged.apply(
    lambda row: row['amount'] / row[row['currency']] if row['currency'] != 'USD' else row['amount'],
    axis=1
)

# Настройка стиля графиков
sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))

# Построение гистограммы и KDE
ax = sns.histplot(merged['amount_usd'], bins=50, kde=True, color='crimson', alpha=0.7)
plt.title('Распределение сумм мошеннических операций (USD)', fontsize=14)
plt.xlabel('Сумма в USD', fontsize=12)
plt.ylabel('Количество операций', fontsize=12)

# Добавление линии среднего и аннотации
mean_val = merged['amount_usd'].mean()
plt.axvline(mean_val, color='navy', linestyle='--', linewidth=2)
plt.text(mean_val*1.05, ax.get_ylim()[1]*0.9,
         f'Среднее: ${mean_val:.2f}', color='navy', fontsize=12)

# Вывод стандартного отклонения (округленного вверх)
std_usd = math.ceil(merged['amount_usd'].std())
plt.text(mean_val*1.05, ax.get_ylim()[1]*0.8,
         f'Станд. отклонение: ${std_usd}', color='darkgreen', fontsize=12)

# Логарифмическая шкала (если данные сильно скошены)
plt.yscale('log')  # Раскомментируйте, если нужно

plt.tight_layout()
plt.show()
