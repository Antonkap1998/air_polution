# -*- coding: utf-8 -*-
"""
Главный модуль информационно-аналитического приложения
«Анализ качества воздуха по городам мира».

Запуск: python scripts/main.py

Приложение предоставляет графический интерфейс для работы
с базой данных загрязнения воздуха, формирования текстовых
и графических аналитических отчётов.

Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
"""

import sys
import os

# Корень проекта — папка на уровень выше scripts/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Меняем рабочую директорию на корень проекта,
# чтобы все относительные пути (data/, output/ и т.д.) работали корректно
os.chdir(ROOT)

# Добавляем корень в путь поиска модулей (для library и scripts)
sys.path.insert(0, ROOT)

import tkinter as tki
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from pathlib import Path

import pandas as pd

# Импорт собственных модулей
from library.utils import (
    load_config, save_config,
    ensure_dirs,
    make_label, make_button, make_entry, make_combobox, make_scrolled_text,
    show_info, show_error, ask_yes_no
)
from scripts.loaders import (
    create_pickle_database, load_all_data,
    load_city, save_city, get_city_list
)
from scripts.text_reports import (
    high_pm25_report,
    temperature_pollution_report,
    climate_report,
    pivot_pollution_report,
    statistics_report,
    frequency_report
)
from scripts.graphic_reports import (
    pm25_line_plot,
    temperature_pm25_scatter,
    pm25_boxplot,
    temperature_histogram,
    pollution_bar_chart
)


# ==============================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ПРИЛОЖЕНИЯ
# ==============================================================

# Конфигурация (загружается один раз при старте)
CFG = load_config(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))

# База данных (загружается при старте)
DB = None


# ==============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ИНТЕРФЕЙСА
# ==============================================================

def apply_bg(widget) -> None:
    """
    Рекурсивно устанавливает цвет фона для виджета и его детей.

    Parameters
    ----------
    widget : tk widget
        Корневой виджет.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    bg = CFG.get("colors", "bg")
    try:
        widget.configure(bg=bg)
    except tki.TclError:
        pass
    for child in widget.winfo_children():
        apply_bg(child)


def styled_frame(parent) -> tki.Frame:
    """
    Создаёт Frame с цветом фона из конфига.

    Parameters
    ----------
    parent : tk widget
        Родительский контейнер.

    Returns
    -------
    tki.Frame

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    return tki.Frame(parent, bg=CFG.get("colors", "bg"))


def show_dataframe_in_text(txt_widget: tki.Text,
                            df: pd.DataFrame) -> None:
    """
    Выводит DataFrame в текстовый виджет.

    Parameters
    ----------
    txt_widget : tki.Text
        Текстовый виджет для отображения.

    df : pd.DataFrame
        Таблица для отображения.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    txt_widget.config(state="normal")
    txt_widget.delete("1.0", tki.END)
    txt_widget.insert(tki.END, df.to_string(index=False))
    txt_widget.config(state="disabled")


# ==============================================================
# ОКНО НАСТРОЕК
# ==============================================================

def open_settings_window(root: tki.Tk) -> None:
    """
    Открывает окно настройки интерфейса (цвета и шрифты).

    Parameters
    ----------
    root : tki.Tk
        Главное окно приложения.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    win = tki.Toplevel(root)
    win.title("Настройки интерфейса")
    win.geometry("450x350")
    win.configure(bg=CFG.get("colors", "bg"))
    win.resizable(False, False)

    frm = styled_frame(win)
    frm.pack(fill="both", expand=True, padx=15, pady=15)

    # --- Цвет фона ---
    make_label(frm, "Цвет фона (HEX):", CFG).grid(
        row=0, column=0, sticky="w", pady=4)
    ent_bg = make_entry(frm, CFG, width=18)
    ent_bg.insert(0, CFG.get("colors", "bg"))
    ent_bg.grid(row=0, column=1, sticky="w", pady=4, padx=8)

    # --- Цвет текста ---
    make_label(frm, "Цвет текста (HEX):", CFG).grid(
        row=1, column=0, sticky="w", pady=4)
    ent_fg = make_entry(frm, CFG, width=18)
    ent_fg.insert(0, CFG.get("colors", "fg"))
    ent_fg.grid(row=1, column=1, sticky="w", pady=4, padx=8)

    # --- Шрифт ---
    make_label(frm, "Шрифт:", CFG).grid(
        row=2, column=0, sticky="w", pady=4)
    fonts_list = ["Arial", "Times New Roman", "Courier", "Verdana", "Tahoma"]
    cmb_font = make_combobox(frm, fonts_list, CFG, width=16)
    cmb_font.set(CFG.get("fonts", "main"))
    cmb_font.grid(row=2, column=1, sticky="w", pady=4, padx=8)

    # --- Размер шрифта ---
    make_label(frm, "Размер шрифта:", CFG).grid(
        row=3, column=0, sticky="w", pady=4)
    ent_fsize = make_entry(frm, CFG, width=18)
    ent_fsize.insert(0, CFG.get("fonts", "size_normal"))
    ent_fsize.grid(row=3, column=1, sticky="w", pady=4, padx=8)

    def apply_settings():
        """
        Применяет и сохраняет введённые настройки.
        """
        CFG.set("colors", "bg", ent_bg.get().strip())
        CFG.set("colors", "fg", ent_fg.get().strip())
        CFG.set("colors", "btn_bg", ent_bg.get().strip())
        CFG.set("colors", "btn_fg", ent_fg.get().strip())
        CFG.set("fonts", "main", cmb_font.get())
        CFG.set("fonts", "size_normal", ent_fsize.get().strip())

        # Сохраняем конфиг в файл
        save_config(CFG, os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))
        show_info("Настройки", "Настройки сохранены.\nПерезапустите приложение для полного применения.")
        win.destroy()

    make_button(frm, "Применить и сохранить", apply_settings, CFG).grid(
        row=5, column=0, columnspan=2, pady=16)


# ==============================================================
# ОКНО УПРАВЛЕНИЯ СПРАВОЧНИКОМ ГОРОДОВ
# ==============================================================

def open_city_manager(root: tki.Tk) -> None:
    """
    Открывает окно управления справочником городов.

    Позволяет просматривать список городов и удалять города из БД.

    Parameters
    ----------
    root : tki.Tk
        Главное окно приложения.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    global DB

    win = tki.Toplevel(root)
    win.title("Справочник городов")
    win.geometry("500x480")
    win.configure(bg=CFG.get("colors", "bg"))

    frm = styled_frame(win)
    frm.pack(fill="both", expand=True, padx=15, pady=10)

    make_label(frm, "Справочник городов", CFG,
               font_size=CFG.getint("fonts", "size_header")).pack(pady=(0, 8))

    # Список городов
    lb_frame = styled_frame(frm)
    lb_frame.pack(fill="both", expand=True)

    scrollbar = tki.Scrollbar(lb_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tki.Listbox(
        lb_frame,
        yscrollcommand=scrollbar.set,
        font=(CFG.get("fonts", "main"), CFG.getint("fonts", "size_normal")),
        bg=CFG.get("colors", "entry_bg"),
        fg=CFG.get("colors", "fg"),
        selectbackground=CFG.get("colors", "btn_bg"),
        height=15
    )
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    # Заполнение списка
    for city in get_city_list():
        listbox.insert(tki.END, city)

    # Счётчик записей
    lbl_count = make_label(frm, "", CFG)
    lbl_count.pack(pady=4)

    def on_select(event):
        """
        Показывает количество записей выбранного города.
        """
        sel = listbox.curselection()
        if sel:
            city = listbox.get(sel[0])
            city_df = DB[DB["City"] == city]
            lbl_count.config(text=f"Записей в базе: {len(city_df)}")

    listbox.bind("<<ListboxSelect>>", on_select)

    # Кнопки управления
    btn_frm = styled_frame(frm)
    btn_frm.pack(pady=8)

    def delete_city():
        """
        Удаляет все записи выбранного города из БД (в памяти).
        """
        global DB
        sel = listbox.curselection()
        if not sel:
            show_error("Ошибка", "Выберите город из списка")
            return
        city = listbox.get(sel[0])
        if ask_yes_no("Удаление", f"Удалить все записи города {city}?"):
            DB = DB[DB["City"] != city]
            listbox.delete(sel[0])
            lbl_count.config(text="Записи удалены (только в памяти)")

    make_button(btn_frm, "Удалить записи города", delete_city, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_frm, "Закрыть", win.destroy, CFG).grid(
        row=0, column=1, padx=6)


# ==============================================================
# ОКНО УПРАВЛЕНИЯ ЗАПИСЯМИ (CRUD)
# ==============================================================

def open_data_editor(root: tki.Tk) -> None:
    """
    Открывает окно просмотра и редактирования записей БД.

    Позволяет добавлять и удалять записи по городу.

    Parameters
    ----------
    root : tki.Tk
        Главное окно приложения.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    global DB

    win = tki.Toplevel(root)
    win.title("Редактор данных")
    win.geometry("900x560")
    win.configure(bg=CFG.get("colors", "bg"))

    frm = styled_frame(win)
    frm.pack(fill="both", expand=True, padx=12, pady=10)

    # --- Выбор города ---
    top_row = styled_frame(frm)
    top_row.pack(fill="x", pady=(0, 8))

    make_label(top_row, "Город:", CFG).pack(side="left", padx=(0, 6))
    cmb_city = make_combobox(top_row, get_city_list(), CFG, width=18)
    cmb_city.pack(side="left")

    make_button(top_row, "Загрузить", lambda: load_table(), CFG).pack(
        side="left", padx=8)

    # --- Таблица данных (Treeview) ---
    tree_frame = styled_frame(frm)
    tree_frame.pack(fill="both", expand=True)

    columns = ("Date", "PM2.5", "PM10", "NO2", "CO",
                "Temperature", "Humidity", "Wind Speed")

    tree = ttk.Treeview(tree_frame, columns=columns,
                        show="headings", height=14)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=90, anchor="center")

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    # --- Поля для добавления новой записи ---
    add_frame = styled_frame(frm)
    add_frame.pack(fill="x", pady=8)

    make_label(add_frame, "Добавить запись:", CFG).grid(
        row=0, column=0, columnspan=8, sticky="w", pady=(0, 4))

    field_labels = ["Дата (ГГГГ-ММ-ДД)", "PM2.5", "PM10",
                    "NO2", "CO", "Темп.", "Влажн.", "Ветер"]
    entries = []
    for i, lbl_text in enumerate(field_labels):
        make_label(add_frame, lbl_text, CFG,
                   font_size=8).grid(row=1, column=i, padx=2)
        ent = make_entry(add_frame, CFG, width=10)
        ent.grid(row=2, column=i, padx=2)
        entries.append(ent)

    def load_table():
        """
        Загружает записи выбранного города в таблицу.
        """
        city = cmb_city.get()
        city_df = DB[DB["City"] == city].sort_values("Date")
        # Очищаем таблицу
        for row in tree.get_children():
            tree.delete(row)
        # Заполняем
        for _, row in city_df.iterrows():
            tree.insert("", tki.END, values=(
                str(row.get("Date", ""))[:10],
                row.get("PM2.5", ""),
                row.get("PM10", ""),
                row.get("NO2", ""),
                row.get("CO", ""),
                row.get("Temperature", ""),
                row.get("Humidity", ""),
                row.get("Wind Speed", "")
            ))

    def add_record():
        """
        Добавляет новую запись в БД (в памяти).
        """
        global DB
        city = cmb_city.get()
        vals = [e.get().strip() for e in entries]
        if not vals[0]:
            show_error("Ошибка", "Введите дату")
            return
        try:
            new_row = {
                "City": city,
                "Date": pd.to_datetime(vals[0]),
                "PM2.5": float(vals[1]) if vals[1] else None,
                "PM10": float(vals[2]) if vals[2] else None,
                "NO2": float(vals[3]) if vals[3] else None,
                "CO": float(vals[4]) if vals[4] else None,
                "Temperature": float(vals[5]) if vals[5] else None,
                "Humidity": float(vals[6]) if vals[6] else None,
                "Wind Speed": float(vals[7]) if vals[7] else None,
            }
            DB = pd.concat([DB, pd.DataFrame([new_row])], ignore_index=True)
            load_table()
            for e in entries:
                e.delete(0, tki.END)
        except ValueError as err:
            show_error("Ошибка ввода", str(err))

    def delete_record():
        """
        Удаляет выделенную запись из БД (в памяти).
        """
        global DB
        sel = tree.selection()
        if not sel:
            show_error("Ошибка", "Выберите запись для удаления")
            return
        city = cmb_city.get()
        item = tree.item(sel[0])["values"]
        date_val = pd.to_datetime(item[0])
        # Удаляем по городу и дате
        mask = ~((DB["City"] == city) & (DB["Date"].dt.date == date_val.date()))
        DB = DB[mask].reset_index(drop=True)
        load_table()

    def save_to_file():
        """
        Сохраняет текущие данные города в pickle-файл.
        """
        city = cmb_city.get()
        city_df = DB[DB["City"] == city]
        save_city(city_df, city)
        show_info("Сохранение", f"Данные города {city} сохранены в data/{city}.pckl")

    # Кнопки
    btn_row = styled_frame(frm)
    btn_row.pack(pady=4)

    make_button(btn_row, "Добавить запись", add_record, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_row, "Удалить запись", delete_record, CFG).grid(
        row=0, column=1, padx=6)
    make_button(btn_row, "Сохранить в файл", save_to_file, CFG).grid(
        row=0, column=2, padx=6)
    make_button(btn_row, "Закрыть", win.destroy, CFG).grid(
        row=0, column=3, padx=6)


# ==============================================================
# ТЕКСТОВЫЕ ОТЧЁТЫ — ВКЛАДКИ
# ==============================================================

def build_tab_report1(tab: tki.Frame) -> None:
    """
    Строит интерфейс вкладки «Высокий PM2.5».

    Parameters
    ----------
    tab : tki.Frame
        Родительская вкладка Notebook.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frm = styled_frame(tab)
    frm.pack(fill="both", expand=True, padx=12, pady=8)

    # --- Параметры ---
    ctrl = styled_frame(frm)
    ctrl.pack(fill="x")

    make_label(ctrl, "Мин. PM2.5 (мкг/м³):", CFG).grid(
        row=0, column=0, sticky="w", padx=(0, 6))
    ent_thresh = make_entry(ctrl, CFG, width=10)
    ent_thresh.insert(0, "120")
    ent_thresh.grid(row=0, column=1)

    # --- Область вывода ---
    txt_frame, txt = make_scrolled_text(frm, CFG, width=95, height=22)
    txt_frame.pack(fill="both", expand=True, pady=8)

    last_report = [None]

    def generate():
        """
        Формирует отчёт и выводит его в текстовый виджет.
        """
        try:
            thresh = float(ent_thresh.get())
        except ValueError:
            show_error("Ошибка", "Введите числовое значение")
            return
        report = high_pm25_report(DB, thresh)
        last_report[0] = report
        show_dataframe_in_text(txt, report)

    def save_report():
        """
        Сохраняет сформированный отчёт в файл.
        """
        if last_report[0] is None:
            show_error("Ошибка", "Сначала сформируйте отчёт")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Excel", "*.xlsx")],
            initialdir="output"
        )
        if path:
            if path.endswith(".xlsx"):
                last_report[0].to_excel(path, index=False)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(last_report[0].to_string(index=False))
            show_info("Сохранение", f"Отчёт сохранён:\n{path}")

    btn_row = styled_frame(frm)
    btn_row.pack()
    make_button(btn_row, "Сформировать", generate, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_row, "Сохранить", save_report, CFG).grid(
        row=0, column=1, padx=6)


def build_tab_report2(tab: tki.Frame) -> None:
    """
    Строит интерфейс вкладки «Температура».

    Parameters
    ----------
    tab : tki.Frame
        Родительская вкладка Notebook.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frm = styled_frame(tab)
    frm.pack(fill="both", expand=True, padx=12, pady=8)

    ctrl = styled_frame(frm)
    ctrl.pack(fill="x")

    make_label(ctrl, "Мин. темп. (°C):", CFG).grid(
        row=0, column=0, sticky="w")
    ent_min = make_entry(ctrl, CFG, width=8)
    ent_min.insert(0, "10")
    ent_min.grid(row=0, column=1, padx=4)

    make_label(ctrl, "Макс. темп. (°C):", CFG).grid(
        row=0, column=2, sticky="w", padx=(12, 0))
    ent_max = make_entry(ctrl, CFG, width=8)
    ent_max.insert(0, "30")
    ent_max.grid(row=0, column=3, padx=4)

    txt_frame, txt = make_scrolled_text(frm, CFG, width=95, height=22)
    txt_frame.pack(fill="both", expand=True, pady=8)

    last_report = [None]

    def generate():
        """
        Формирует отчёт по температурному диапазону.
        """
        try:
            mn = float(ent_min.get())
            mx = float(ent_max.get())
        except ValueError:
            show_error("Ошибка", "Введите числовые значения")
            return
        report = temperature_pollution_report(DB, mn, mx)
        last_report[0] = report
        show_dataframe_in_text(txt, report)

    def save_report():
        """
        Сохраняет сформированный отчёт в файл.
        """
        if last_report[0] is None:
            show_error("Ошибка", "Сначала сформируйте отчёт")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Excel", "*.xlsx")],
            initialdir="output"
        )
        if path:
            if path.endswith(".xlsx"):
                last_report[0].to_excel(path, index=False)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(last_report[0].to_string(index=False))
            show_info("Сохранение", f"Отчёт сохранён:\n{path}")

    btn_row = styled_frame(frm)
    btn_row.pack()
    make_button(btn_row, "Сформировать", generate, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_row, "Сохранить", save_report, CFG).grid(
        row=0, column=1, padx=6)


def build_tab_report3(tab: tki.Frame) -> None:
    """
    Строит интерфейс вкладки «Климат (влажность и ветер)».

    Parameters
    ----------
    tab : tki.Frame
        Родительская вкладка Notebook.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frm = styled_frame(tab)
    frm.pack(fill="both", expand=True, padx=12, pady=8)

    ctrl = styled_frame(frm)
    ctrl.pack(fill="x")

    make_label(ctrl, "Мин. влажность (%):", CFG).grid(
        row=0, column=0, sticky="w")
    ent_hum = make_entry(ctrl, CFG, width=8)
    ent_hum.insert(0, "70")
    ent_hum.grid(row=0, column=1, padx=4)

    make_label(ctrl, "Мин. скорость ветра (м/с):", CFG).grid(
        row=0, column=2, sticky="w", padx=(12, 0))
    ent_wind = make_entry(ctrl, CFG, width=8)
    ent_wind.insert(0, "3")
    ent_wind.grid(row=0, column=3, padx=4)

    txt_frame, txt = make_scrolled_text(frm, CFG, width=95, height=22)
    txt_frame.pack(fill="both", expand=True, pady=8)

    last_report = [None]

    def generate():
        """
        Формирует климатический отчёт.
        """
        try:
            hum = float(ent_hum.get())
            wind = float(ent_wind.get())
        except ValueError:
            show_error("Ошибка", "Введите числовые значения")
            return
        report = climate_report(DB, hum, wind)
        last_report[0] = report
        show_dataframe_in_text(txt, report)

    def save_report():
        """
        Сохраняет сформированный отчёт в файл.
        """
        if last_report[0] is None:
            show_error("Ошибка", "Сначала сформируйте отчёт")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Excel", "*.xlsx")],
            initialdir="output"
        )
        if path:
            if path.endswith(".xlsx"):
                last_report[0].to_excel(path, index=False)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(last_report[0].to_string(index=False))
            show_info("Сохранение", f"Отчёт сохранён:\n{path}")

    btn_row = styled_frame(frm)
    btn_row.pack()
    make_button(btn_row, "Сформировать", generate, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_row, "Сохранить", save_report, CFG).grid(
        row=0, column=1, padx=6)


def build_tab_report4(tab: tki.Frame) -> None:
    """
    Строит интерфейс вкладки «Сводная таблица».

    Parameters
    ----------
    tab : tki.Frame
        Родительская вкладка Notebook.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frm = styled_frame(tab)
    frm.pack(fill="both", expand=True, padx=12, pady=8)

    make_label(frm, "Средние показатели по всем параметрам", CFG,
               font_size=12).pack(pady=(0, 8))

    txt_frame, txt = make_scrolled_text(frm, CFG, width=60, height=24)
    txt_frame.pack(fill="both", expand=True, pady=8)

    last_report = [None]

    def generate():
        """
        Формирует сводную таблицу.
        """
        report = pivot_pollution_report(DB)
        last_report[0] = report
        txt.config(state="normal")
        txt.delete("1.0", tki.END)
        txt.insert(tki.END, report.to_string())
        txt.config(state="disabled")

    def save_report():
        """
        Сохраняет сводную таблицу в файл.
        """
        if last_report[0] is None:
            show_error("Ошибка", "Сначала сформируйте отчёт")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Excel", "*.xlsx")],
            initialdir="output"
        )
        if path:
            if path.endswith(".xlsx"):
                last_report[0].to_excel(path)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(last_report[0].to_string())
            show_info("Сохранение", f"Отчёт сохранён:\n{path}")

    btn_row = styled_frame(frm)
    btn_row.pack()
    make_button(btn_row, "Сформировать", generate, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_row, "Сохранить", save_report, CFG).grid(
        row=0, column=1, padx=6)


def build_tab_report5(tab: tki.Frame) -> None:
    """
    Строит интерфейс вкладки «Статистика».

    Включает описательную статистику числовых переменных
    и таблицу частот для качественной переменной «Город».

    Parameters
    ----------
    tab : tki.Frame
        Родительская вкладка Notebook.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frm = styled_frame(tab)
    frm.pack(fill="both", expand=True, padx=12, pady=8)

    # Радиокнопки выбора типа статистики
    sel = tki.IntVar()
    sel.set(0)

    radio_frm = styled_frame(frm)
    radio_frm.pack(fill="x")

    make_label(radio_frm, "Тип отчёта:", CFG).grid(
        row=0, column=0, sticky="w", padx=(0, 10))

    rad1 = ttk.Radiobutton(radio_frm, text="Числовые переменные",
                            value=0, variable=sel)
    rad1.grid(row=0, column=1, padx=6)

    rad2 = ttk.Radiobutton(radio_frm, text="Таблица частот (города)",
                            value=1, variable=sel)
    rad2.grid(row=0, column=2, padx=6)

    txt_frame, txt = make_scrolled_text(frm, CFG, width=80, height=22)
    txt_frame.pack(fill="both", expand=True, pady=8)

    last_report = [None]

    def generate():
        """
        Формирует статистический отчёт в зависимости от выбора.
        """
        if sel.get() == 0:
            report = statistics_report(DB)
        else:
            report = frequency_report(DB, "City")
        last_report[0] = report
        show_dataframe_in_text(txt, report)

    def save_report():
        """
        Сохраняет сформированный отчёт в файл.
        """
        if last_report[0] is None:
            show_error("Ошибка", "Сначала сформируйте отчёт")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Excel", "*.xlsx")],
            initialdir="output"
        )
        if path:
            if path.endswith(".xlsx"):
                last_report[0].to_excel(path, index=False)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(last_report[0].to_string(index=False))
            show_info("Сохранение", f"Отчёт сохранён:\n{path}")

    btn_row = styled_frame(frm)
    btn_row.pack()
    make_button(btn_row, "Сформировать", generate, CFG).grid(
        row=0, column=0, padx=6)
    make_button(btn_row, "Сохранить", save_report, CFG).grid(
        row=0, column=1, padx=6)


# ==============================================================
# ГРАФИЧЕСКИЕ ОТЧЁТЫ — ВКЛАДКА
# ==============================================================

def build_tab_graphics(tab: tki.Frame) -> None:
    """
    Строит интерфейс вкладки «Графические отчёты».

    Позволяет строить и сохранять все виды графиков.

    Parameters
    ----------
    tab : tki.Frame
        Родительская вкладка Notebook.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    frm = styled_frame(tab)
    frm.pack(fill="both", expand=True, padx=12, pady=8)

    make_label(frm, "Графические отчёты", CFG,
               font_size=CFG.getint("fonts", "size_header")).pack(pady=(0, 10))

    # ---- Линейный график PM2.5 ----
    sec1 = styled_frame(frm)
    sec1.pack(fill="x", pady=4)

    make_label(sec1, "Линейный график PM2.5 — Город:", CFG).grid(
        row=0, column=0, sticky="w")
    cmb_city1 = make_combobox(sec1, get_city_list(), CFG, width=14)
    cmb_city1.grid(row=0, column=1, padx=6)

    chk_save1_var = tki.BooleanVar(value=True)
    chk_save1 = ttk.Checkbutton(sec1, text="Сохранить", variable=chk_save1_var)
    chk_save1.grid(row=0, column=2, padx=4)

    make_button(sec1, "Построить",
                lambda: pm25_line_plot(DB, cmb_city1.get(),
                                       save=chk_save1_var.get()),
                CFG).grid(row=0, column=3, padx=6)

    # ---- Scatter: температура и PM2.5 ----
    sep1 = tki.Frame(frm, bg=CFG.get("colors", "fg"), height=1)
    sep1.pack(fill="x", pady=6)

    sec2 = styled_frame(frm)
    sec2.pack(fill="x", pady=4)

    make_label(sec2, "Диаграмма рассеивания Температура–PM2.5:", CFG).grid(
        row=0, column=0, sticky="w")

    scatter_mode = tki.IntVar(value=0)
    rad_all = ttk.Radiobutton(sec2, text="Все города",
                               value=0, variable=scatter_mode)
    rad_all.grid(row=0, column=1, padx=4)
    rad_one = ttk.Radiobutton(sec2, text="Один город",
                               value=1, variable=scatter_mode)
    rad_one.grid(row=0, column=2, padx=4)
    cmb_city2 = make_combobox(sec2, get_city_list(), CFG, width=14)
    cmb_city2.grid(row=0, column=3, padx=4)

    chk_save2_var = tki.BooleanVar(value=True)
    ttk.Checkbutton(sec2, text="Сохранить",
                    variable=chk_save2_var).grid(row=0, column=4, padx=4)

    def build_scatter():
        """
        Строит scatter-диаграмму для выбранного режима.
        """
        city = cmb_city2.get() if scatter_mode.get() == 1 else None
        temperature_pm25_scatter(DB, city=city, save=chk_save2_var.get())

    make_button(sec2, "Построить", build_scatter, CFG).grid(
        row=0, column=5, padx=6)

    # ---- Boxplot PM2.5 ----
    sep2 = tki.Frame(frm, bg=CFG.get("colors", "fg"), height=1)
    sep2.pack(fill="x", pady=6)

    sec3 = styled_frame(frm)
    sec3.pack(fill="x", pady=4)

    make_label(sec3, "Диаграмма Бокса–Вискера PM2.5 (все города):", CFG).grid(
        row=0, column=0, sticky="w")

    chk_save3_var = tki.BooleanVar(value=True)
    ttk.Checkbutton(sec3, text="Сохранить",
                    variable=chk_save3_var).grid(row=0, column=1, padx=4)
    make_button(sec3, "Построить",
                lambda: pm25_boxplot(DB, save=chk_save3_var.get()),
                CFG).grid(row=0, column=2, padx=6)

    # ---- Гистограмма температуры ----
    sep3 = tki.Frame(frm, bg=CFG.get("colors", "fg"), height=1)
    sep3.pack(fill="x", pady=6)

    sec4 = styled_frame(frm)
    sec4.pack(fill="x", pady=4)

    make_label(sec4, "Гистограмма температуры — Город:", CFG).grid(
        row=0, column=0, sticky="w")
    cmb_city4 = make_combobox(sec4, ["Все"] + get_city_list(), CFG, width=14)
    cmb_city4.grid(row=0, column=1, padx=6)

    make_label(sec4, "Столбцов:", CFG).grid(row=0, column=2, padx=(10, 2))
    ent_bins = make_entry(sec4, CFG, width=5)
    ent_bins.insert(0, "20")
    ent_bins.grid(row=0, column=3, padx=4)

    chk_save4_var = tki.BooleanVar(value=True)
    ttk.Checkbutton(sec4, text="Сохранить",
                    variable=chk_save4_var).grid(row=0, column=4, padx=4)

    def build_hist():
        """
        Строит гистограмму температуры.
        """
        city_val = cmb_city4.get()
        city = None if city_val == "Все" else city_val
        try:
            bins = int(ent_bins.get())
        except ValueError:
            bins = 20
        temperature_histogram(DB, city=city, bins=bins,
                              save=chk_save4_var.get())

    make_button(sec4, "Построить", build_hist, CFG).grid(
        row=0, column=5, padx=6)

    # ---- Столбчатая диаграмма среднего загрязнения ----
    sep4 = tki.Frame(frm, bg=CFG.get("colors", "fg"), height=1)
    sep4.pack(fill="x", pady=6)

    sec5 = styled_frame(frm)
    sec5.pack(fill="x", pady=4)

    make_label(sec5, "Столбчатая диаграмма загрязнения — Показатель:", CFG).grid(
        row=0, column=0, sticky="w")
    cmb_metric = make_combobox(sec5, ["PM2.5", "PM10", "NO2"], CFG, width=10)
    cmb_metric.grid(row=0, column=1, padx=6)

    chk_save5_var = tki.BooleanVar(value=True)
    ttk.Checkbutton(sec5, text="Сохранить",
                    variable=chk_save5_var).grid(row=0, column=2, padx=4)
    make_button(sec5, "Построить",
                lambda: pollution_bar_chart(DB, cmb_metric.get(),
                                            save=chk_save5_var.get()),
                CFG).grid(row=0, column=3, padx=6)


# ==============================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ==============================================================

def build_main_window() -> tki.Tk:
    """
    Создаёт и настраивает главное окно приложения.

    Returns
    -------
    tki.Tk
        Главное окно.

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    root = tki.Tk()
    root.title("Анализ качества воздуха по городам мира")

    # Размеры и положение из конфига
    w = CFG.getint("window", "width")
    h = CFG.getint("window", "height")
    x = CFG.getint("window", "x")
    y = CFG.getint("window", "y")
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.configure(bg=CFG.get("colors", "bg"))
    root.resizable(True, True)

    # ---- Заголовок ----
    hdr_frm = tki.Frame(root, bg=CFG.get("colors", "header_bg"), pady=6)
    hdr_frm.pack(fill="x")

    tki.Label(
        hdr_frm,
        text="Информационно-аналитическая система «Качество воздуха»",
        font=(CFG.get("fonts", "main"),
              CFG.getint("fonts", "size_header"),
              "bold"),
        bg=CFG.get("colors", "header_bg"),
        fg=CFG.get("colors", "fg")
    ).pack()

    # ---- Меню верхних кнопок ----
    menu_frm = tki.Frame(root, bg=CFG.get("colors", "btn_bg"), pady=4)
    menu_frm.pack(fill="x")

    make_button(menu_frm, "Справочник городов",
                lambda: open_city_manager(root), CFG).pack(
        side="left", padx=6)
    make_button(menu_frm, "Редактор данных",
                lambda: open_data_editor(root), CFG).pack(
        side="left", padx=6)
    make_button(menu_frm, "Настройки",
                lambda: open_settings_window(root), CFG).pack(
        side="left", padx=6)
    make_button(menu_frm, "Выход",
                root.quit, CFG).pack(side="right", padx=10)

    # ---- Notebook с вкладками отчётов ----
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TNotebook",
                    background=CFG.get("colors", "bg"),
                    borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=CFG.get("colors", "btn_bg"),
                    foreground=CFG.get("colors", "fg"),
                    font=(CFG.get("fonts", "main"),
                          CFG.getint("fonts", "size_normal"),
                          "bold"),
                    padding=[8, 4])
    style.map("TNotebook.Tab",
              background=[("selected", CFG.get("colors", "bg"))],
              foreground=[("selected", CFG.get("colors", "fg"))])

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=6, pady=6)

    # Создаём вкладки
    tab_names = [
        ("Высокий PM2.5", build_tab_report1),
        ("Температура", build_tab_report2),
        ("Климат", build_tab_report3),
        ("Сводная таблица", build_tab_report4),
        ("Статистика", build_tab_report5),
        ("Графики", build_tab_graphics),
    ]

    for name, builder in tab_names:
        tab = tki.Frame(notebook, bg=CFG.get("colors", "bg"))
        notebook.add(tab, text=f"  {name}  ")
        builder(tab)

    # ---- Строка статуса ----
    status_frm = tki.Frame(root, bg=CFG.get("colors", "header_bg"), pady=3)
    status_frm.pack(fill="x", side="bottom")

    count = len(DB)
    cities = DB["City"].nunique()
    tki.Label(
        status_frm,
        text=f"  Загружено: {count} записей  |  Городов: {cities}  |  "
             f"Источник: data/  |  Отчёты: output/ и graphics/",
        font=(CFG.get("fonts", "main"),
              CFG.getint("fonts", "size_small"),
              "normal"),
        bg=CFG.get("colors", "header_bg"),
        fg=CFG.get("colors", "fg")
    ).pack(side="left")

    return root


# ==============================================================
# ТОЧКА ВХОДА
# ==============================================================

def main() -> None:
    """
    Точка входа в приложение.

    Инициализирует директории, загружает данные,
    запускает главное окно.

    Returns
    -------
    None

    Авторы: Капитанов Антон, Родионов Игорь, Коноплев Кирилл (бригада 6)
    """
    global DB

    # Создаём все необходимые директории
    ensure_dirs(["data", "graphics", "images", "output", "library", "notes", "scripts"])

    # Инициализация базы данных из pickle-файлов
    # Если pickle-файлов нет — читаем из Excel
    data_dir = Path("data")
    if not any(data_dir.glob("*.pckl")):
        print("Первый запуск — создание базы данных из Excel...")
        create_pickle_database()
        print("База данных создана.")

    # Загрузка общей таблицы
    DB = load_all_data()
    print(f"Загружено {len(DB)} записей из {DB['City'].nunique()} городов.")

    # Запуск GUI
    root = build_main_window()
    root.mainloop()


if __name__ == "__main__":
    main()
