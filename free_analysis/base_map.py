import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors  # Правильный импорт модуля цветов
import numpy as np
import os
from urllib.request import urlretrieve


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


def load_transaction_data():
    try:
        transactions = pd.read_parquet("src/transaction_fraud_data.parquet")
        fraud_data = transactions[transactions['is_fraud']].groupby('country').agg(
            fraud_count=('transaction_id', 'count'),
            total_amount=('amount', 'sum')
        ).reset_index()
        return fraud_data
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def plot_fraud_map(world, fraud_data):
    merged = world.merge(
        fraud_data,
        left_on='NAME',
        right_on='country',
        how='left'
    )

    merged['fraud_count'] = merged['fraud_count'].fillna(0)
    merged['total_amount'] = merged['total_amount'].fillna(0)

    fig, ax = plt.subplots(figsize=(25, 15))

    # Логарифмические интервалы для большого диапазона
    bins = [0, 1, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 300000]
    colors = [
        '#f7f7f7', '#fee5d9', '#fcbba1', '#fc9272',
        '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15',
        '#7a0c12', '#50080c', '#300506', '#000000'
    ]

    # Создаем цветовую карту
    cmap = matplotlib.colors.ListedColormap(colors[1:])  # Пропускаем первый цвет (0)

    # Нормализация (используем BoundaryNorm вместо LogNorm для лучшего контроля)
    norm = matplotlib.colors.BoundaryNorm(bins[1:], cmap.N)  # Исключаем 0 из границ

    # Рисуем карту
    merged.plot(
        column='fraud_count',
        ax=ax,
        cmap=cmap,
        norm=norm,
        legend=False,
        edgecolor='black',
        linewidth=0.3,
        missing_kwds={'color': colors[0]}  # Серый для 0 операций
    )

    # Создаем кастомную легенду
    from matplotlib.patches import Patch
    legend_labels = [
        '0',
        '1-9',
        '10-49',
        '50-99',
        '100-499',
        '500-999',
        '1,000-4,999',
        '5,000-9,999',
        '10,000-49,999',
        '50,000-99,999',
        '100,000-299,999',
        '300,000+'
    ]

    legend_elements = [Patch(facecolor=colors[i], label=legend_labels[i])
                       for i in range(len(colors))]

    ax.legend(
        handles=legend_elements,
        title='Количество операций',
        loc='lower left',
        bbox_to_anchor=(0, 0),
        frameon=True,
        fontsize=10
    )

    # Добавляем подписи для топ-стран
    top_countries = merged.nlargest(15, 'fraud_count')
    for idx, row in top_countries.iterrows():
        if row['fraud_count'] > 0:
            centroid = row.geometry.centroid
            ax.annotate(
                text=f"{row['NAME']}\n{int(row['fraud_count']):,}",
                xy=(centroid.x, centroid.y),
                fontsize=10,
                ha='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
            )

    plt.title('Распределение мошеннических операций по странам', fontsize=18)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('fraud_map_corrected.png', dpi=300, bbox_inches='tight')
    plt.show()


def main():
    world = load_geodata()
    if world is None:
        return

    fraud_data = load_transaction_data()
    if fraud_data is None:
        return

    plot_fraud_map(world, fraud_data)


if __name__ == "__main__":
    main()