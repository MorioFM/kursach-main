"""
Электронный журнал посещаемости
"""
import flet as ft
from datetime import datetime, date, timedelta
import calendar
from typing import Callable


class ElectronicJournalView(ft.Container):
    """Электронный журнал посещаемости в стиле календаря"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.page = page
        
        # Текущие параметры
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.selected_group = None
        self.attendance_cache = {}  # Кэш для данных посещаемости
        
        # Элементы управления
        self.group_dropdown = ft.Dropdown(
            label="Выберите группу",
            width=200,
            on_change=self.on_group_change
        )
        
        self.month_dropdown = ft.Dropdown(
            label="Месяц",
            width=150,
            value=str(self.current_month),
            options=[ft.dropdown.Option(str(i), calendar.month_name[i]) for i in range(1, 13)],
            on_change=self.on_month_change
        )
        
        self.year_dropdown = ft.Dropdown(
            label="Год",
            width=100,
            value=str(self.current_year),
            options=[ft.dropdown.Option(str(y), str(y)) for y in range(2020, 2030)],
            on_change=self.on_year_change
        )
        
        # Контейнер для журнала
        self.journal_container = ft.Container()
        
        # Основной контент
        self.content = ft.Column([
            ft.Row([
                self.group_dropdown,
                self.month_dropdown,
                self.year_dropdown,
                ft.ElevatedButton("Обновить", on_click=self.refresh_journal)
            ], spacing=10),
            ft.Divider(),
            self.journal_container
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        
        self.load_groups()
    
    def load_groups(self):
        """Загрузка списка групп"""
        try:
            groups = self.db.get_all_groups()
            self.group_dropdown.options = [
                ft.dropdown.Option(str(group['group_id']), group['group_name'])
                for group in groups
            ]
            if self.page:
                self.page.update()
        except Exception as ex:
            print(f"Ошибка загрузки групп: {ex}")
    
    def on_group_change(self, e):
        """Обработчик изменения группы"""
        self.selected_group = int(e.control.value) if e.control.value else None
        self.build_journal()
    
    def on_month_change(self, e):
        """Обработчик изменения месяца"""
        self.current_month = int(e.control.value)
        self.build_journal()
    
    def on_year_change(self, e):
        """Обработчик изменения года"""
        self.current_year = int(e.control.value)
        self.build_journal()
    
    def refresh_journal(self, e):
        """Обновление журнала"""
        self.build_journal()
    
    def get_days_in_month(self):
        """Получить количество дней в месяце"""
        return calendar.monthrange(self.current_year, self.current_month)[1]
    
    def build_journal(self):
        """Построение журнала посещаемости"""
        if not self.selected_group:
            self.journal_container.content = ft.Text("Выберите группу для отображения журнала")
            if self.page:
                self.page.update()
            return
        
        # Адаптивные цвета для темы
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK if self.page else False
        header_bg = ft.Colors.GREY_800 if is_dark else ft.Colors.GREY_200
        row_bg = ft.Colors.GREY_900 if is_dark else ft.Colors.GREY_50
        border_color = ft.Colors.GREY_600 if is_dark else ft.Colors.OUTLINE
        
        # Адаптивные цвета для статусов
        present_bg = ft.Colors.GREEN_100 if not is_dark else ft.Colors.GREEN_900
        present_color = ft.Colors.GREEN_800 if not is_dark else ft.Colors.GREEN_200
        absent_bg = ft.Colors.RED_100 if not is_dark else ft.Colors.RED_900
        absent_color = ft.Colors.RED_800 if not is_dark else ft.Colors.RED_200
        sick_bg = ft.Colors.ORANGE_100 if not is_dark else ft.Colors.ORANGE_900
        sick_color = ft.Colors.ORANGE_800 if not is_dark else ft.Colors.ORANGE_200
        
        try:
            # Получаем детей группы
            children = self.db.get_children_by_group(self.selected_group)
            if not children:
                self.journal_container.content = ft.Text("В группе нет детей")
                if self.page:
                    self.page.update()
                return
            
            # Получаем количество дней в месяце
            days_in_month = self.get_days_in_month()
            
            # Предзагружаем все данные посещаемости за месяц
            self.attendance_cache = {}
            for day in range(1, days_in_month + 1):
                date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                attendance_data = self.db.get_attendance_by_group_and_date(self.selected_group, date_str)
                for item in attendance_data:
                    self.attendance_cache[f"{item['child_id']}_{date_str}"] = item['status']
            
            # Создаем заголовок с днями
            header_row = [ft.Container(
                content=ft.Text("№", weight=ft.FontWeight.BOLD, size=12),
                width=40,
                padding=5,
                border=ft.border.all(1, border_color),
                bgcolor=header_bg
            ), ft.Container(
                content=ft.Text("🏭", weight=ft.FontWeight.BOLD, size=12),
                width=40,
                padding=5,
                border=ft.border.all(1, border_color),
                bgcolor=header_bg
            ), ft.Container(
                content=ft.Text("ФИО", weight=ft.FontWeight.BOLD, size=12),
                width=200,
                padding=5,
                border=ft.border.all(1, border_color),
                bgcolor=header_bg
            )]
            
            for day in range(1, days_in_month + 1):
                header_row.append(ft.Container(
                    content=ft.Text(str(day), weight=ft.FontWeight.BOLD, size=10, text_align=ft.TextAlign.CENTER),
                    width=30,
                    height=30,
                    padding=2,
                    border=ft.border.all(1, border_color),
                    bgcolor=header_bg
                ))
            
            # Создаем строки для каждого ребенка
            rows = [ft.Row(header_row, spacing=0)]
            
            for idx, child in enumerate(children, start=1):
                locker_symbol = child.get('locker_symbol', '❓')
                child_row = [ft.Container(
                    content=ft.Text(str(idx), size=11, text_align=ft.TextAlign.CENTER),
                    width=40,
                    padding=5,
                    border=ft.border.all(1, border_color),
                    bgcolor=row_bg
                ), ft.Container(
                    content=ft.Text(locker_symbol or '❓', size=16, text_align=ft.TextAlign.CENTER),
                    width=40,
                    padding=5,
                    border=ft.border.all(1, border_color),
                    bgcolor=row_bg
                ), ft.Container(
                    content=ft.Text(f"{child['last_name']} {child['first_name']}", size=11),
                    width=200,
                    padding=5,
                    border=ft.border.all(1, border_color),
                    bgcolor=row_bg
                )]
                
                for day in range(1, days_in_month + 1):
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    
                    # Получаем статус из кэша
                    status = self.attendance_cache.get(f"{child['child_id']}_{date_str}", 'Присутствует')
                    
                    # Определяем цвет и символ
                    if status == 'Присутствует':
                        bgcolor = present_bg
                        symbol = "+"
                        color = present_color
                    elif status == 'Отсутствует':
                        bgcolor = absent_bg
                        symbol = "-"
                        color = absent_color
                    else:  # Болеет
                        bgcolor = sick_bg
                        symbol = "Б"
                        color = sick_color
                    
                    cell = ft.Container(
                        content=ft.Text(symbol, size=10, weight=ft.FontWeight.BOLD, 
                                       text_align=ft.TextAlign.CENTER, color=color),
                        width=30,
                        height=30,
                        padding=2,
                        border=ft.border.all(1, border_color),
                        bgcolor=bgcolor,
                        on_click=lambda e, c_id=child['child_id'], d=date_str: self.toggle_attendance(c_id, d)
                    )
                    child_row.append(cell)
                
                rows.append(ft.Row(child_row, spacing=0))
            
            # Легенда
            legend = ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor=present_bg, 
                                   border=ft.border.all(1, border_color)),
                        ft.Text("+ Присутствует", size=12)
                    ], spacing=5),
                    padding=5
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor=absent_bg,
                                   border=ft.border.all(1, border_color)),
                        ft.Text("- Отсутствует", size=12)
                    ], spacing=5),
                    padding=5
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=20, height=20, bgcolor=sick_bg,
                                   border=ft.border.all(1, border_color)),
                        ft.Text("Б Болеет", size=12)
                    ], spacing=5),
                    padding=5
                )
            ], spacing=20)
            
            self.journal_container.content = ft.Column([
                ft.Text(f"Журнал посещаемости - {calendar.month_name[self.current_month]} {self.current_year}",
                        size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                legend,
                ft.Container(height=10),
                ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO)
            ])
            
            if self.page:
                self.page.update()
                
        except Exception as ex:
            print(f"Ошибка построения журнала: {ex}")
            self.journal_container.content = ft.Text(f"Ошибка: {ex}")
            if self.page:
                self.page.update()
    
    def toggle_attendance(self, child_id: int, date_str: str):
        """Переключение статуса посещаемости"""
        try:
            # Получаем текущий статус из кэша
            current_status = self.attendance_cache.get(f"{child_id}_{date_str}", 'Присутствует')
            
            # Циклическое переключение статусов
            if current_status == 'Присутствует':
                new_status = 'Отсутствует'
            elif current_status == 'Отсутствует':
                new_status = 'Болеет'
            else:
                new_status = 'Присутствует'
            
            # Обновляем в базе данных
            self.db.update_attendance_record(child_id, date_str, new_status)
            
            # Обновляем кэш
            self.attendance_cache[f"{child_id}_{date_str}"] = new_status
            
            # Перестраиваем журнал
            self.build_journal()
            
        except Exception as ex:
            print(f"Ошибка переключения посещаемости: {ex}")