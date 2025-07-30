import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

try:
    # Загрузка данных с обработкой возможных ошибок
    try:
        df = pd.read_parquet('src/transaction_fraud_data.parquet')
    except Exception as e:
        raise Exception(f"Ошибка при загрузке файла: {str(e)}")

    # Проверка наличия необходимых колонок
    required_columns = ['vendor_category', 'is_fraud']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise Exception(f"Отсутствуют обязательные колонки: {missing_columns}")

    # 1. Расчет доли мошенничества по категориям вендоров
    fraud_rate_by_category = df.groupby('vendor_category')['is_fraud'].mean().sort_values(ascending=False)

    # Разделение категорий на две группы
    high_fraud_categories = fraud_rate_by_category[fraud_rate_by_category > 0.2].index.tolist()
    low_fraud_categories = fraud_rate_by_category[fraud_rate_by_category <= 0.2].index.tolist()

    # Создание колонки для группировки
    df['fraud_group'] = np.where(
        df['vendor_category'].isin(high_fraud_categories),
        'High Fraud (>20%)',
        'Low Fraud (≤20%)'
    )


    # 2. Функция для сравнения групп с обработкой ошибок
    def safe_compare_groups(df, column, plot=False):
        try:
            if column not in df.columns:
                print(f"Колонка '{column}' отсутствует в данных. Пропускаем.")
                return None

            comparison = df.groupby(['fraud_group', column])['is_fraud'].count().unstack().fillna(0)
            comparison_pct = comparison.div(comparison.sum(axis=1), axis=0) * 100

            if plot:
                try:
                    comparison_pct.T.plot(kind='bar', stacked=True, figsize=(10, 6))
                    plt.title(f'Распределение {column} по группам мошенничества')
                    plt.ylabel('Доля, %')
                    plt.xticks(rotation=45)
                    plt.show()
                except Exception as e:
                    print(f"Ошибка при построении графика для {column}: {str(e)}")

            return comparison_pct
        except Exception as e:
            print(f"Ошибка при анализе колонки {column}: {str(e)}")
            return None


    # Сравнение по категориям вендоров
    print("=" * 50)
    print("Доля операций по категориям вендоров:")
    print("=" * 50)
    vendor_category_comparison = safe_compare_groups(df, 'vendor_category', plot=True)
    if vendor_category_comparison is not None:
        print(vendor_category_comparison)

    # Сравнение по другим ключевым признакам
    features_to_compare = [
        'vendor_type', 'is_card_present', 'channel',
        'is_outside_home_country', 'is_high_risk_vendor', 'is_weekend'
    ]

    for feature in features_to_compare:
        print("\n" + "=" * 50)
        print(f"Сравнение по признаку '{feature}':")
        print("=" * 50)
        result = safe_compare_groups(df, feature, plot=True)
        if result is not None:
            print(result)

    # 3. Сравнение числовых признаков
    print("\n" + "=" * 50)
    print("Средние значения числовых признаков:")
    print("=" * 50)

    numeric_features = ['amount']
    # Добавляем поля из last_hour_activity, если они существуют
    if 'last_hour_activity.num_transactions' in df.columns:
        numeric_features.append('last_hour_activity.num_transactions')
    if 'last_hour_activity.total_amount' in df.columns:
        numeric_features.append('last_hour_activity.total_amount')

    try:
        numeric_comparison = df.groupby('fraud_group')[numeric_features].mean()
        print(numeric_comparison)

        # Визуализация числовых признаков
        for feature in numeric_features:
            try:
                plt.figure(figsize=(10, 6))
                df.boxplot(column=feature, by='fraud_group', vert=False)
                plt.title(f'Распределение {feature} по группам мошенничества')
                plt.suptitle('')
                plt.show()
            except Exception as e:
                print(f"Ошибка при построении boxplot для {feature}: {str(e)}")
    except Exception as e:
        print(f"Ошибка при анализе числовых признаков: {str(e)}")

    # 4. Дополнительный анализ
    print("\n" + "=" * 50)
    print("Дополнительная статистика:")
    print("=" * 50)
    try:
        print("\nРазмер групп:")
        print(df['fraud_group'].value_counts())

        print("\nОбщая доля мошенничества:")
        print(df['is_fraud'].mean())

        print("\nДоля мошенничества по группам:")
        print(df.groupby('fraud_group')['is_fraud'].mean())
    except Exception as e:
        print(f"Ошибка при выводе дополнительной статистики: {str(e)}")

except Exception as e:
    print(f"Критическая ошибка в выполнении скрипта: {str(e)}")
    exit(1)

print("\nАнализ успешно завершен!")
exit(0)