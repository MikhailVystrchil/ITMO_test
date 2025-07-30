import pandas as pd

# Загрузка данных
df = pd.read_parquet('src/transaction_fraud_data.parquet')

# Расчет доли мошенничества по странам
country_stats = df.groupby('country')['is_fraud'].mean().reset_index()
country_stats.columns = ['country', 'fraud_rate']

# Список высокорисковых стран (≥20%)
high_risk_countries = country_stats[country_stats['fraud_rate'] >= 0.20]['country'].tolist()

# Разделение датасета
high_risk_df = df[df['country'].isin(high_risk_countries)]
low_risk_df = df[~df['country'].isin(high_risk_countries)]

# Сохранение
high_risk_df.to_parquet('high_risk_countries.parquet', index=False)
low_risk_df.to_parquet('low_risk_countries.parquet', index=False)

print(f'Сохранено:')
print(f'- high_risk_countries.parquet ({len(high_risk_df)} записей)')
print(f'- low_risk_countries.parquet ({len(low_risk_df)} записей)')
print(f'\nСписок высокорисковых стран (≥20% мошенничества):')
print(high_risk_countries)