# -*- coding: utf-8 -*-
"""
Модуль загрузки и сохранения справочников.

Содержит функции для чтения исходных данных из Excel,
хранения их в двоичном формате pickle и загрузки обратно.

Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
"""

from pathlib import Path
import pandas as pd


# Путь к исходному файлу Excel
SOURCE_FILE = "data/итоговая_база_данных.xlsx"

# Директория с pickle-файлами (двоичная БД)
DATA_DIR = Path("data")

# Список всех городов (справочник городов)
CITY_LIST = [
    "Bangkok",
    "Beijing",
    "Berlin",
    "Cairo",
    "Dubai",
    "Istanbul",
    "Johannesburg",
    "London",
    "LosAngeles",
    "Madrid",
    "MexicoCity",
    "Moscow",
    "Mumbai",
    "NewYork",
    "Paris",
    "RiodeJaneiro",
    "Seoul",
    "Sydney",
    "Tokyo",
    "Toronto"
]


def create_pickle_database() -> None:
    """
    Читает Excel-файл и создаёт pickle-файлы по каждому городу.

    Для каждого листа (города) добавляются столбцы City и Date.
    Файлы сохраняются в директорию data/.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    # Создаём директорию data/, если её нет
    DATA_DIR.mkdir(exist_ok=True)

    for city in CITY_LIST:
        # Читаем лист с именем города из Excel
        df = pd.read_excel(SOURCE_FILE, sheet_name=city)

        # Добавляем служебные столбцы
        df["City"] = city
        df["Date"] = pd.to_datetime(df["Date"])

        # Сохраняем в двоичный формат
        file_name = DATA_DIR / f"{city}.pckl"
        df.to_pickle(file_name)


def load_city(city_name: str) -> pd.DataFrame:
    """
    Загружает данные одного города из pickle-файла.

    Parameters
    ----------
    city_name : str
        Название города (должно совпадать с именем файла).

    Returns
    -------
    pd.DataFrame
        Таблица с данными города.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    file_name = DATA_DIR / f"{city_name}.pckl"
    return pd.read_pickle(file_name)


def save_city(df: pd.DataFrame, city_name: str) -> None:
    """
    Сохраняет DataFrame города обратно в pickle-файл.

    Parameters
    ----------
    df : pd.DataFrame
        Таблица с данными города.

    city_name : str
        Название города.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    file_name = DATA_DIR / f"{city_name}.pckl"
    df.to_pickle(file_name)


def load_all_data() -> pd.DataFrame:
    """
    Загружает и объединяет данные всех городов в одну таблицу.

    Returns
    -------
    pd.DataFrame
        Объединённая таблица по всем городам.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frames = []

    for city in CITY_LIST:
        frames.append(load_city(city))

    # Объединяем все города в одну таблицу
    return pd.concat(frames, ignore_index=True)


def get_city_list() -> list:
    """
    Возвращает список доступных городов.

    Returns
    -------
    list
        Список названий городов.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    return CITY_LIST.copy()
