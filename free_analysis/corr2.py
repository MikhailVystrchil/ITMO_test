import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Загрузка данных
df = pd.read_parquet('src/transaction_fraud_data.parquet')


# Определяем страны для первой группы
selected_countries = ['Brazil', 'Mexico', 'Nigeria', 'Russia']
df['country_group'] = np.where(
    df['country'].isin(selected_countries),
    'Brazil/Mexico/Nigeria/Russia',
    'Other countries'
)

# Вычисляем долю мошеннических транзакций
fraud_stats = (df.groupby(['vendor_category', 'country_group'])['is_fraud']
                .mean()
                .mul(100)
                .reset_index()
                .rename(columns={'is_fraud': 'fraud_percentage'}))

# Сортируем категории по общей доле мошенничества
category_order = (df.groupby('vendor_category')['is_fraud']
                  .mean()
                  .sort_values(ascending=False)
                  .index)

# Настройка стиля seaborn
sns.set_style("whitegrid")
plt.figure(figsize=(14, 8))

# Создаем barplot
ax = sns.barplot(
    data=fraud_stats,
    x='vendor_category',
    y='fraud_percentage',
    hue='country_group',
    order=category_order,
    palette=['#1f77b4', '#ff7f0e'],
    saturation=0.8
)

# Настройка внешнего вида
plt.title('Доля мошеннических транзакций по категориям\n(Сравнение групп стран)',
          fontsize=16, pad=20)
plt.xlabel('Категория транзакции', fontsize=12)
plt.ylabel('Доля мошенничества (%)', fontsize=12)
plt.xticks(rotation=45, ha='right')

# Добавляем аннотации
for p in ax.patches:
    ax.annotate(
        f'{p.get_height():.1f}%',
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='center',
        xytext=(0, 5),
        textcoords='offset points',
        fontsize=9
    )

# Улучшаем легенду
plt.legend(
    title='Группа стран',
    loc='upper right',
    frameon=True,
    shadow=True
)

# Добавляем общую информацию
total_fraud = df['is_fraud'].mean() * 100
plt.axhline(total_fraud, color='red', linestyle='--', alpha=0.7)
plt.text(
    x=0.95, y=total_fraud + 0.5,
    s=f'Средний уровень мошенничества: {total_fraud:.1f}%',
    ha='right', va='bottom',
    color='red',
    bbox=dict(facecolor='white', alpha=0.8)
)

plt.tight_layout()
plt.show()