# -*- coding: utf-8 -*-
"""
Модуль графических отчётов.

Содержит функции для построения и сохранения
визуальных аналитических отчётов с помощью Matplotlib.

Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


# Директория для сохранения графиков
GRAPHICS_DIR = Path("graphics")


def pm25_line_plot(df: pd.DataFrame, city: str,
                   save: bool = True) -> None:
    """
    Линейный график динамики PM2.5 для выбранного города.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    city : str
        Название города.

    save : bool
        Если True — сохраняет файл в папку graphics/.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Фильтрация по городу
    city_df = df[df["City"] == city].sort_values("Date")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(city_df["Date"], city_df["PM2.5"], linewidth=1.5)
    ax.set_title(f"Динамика PM2.5 — {city}", fontsize=14)
    ax.set_xlabel("Дата")
    ax.set_ylabel("PM2.5 (мкг/м³)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        GRAPHICS_DIR.mkdir(exist_ok=True)
        plt.savefig(GRAPHICS_DIR / f"{city}_pm25_line.png", dpi=150)

    plt.show()
    plt.close()


def temperature_pm25_scatter(df: pd.DataFrame,
                              city: str = None,
                              save: bool = True) -> None:
    """
    Категоризированная диаграмма рассеивания температуры и PM2.5.

    Если город указан — показывает только его данные.
    Иначе — все города, окрашенные по принадлежности.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    city : str, optional
        Название города для фильтрации.

    save : bool
        Если True — сохраняет файл в папку graphics/.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    if city:
        # Данные одного города
        sub = df[df["City"] == city]
        ax.scatter(sub["Temperature"], sub["PM2.5"], alpha=0.5, s=15)
        title = f"Температура и PM2.5 — {city}"
        filename = f"{city}_temp_pm25_scatter.png"
    else:
        # Все города — каждый цвет
        for c in df["City"].unique():
            sub = df[df["City"] == c]
            ax.scatter(sub["Temperature"], sub["PM2.5"],
                       alpha=0.4, s=10, label=c)
        ax.legend(loc="upper right", fontsize=7, ncol=2)
        title = "Температура и PM2.5 (все города)"
        filename = "all_temp_pm25_scatter.png"

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Температура (°C)")
    ax.set_ylabel("PM2.5 (мкг/м³)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        GRAPHICS_DIR.mkdir(exist_ok=True)
        plt.savefig(GRAPHICS_DIR / filename, dpi=150)

    plt.show()
    plt.close()


def pm25_boxplot(df: pd.DataFrame, save: bool = True) -> None:
    """
    Категоризированная диаграмма Бокса–Вискера PM2.5 по городам.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    save : bool
        Если True — сохраняет файл в папку graphics/.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    # Группируем данные по городам
    cities = df["City"].unique()
    data = [df.loc[df["City"] == c, "PM2.5"].dropna().values for c in cities]

    ax.boxplot(data, labels=cities, patch_artist=True)
    ax.set_title("Распределение PM2.5 по городам", fontsize=14)
    ax.set_xlabel("Город")
    ax.set_ylabel("PM2.5 (мкг/м³)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save:
        GRAPHICS_DIR.mkdir(exist_ok=True)
        plt.savefig(GRAPHICS_DIR / "pm25_boxplot.png", dpi=150)

    plt.show()
    plt.close()


def temperature_histogram(df: pd.DataFrame,
                           city: str = None,
                           bins: int = 20,
                           save: bool = True) -> None:
    """
    Категоризированная гистограмма распределения температуры.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    city : str, optional
        Если указан — строит гистограмму только для этого города.

    bins : int
        Количество бинов гистограммы.

    save : bool
        Если True — сохраняет файл в папку graphics/.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    if city:
        sub = df[df["City"] == city]
        ax.hist(sub["Temperature"], bins=bins, alpha=0.7, edgecolor="black")
        title = f"Распределение температуры — {city}"
        filename = f"{city}_temperature_hist.png"
    else:
        # Гистограммы для каждого города
        for c in df["City"].unique():
            sub = df[df["City"] == c]
            ax.hist(sub["Temperature"], bins=bins, alpha=0.3, label=c)
        ax.legend(fontsize=7, ncol=2)
        title = "Распределение температуры (все города)"
        filename = "all_temperature_hist.png"

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Температура (°C)")
    ax.set_ylabel("Количество наблюдений")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        GRAPHICS_DIR.mkdir(exist_ok=True)
        plt.savefig(GRAPHICS_DIR / filename, dpi=150)

    plt.show()
    plt.close()


def pollution_bar_chart(df: pd.DataFrame,
                         metric: str = "PM2.5",
                         save: bool = True) -> None:
    """
    Кластеризованная столбчатая диаграмма среднего загрязнения по городам.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная таблица.

    metric : str
        Показатель загрязнения: 'PM2.5', 'PM10' или 'NO2'.

    save : bool
        Если True — сохраняет файл в папку graphics/.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Среднее значение показателя по каждому городу
    avg = df.groupby("City")[metric].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(14, 6))

    # Кластеризованная столбчатая диаграмма
    ax.bar(avg.index, avg.values, color="steelblue", edgecolor="black")
    ax.set_title(f"Среднее {metric} по городам", fontsize=14)
    ax.set_xlabel("Город")
    ax.set_ylabel(f"{metric} (мкг/м³)")
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()

    if save:
        GRAPHICS_DIR.mkdir(exist_ok=True)
        plt.savefig(GRAPHICS_DIR / f"bar_{metric.replace('.', '')}.png", dpi=150)

    plt.show()
    plt.close()
