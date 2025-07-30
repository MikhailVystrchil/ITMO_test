import pandas as pd

# Загрузка данных
df = pd.read_parquet('src/transaction_fraud_data.parquet')

# Расчет mean и std для суммы транзакций
mean_amount = df['amount'].mean()
std_amount = df['amount'].std()

print(f"Математическое ожидание суммы транзакций: {mean_amount:.2f}")
print(f"Стандартное отклонение суммы транзакций: {std_amount:.2f}")