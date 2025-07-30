import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Настройки отображения
pd.set_option('display.max_rows', None)
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12

# 1. Загрузка данных
try:
    df = pd.read_parquet('src/transaction_fraud_data.parquet')
    print(f"Загружено {len(df)} транзакций. Пример данных:")
    print(df[['country', 'amount', 'is_fraud']].sample(3))
except Exception as e:
    print(f"Ошибка загрузки: {e}")
    exit()

# 2. Анализ мошенничества по странам
country_stats = df.groupby('country').agg(
    total_transactions=('is_fraud', 'count'),
    fraud_transactions=('is_fraud', 'sum'),
    avg_amount=('amount', 'mean')
).reset_index()

country_stats['fraud_rate'] = country_stats['fraud_transactions'] / country_stats['total_transactions']
country_stats['fraud_percentage'] = country_stats['fraud_rate'] * 100

# 3. Улучшенная классификация (5 классов)
def classify_fraud_rate(rate):
    if rate < 0.005:
        return 'Очень низкий (<0.5%)'
    elif 0.005 <= rate < 0.01:
        return 'Низкий (0.5-1%)'
    elif 0.01 <= rate < 0.03:
        return 'Умеренный (1-3%)'
    elif 0.03 <= rate < 0.07:
        return 'Высокий (3-7%)'
    else:
        return 'Очень высокий (>7%)'

country_stats['risk_category'] = country_stats['fraud_rate'].apply(classify_fraud_rate)

# 4. Расширенная визуализация
# Цветовая палитра для 5 категорий
palette = {
    'Очень низкий (<0.5%)': '#2ecc71',
    'Низкий (0.5-1%)': '#27ae60',
    'Умеренный (1-3%)': '#f39c12',
    'Высокий (3-7%)': '#e74c3c',
    'Очень высокий (>7%)': '#c0392b'
}

# График 1: Топ-20 стран с аннотациями
plt.figure(figsize=(16, 8))
top_countries = country_stats.nlargest(20, 'fraud_percentage')
ax = sns.barplot(data=top_countries, x='country', y='fraud_percentage',
                 hue='risk_category', palette=palette, dodge=False)

# Добавляем аннотации
for p in ax.patches:
    ax.annotate(f"{p.get_height():.2f}%",
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points')

plt.title('Доля мошеннических транзакций по странам (Топ-20)', pad=20, fontsize=16)
plt.xlabel('Страна', labelpad=15)
plt.ylabel('Доля мошенничества (%)', labelpad=15)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Уровень риска', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# График 2: Пузырьковая диаграмма (доля мошенничества vs объем транзакций)
plt.figure(figsize=(14, 8))
scatter = sns.scatterplot(data=country_stats, x='total_transactions', y='fraud_percentage',
                          hue='risk_category', size='avg_amount', sizes=(50, 300),
                          palette=palette, alpha=0.8)

# Выделяем опасные страны
threshold = country_stats['fraud_percentage'].quantile(0.9)
high_risk = country_stats[country_stats['fraud_percentage'] >= threshold]
for i, row in high_risk.iterrows():
    plt.text(row['total_transactions']*1.05, row['fraud_percentage'],
             row['country'], fontsize=10, va='center')

plt.title('Соотношение объема транзакций и доли мошенничества', pad=20, fontsize=16)
plt.xlabel('Общее количество транзакций (log scale)', labelpad=15)
plt.ylabel('Доля мошенничества (%)', labelpad=15)
plt.xscale('log')
plt.legend(title='Уровень риска', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 5. Анализ распределения
print("\nСтатистика по категориям риска:")
category_stats = country_stats.groupby('risk_category').agg(
    num_countries=('country', 'count'),
    avg_fraud_rate=('fraud_rate', 'mean'),
    median_transactions=('total_transactions', 'median')
).sort_values('avg_fraud_rate', ascending=False)
print(category_stats)

# 6. Сохранение результатов
output = country_stats.sort_values('fraud_percentage', ascending=False)
output.to_excel('detailed_country_fraud_analysis.xlsx', index=False)
print("\nРезультаты сохранены в 'detailed_country_fraud_analysis.xlsx'")
