# -*- coding: utf-8 -*-
"""
Библиотека универсальных функций.

Содержит стандартные функции общего назначения,
которые могут использоваться в различных приложениях.

Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
"""

import configparser
import os
from pathlib import Path

import pandas as pd
import tkinter as tki
import tkinter.ttk as ttk
from tkinter import messagebox


# ==============================================================
# КОНФИГУРАЦИЯ
# ==============================================================

def load_config(path: str = "scripts/config.ini") -> configparser.ConfigParser:
    """
    Загружает конфигурационный файл .ini.

    Parameters
    ----------
    path : str
        Путь к конфигурационному файлу.

    Returns
    -------
    configparser.ConfigParser
        Объект конфигурации.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")
    return cfg


def save_config(cfg: configparser.ConfigParser,
                path: str = "scripts/config.ini") -> None:
    """
    Сохраняет конфигурационный файл .ini.

    Parameters
    ----------
    cfg : configparser.ConfigParser
        Объект конфигурации.

    path : str
        Путь к конфигурационному файлу.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    with open(path, "w", encoding="utf-8") as f:
        cfg.write(f)


# ==============================================================
# РАБОТА С ФАЙЛАМИ
# ==============================================================

def ensure_dirs(paths: list) -> None:
    """
    Создаёт директории, если они отсутствуют.

    Parameters
    ----------
    paths : list
        Список путей к директориям.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def save_dataframe_txt(df: pd.DataFrame, filepath: str) -> None:
    """
    Сохраняет DataFrame в текстовый файл.

    Parameters
    ----------
    df : pd.DataFrame
        Таблица для сохранения.

    filepath : str
        Путь к файлу.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(df.to_string(index=False))


def save_dataframe_excel(df: pd.DataFrame, filepath: str) -> None:
    """
    Сохраняет DataFrame в файл Excel.

    Parameters
    ----------
    df : pd.DataFrame
        Таблица для сохранения.

    filepath : str
        Путь к файлу.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    df.to_excel(filepath, index=False)


# ==============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ GUI
# ==============================================================

def rgb_to_hex(rgb: tuple) -> str:
    """
    Конвертирует RGB-кортеж в HEX-строку для Tkinter.

    Parameters
    ----------
    rgb : tuple
        Кортеж (R, G, B).

    Returns
    -------
    str
        Строка вида #RRGGBB.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    return "#%02x%02x%02x" % rgb


def make_label(parent, text: str, cfg: configparser.ConfigParser,
               font_size: int = None, **kwargs) -> tki.Label:
    """
    Создаёт стилизованный Label с цветами из конфига.

    Parameters
    ----------
    parent : tk widget
        Родительский контейнер.

    text : str
        Текст метки.

    cfg : configparser.ConfigParser
        Конфигурация приложения.

    font_size : int, optional
        Размер шрифта (если None — берётся из конфига).

    Returns
    -------
    tki.Label

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    size = font_size or cfg.getint("fonts", "size_normal")
    font = (
        cfg.get("fonts", "main"),
        size,
        cfg.get("fonts", "style_normal")
    )
    lbl = tki.Label(
        parent,
        text=text,
        font=font,
        bg=cfg.get("colors", "bg"),
        fg=cfg.get("colors", "fg"),
        **kwargs
    )
    return lbl


def make_button(parent, text: str, command,
                cfg: configparser.ConfigParser, **kwargs) -> tki.Button:
    """
    Создаёт стилизованную Button с цветами из конфига.

    Parameters
    ----------
    parent : tk widget
        Родительский контейнер.

    text : str
        Текст кнопки.

    command : callable
        Функция-обработчик нажатия.

    cfg : configparser.ConfigParser
        Конфигурация приложения.

    Returns
    -------
    tki.Button

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    font = (
        cfg.get("fonts", "main"),
        cfg.getint("fonts", "size_normal"),
        cfg.get("fonts", "style_normal")
    )
    btn = tki.Button(
        parent,
        text=text,
        command=command,
        font=font,
        bg=cfg.get("colors", "btn_bg"),
        fg=cfg.get("colors", "btn_fg"),
        relief="raised",
        cursor="hand2",
        **kwargs
    )
    return btn


def make_entry(parent, cfg: configparser.ConfigParser,
               width: int = 20, **kwargs) -> ttk.Entry:
    """
    Создаёт поле ввода Entry.

    Parameters
    ----------
    parent : tk widget
        Родительский контейнер.

    cfg : configparser.ConfigParser
        Конфигурация приложения.

    width : int
        Ширина поля.

    Returns
    -------
    ttk.Entry

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    ent = ttk.Entry(parent, width=width, **kwargs)
    return ent


def make_combobox(parent, values: list,
                  cfg: configparser.ConfigParser,
                  width: int = 20, **kwargs) -> ttk.Combobox:
    """
    Создаёт выпадающий список Combobox.

    Parameters
    ----------
    parent : tk widget
        Родительский контейнер.

    values : list
        Список значений.

    cfg : configparser.ConfigParser
        Конфигурация приложения.

    width : int
        Ширина виджета.

    Returns
    -------
    ttk.Combobox

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    cmb = ttk.Combobox(parent, values=values, width=width, state="readonly",
                       **kwargs)
    if values:
        cmb.current(0)
    return cmb


def make_scrolled_text(parent, cfg: configparser.ConfigParser,
                       width: int = 80, height: int = 20) -> tki.Text:
    """
    Создаёт текстовый виджет с полосой прокрутки.

    Parameters
    ----------
    parent : tk widget
        Родительский контейнер.

    cfg : configparser.ConfigParser
        Конфигурация приложения.

    width : int
        Ширина (символы).

    height : int
        Высота (строки).

    Returns
    -------
    tki.Text

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frame = tki.Frame(parent, bg=cfg.get("colors", "bg"))
    font = (
        "Courier",
        cfg.getint("fonts", "size_small"),
        "normal"
    )
    txt = tki.Text(
        frame,
        width=width,
        height=height,
        font=font,
        bg=cfg.get("colors", "entry_bg"),
        fg=cfg.get("colors", "fg"),
        wrap="none"
    )
    # Горизонтальная прокрутка
    scr_x = tki.Scrollbar(frame, orient="horizontal", command=txt.xview)
    txt.configure(xscrollcommand=scr_x.set)
    # Вертикальная прокрутка
    scr_y = tki.Scrollbar(frame, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=scr_y.set)

    txt.grid(row=0, column=0, sticky="nsew")
    scr_y.grid(row=0, column=1, sticky="ns")
    scr_x.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    return frame, txt


def show_info(title: str, message: str) -> None:
    """
    Показывает информационное сообщение.

    Parameters
    ----------
    title : str
        Заголовок.

    message : str
        Текст сообщения.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    messagebox.showinfo(title, message)


def show_error(title: str, message: str) -> None:
    """
    Показывает сообщение об ошибке.

    Parameters
    ----------
    title : str
        Заголовок.

    message : str
        Текст сообщения.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    messagebox.showerror(title, message)


def ask_yes_no(title: str, message: str) -> bool:
    """
    Показывает диалог да/нет.

    Parameters
    ----------
    title : str
        Заголовок.

    message : str
        Текст вопроса.

    Returns
    -------
    bool
        True если нажато «Да», иначе False.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    return messagebox.askyesno(title, message)
