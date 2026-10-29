# -*- coding: utf-8 -*-
"""
Модуль текстовых отчётов.

Содержит функции для формирования аналитических
таблиц на основе загруженной базы данных.

Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
"""

import pandas as pd


def high_pm25_report(df: pd.DataFrame, min_pm25: float) -> pd.DataFrame:
    """
    Отчёт по записям с высоким уровнем PM2.5.

    Возвращает строки, где PM2.5 >= min_pm25,
    отсортированные по убыванию загрязнения.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная объединённая таблица.

    min_pm25 : float
        Минимальный порог PM2.5 для включения в отчёт.

    Returns
    -------
    pd.DataFrame
        Таблица отчёта.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Фильтрация по порогу PM2.5
    ind = df["PM2.5"] >= min_pm25

    cols = ["City", "Date", "PM2.5", "PM10", "Temperature"]

    report = df.loc[ind, cols]

    # Сортировка по убыванию загрязнения
    return report.sort_values(by="PM2.5", ascending=False).reset_index(drop=True)


def temperature_pollution_report(df: pd.DataFrame,
                                  min_temp: float,
                                  max_temp: float) -> pd.DataFrame:
    """
    Отчёт по загрязнению в заданном температурном диапазоне.

    Parameters
    ----------
    df : pd.DataFrame
        Общая таблица.

    min_temp : float
        Минимальная температура (включительно).

    max_temp : float
        Максимальная температура (включительно).

    Returns
    -------
    pd.DataFrame
        Итоговый отчёт.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Фильтрация по температурному диапазону
    ind = (df["Temperature"] >= min_temp) & (df["Temperature"] <= max_temp)

    cols = ["City", "Date", "Temperature", "PM2.5", "NO2", "CO"]

    return df.loc[ind, cols].reset_index(drop=True)


def climate_report(df: pd.DataFrame,
                   min_humidity: float,
                   min_wind: float) -> pd.DataFrame:
    """
    Отчёт по климатическим условиям (влажность и ветер).

    Parameters
    ----------
    df : pd.DataFrame
        Исходные данные.

    min_humidity : float
        Минимальная влажность (%).

    min_wind : float
        Минимальная скорость ветра (м/с).

    Returns
    -------
    pd.DataFrame
        Итоговый отчёт.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Фильтрация: влажность >= мин и скорость ветра >= мин
    ind = (df["Humidity"] >= min_humidity) & (df["Wind Speed"] >= min_wind)

    cols = ["City", "Date", "Humidity", "Wind Speed", "PM2.5", "PM10"]

    return df.loc[ind, cols].reset_index(drop=True)


def pivot_pollution_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Сводная таблица среднего загрязнения по городам.

    Строится с помощью pandas.pivot_table().
    Показывает средние значения PM2.5, PM10 и NO2 по каждому городу.

    Parameters
    ----------
    df : pd.DataFrame
        Общая таблица.

    Returns
    -------
    pd.DataFrame
        Сводная таблица (pivot table).

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Все числовые параметры для сводной таблицы
    all_values = ["PM2.5", "PM10", "NO2", "CO", "Temperature",
                  "Humidity", "Wind Speed"]
    existing = [v for v in all_values if v in df.columns]

    report = pd.pivot_table(
        df,
        values=existing,
        index="City",
        aggfunc="mean"
    )

    return report.round(2)


def statistics_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Статистический отчёт по числовым переменным.

    Возвращает таблицу с основными описательными статистиками:
    минимум, максимум, среднее, дисперсию и стандартное отклонение.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    Returns
    -------
    pd.DataFrame
        Таблица статистик (строки — переменные, столбцы — статистики).

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Числовые столбцы для анализа
    num_cols = ["PM2.5", "PM10", "NO2", "CO", "Temperature",
                "Humidity", "Wind Speed"]

    # Оставляем только те столбцы, которые есть в таблице
    existing = [c for c in num_cols if c in df.columns]

    stats = pd.DataFrame({
        "Переменная": existing,
        "Минимум": [df[c].min() for c in existing],
        "Максимум": [df[c].max() for c in existing],
        "Среднее": [df[c].mean() for c in existing],
    })

    return stats.round(3)


def frequency_report(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Таблица частот для качественной переменной (категориальной).

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    column : str
        Название качественного столбца.

    Returns
    -------
    pd.DataFrame
        Таблица частот: значение, количество, процент.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, "Количество"]
    total = counts["Количество"].sum()
    counts["Процент (%)"] = (counts["Количество"] / total * 100).round(2)

    return counts
