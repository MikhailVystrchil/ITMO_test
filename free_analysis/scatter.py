import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text

# Настройка компактного стиля
plt.style.use('seaborn-v0_8')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (16, 8)  # Уменьшенная высота
plt.rcParams['font.size'] = 9

# Загрузка и подготовка данных
# df = pd.read_parquet('src/transaction_fraud_data.parquet')
df = pd.read_parquet('src/high_risk_countries.parquet')
country_stats = df.groupby('country').agg(
    total_transactions=('is_fraud', 'count'),
    fraud_transactions=('is_fraud', 'sum'),
    avg_amount=('amount', 'mean')
).reset_index()
country_stats['fraud_rate'] = country_stats['fraud_transactions'] / country_stats['total_transactions'] * 100

# Создание компактного графика
fig, ax = plt.subplots(figsize=(16, 8))
scatter = sns.scatterplot(
    data=country_stats,
    x='total_transactions',
    y='fraud_rate',
    size='avg_amount',
    sizes=(40, 400),
    hue='fraud_rate',
    palette='viridis',
    alpha=0.8,
    ax=ax
)

# Настройка осей
ax.set_xscale('log')
ax.set_xlabel('Количество транзакций (log)', fontsize=10)
ax.set_ylabel('Доля мошенничества (%)', fontsize=10)
ax.set_title('Мошеннические операции по странам', fontsize=12, pad=15)

# Умное размещение подписей (только для значимых точек)
texts = []
for i, row in country_stats.iterrows():
    if row['fraud_rate'] > country_stats['fraud_rate'].median() or \
       row['total_transactions'] > country_stats['total_transactions'].median():
        texts.append(ax.text(
            row['total_transactions'],
            row['fraud_rate'],
            row['country'],
            fontsize=8,
            bbox=dict(facecolor='white', alpha=0.7, pad=1, edgecolor='none')
        ))

adjust_text(texts,
            arrowprops=dict(arrowstyle='-', color='gray', lw=0.3),
            expand_points=(1.1, 1.1),
            expand_text=(1.1, 1.1))

# Компактные легенды
handles, labels = scatter.get_legend_handles_labels()
scatter.legend_.remove()
plt.legend(handles[1:-1], labels[1:-1],
           title='Доля мошенничества (%)',
           bbox_to_anchor=(1.02, 1),
           borderaxespad=0)

# Сохранение в файл
plt.tight_layout()
plt.savefig('fraud_by_country.png', dpi=300, bbox_inches='tight')
plt.close()
print("График сохранен как 'fraud_by_country.png'")