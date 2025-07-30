"""
Какова доля мошенничества среди транзакций у продавцов с высоким риском (is_high_risk_vendor=True)?
Округлите до 1 знака после запятой вверх и напишите через точку, например 0.5
"""

import pandas as pd
import math

# Загрузка данных
transactions = pd.read_parquet('../../free_analysis/src/transaction_fraud_data.parquet')

# Фильтрация высокорисковых продавцов
high_risk_trans = transactions[transactions['is_high_risk_vendor']]

# Расчет доли
total_high_risk = len(high_risk_trans)
fraud_high_risk = high_risk_trans['is_fraud'].sum()
fraud_ratio = fraud_high_risk / total_high_risk

# Округление вверх
rounded_ratio = math.ceil(fraud_ratio * 10) / 10

print(f"Доля мошенничества среди high-risk вендоров: {rounded_ratio}")
