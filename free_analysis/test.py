import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Загрузка данных
df = pd.read_parquet('src/transaction_fraud_data.parquet')


# Определяем интересующие нас подкатегории (можно настроить список)
subcategories = ['fast_food' 'gaming' 'physical' 'major' 'medical' 'online' 'hotels'
 'pharmacy' 'premium' 'events' 'supplies' 'airlines' 'local' 'booking'
 'streaming' 'transport' 'casual']

# Фильтруем только выбранные подкатегории, которые существуют в данных
existing_subcats = [sub for sub in subcategories if sub in df['vendor_type'].unique()]
df = df[df['vendor_type'].isin(existing_subcats)]

# Проверяем, есть ли данные после фильтрации
if df.empty:
    print("Нет данных после фильтрации. Проверьте названия подкатегорий.")
else:
    # Группировка стран
    selected_countries = ['Brazil', 'Mexico', 'Nigeria', 'Russia']
    df['country_group'] = np.where(
        df['country'].isin(selected_countries),
        'Brazil/Mexico/Nigeria/Russia',
        'Other countries'
    )

    # Вычисляем статистику мошенничества
    fraud_stats = (df.groupby(['vendor_category', 'vendor_type', 'country_group'])['is_fraud']
                   .mean()
                   .mul(100)
                   .reset_index()
                   .rename(columns={'is_fraud': 'fraud_percentage'}))

    # Получаем список существующих категорий после фильтрации
    existing_categories = fraud_stats['vendor_category'].unique()

    # Настройка стиля
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 8))
    palette = {'Brazil/Mexico/Nigeria/Russia': '#1f77b4', 'Other countries': '#ff7f0e'}

    # Создаем график только если есть данные
    if len(existing_categories) > 0:
        # Создаем FacetGrid с количеством строк, соответствующим количеству категорий
        g = sns.FacetGrid(fraud_stats, col='vendor_category',
                          col_wrap=min(3, len(existing_categories)),
                          height=4, aspect=1.2, sharey=True)

        # Рисуем столбчатые диаграммы
        g.map_dataframe(sns.barplot, x='vendor_type', y='fraud_percentage', hue='country_group',
                        palette=palette, order=existing_subcats, saturation=0.8)

        # Настройка внешнего вида
        g.set_titles("{col_name}")
        g.set_axis_labels("Подкатегория", "Доля мошенничества (%)")
        g.set_xticklabels(rotation=45, ha='right')
        g.add_legend(title='Группа стран')

        # Добавляем аннотации
        for ax in g.axes.flat:
            for p in ax.patches:
                height = p.get_height()
                if not np.isnan(height):
                    ax.annotate(
                        f'{height:.1f}%',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center',
                        xytext=(0, 5),
                        textcoords='offset points',
                        fontsize=8
                    )

        # Общий заголовок
        plt.subplots_adjust(top=0.9)
        g.fig.suptitle('Доля мошеннических транзакций по категориям и подкатегориям\n(Сравнение групп стран)',
                       fontsize=16)

        plt.tight_layout()
        plt.show()
    else:
        print("Нет данных для построения графиков. Проверьте фильтры.")