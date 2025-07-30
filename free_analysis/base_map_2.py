import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np
import os
from urllib.request import urlretrieve


# 1. Загрузка геоданных
def load_geodata():
    os.makedirs('geodata', exist_ok=True)
    geofile = 'geodata/ne_110m_admin_0_countries.zip'

    if not os.path.exists(geofile):
        try:
            print("Скачиваем геоданные...")
            url = 'https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip'
            urlretrieve(url, geofile)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return None

    try:
        return gpd.read_file(geofile)
    except Exception as e:
        print(f"Ошибка чтения: {e}")
        return None


# 2. Загрузка и подготовка данных
def load_transaction_data():
    try:
        transactions = pd.read_parquet("src/transaction_fraud_data.parquet")

        # Считаем общее количество операций и мошеннических по странам
        country_stats = transactions.groupby('country').agg(
            total_count=('transaction_id', 'count'),
            fraud_count=('is_fraud', 'sum')
        ).reset_index()

        # Вычисляем долю мошеннических операций
        country_stats['fraud_ratio'] = country_stats['fraud_count'] / country_stats['total_count']

        return country_stats
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# 3. Построение карты с долями мошенничества
def plot_fraud_ratio_map(world, fraud_data):
    # Объединяем данные
    merged = world.merge(
        fraud_data,
        left_on='NAME',
        right_on='country',
        how='left'
    )

    # Заполняем пропуски
    merged['fraud_ratio'] = merged['fraud_ratio'].fillna(0)
    merged['total_count'] = merged['total_count'].fillna(0)
    merged['fraud_count'] = merged['fraud_count'].fillna(0)

    # Создаем фигуру
    fig, ax = plt.subplots(figsize=(25, 15))

    # Цветовая схема от белого (0%) до темно-красного (10%+)
    colors = ["#ffffff", "#fff5f0", "#fee0d2", "#fcbba1",
              "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d",
              "#a50f15", "#67000d"]

    # Границы интервалов (в долях)
    bins = [0, 0.0001, 0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 1.0]
    labels = [
        '0%',
        '0.01-0.1%',
        '0.1-0.5%',
        '0.5-1%',
        '1-2%',
        '2-3%',
        '3-5%',
        '5-7%',
        '7-10%',
        '>10%'
    ]

    # Создаем цветовую карту
    cmap = matplotlib.colors.ListedColormap(colors)
    norm = matplotlib.colors.BoundaryNorm(bins, cmap.N)

    # Рисуем карту
    merged.plot(
        column='fraud_ratio',
        ax=ax,
        cmap=cmap,
        norm=norm,
        legend=False,
        edgecolor='black',
        linewidth=0.3
    )

    # Создаем кастомную легенду
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colors[i], label=labels[i])
                       for i in range(len(labels))]

    ax.legend(
        handles=legend_elements,
        title='Доля мошеннических операций',
        loc='lower left',
        bbox_to_anchor=(0, 0),
        frameon=True,
        fontsize=10
    )

    # Добавляем подписи для стран с высокой долей мошенничества
    high_risk = merged.nlargest(15, 'fraud_ratio')
    for idx, row in high_risk.iterrows():
        if row['fraud_ratio'] > 0:
            centroid = row.geometry.centroid
            ax.annotate(
                text=f"{row['NAME']}\n{row['fraud_ratio'] * 100:.2f}%",
                xy=(centroid.x, centroid.y),
                fontsize=10,
                ha='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
            )

    plt.title('Доля мошеннических операций по странам (% от общего числа)', fontsize=18)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('fraud_ratio_map.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Выводим таблицу с результатами
    print("\nТоп-15 стран по доле мошеннических операций:")
    result_table = high_risk[['NAME', 'fraud_ratio', 'fraud_count', 'total_count']].copy()
    result_table['fraud_ratio'] = result_table['fraud_ratio'].apply(lambda x: f"{x * 100:.2f}%")
    result_table.columns = ['Страна', 'Доля мошенничества', 'Число мошеннических операций', 'Всего операций']
    print(result_table.reset_index(drop=True))


def main():
    # Загрузка данных
    world = load_geodata()
    if world is None:
        return

    fraud_data = load_transaction_data()
    if fraud_data is None:
        return

    # Построение карты
    plot_fraud_ratio_map(world, fraud_data)


if __name__ == "__main__":
    main()