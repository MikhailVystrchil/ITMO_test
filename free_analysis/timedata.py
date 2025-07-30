import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
df = pd.read_parquet('src/transaction_fraud_data.parquet')

# Извлечение даты и часа из timestamp
df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour

# Группировка по дате и категории вендора
grouped_data = df.groupby(['date', 'vendor_category']).size().unstack()

# Построение графика
plt.figure(figsize=(12, 6))
for category in grouped_data.columns:
    plt.plot(grouped_data.index, grouped_data[category], label=category)

plt.title('Распределение транзакций по типам от времени')
plt.xlabel('Дата')
plt.ylabel('Количество транзакций')
plt.legend(title='Категория вендора', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()