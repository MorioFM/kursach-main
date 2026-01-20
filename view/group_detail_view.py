"""
Детальное представление группы с вкладками
"""
import flet as ft
from datetime import datetime, date
from settings.config import AGE_CATEGORIES


class GroupDetailView(ft.Container):
    """Детальное представление группы"""
    
    def __init__(self, db, group_id: int, on_close, page=None, on_refresh=None):
        super().__init__()
        self.db = db
        self.group_id = group_id
        self.on_close = on_close
        self.page = page
        self.on_refresh = on_refresh
        
        self.group = self.db.get_group_by_id(group_id)
        if not self.group:
            return
        
        group_name = self.group['group_name']
        
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Общая информация", icon=ft.Icons.INFO, content=self._create_info_tab()),
                ft.Tab(text="Дети", icon=ft.Icons.CHILD_CARE, content=self._create_children_tab()),
                ft.Tab(text="Воспитатели", icon=ft.Icons.PERSON, content=self._create_teachers_tab())
            ],
            expand=True
        )
        
        self.content = ft.Column([
            ft.Row([
                ft.Text(group_name, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Редактировать", on_click=self.show_edit_menu),
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: on_close())
            ]),
            ft.Divider(),
            self.tabs
        ], expand=True)
        self.expand = True
    
    def _create_info_tab(self):
        """Создать вкладку с общей информацией"""
        age_category = AGE_CATEGORIES.get(self.group['age_category'], self.group['age_category'])
        
        return ft.Container(
            content=ft.Column([
                self._info_row("Название группы", self.group['group_name']),
                self._info_row("Возрастная категория", age_category),
                self._info_row("Дата создания", self._format_date(self.group.get('created_at')))
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    def _create_children_tab(self):
        """Создать вкладку с детьми"""
        self.children_column = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self._load_children()
        
        return ft.Container(
            content=self.children_column,
            padding=20
        )
    
    def _create_teachers_tab(self):
        """Создать вкладку с воспитателями"""
        self.teachers_column = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self._load_teachers()
        
        return ft.Container(
            content=self.teachers_column,
            padding=20
        )
    
    def manage_children(self, e):
        """Управление детьми группы"""
        all_children = self.db.get_all_children()
        current_children = self.db.get_children_by_group(self.group_id)
        current_child_ids = [c['child_id'] for c in current_children]
        
        child_checkboxes = []
        for child in all_children:
            is_selected = child['child_id'] in current_child_ids
            checkbox = ft.Checkbox(
                label=f"{child['last_name']} {child['first_name']} {child.get('middle_name', '')}",
                value=is_selected,
                data=child['child_id']
            )
            child_checkboxes.append(checkbox)
        
        def save_children(e):
            for checkbox in child_checkboxes:
                if checkbox.value:
                    self.db.update_child(checkbox.data, group_id=self.group_id)
                elif checkbox.data in current_child_ids:
                    self.db.update_child(checkbox.data, group_id=None)
            
            self._load_children()
            if self.on_refresh:
                self.on_refresh()
            self.page.update()
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Дети группы: {self.group['group_name']}"),
            content=ft.Container(
                content=ft.Column(child_checkboxes, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_children),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def manage_teachers(self, e):
        """Управление воспитателями группы"""
        all_teachers = self.db.get_all_teachers()
        current_teachers = self.db.get_teachers_by_group(self.group_id)
        current_teacher_ids = [t['teacher_id'] for t in current_teachers]
        
        teacher_checkboxes = []
        for teacher in all_teachers:
            is_selected = teacher['teacher_id'] in current_teacher_ids
            checkbox = ft.Checkbox(
                label=teacher.get('full_name', ''),
                value=is_selected,
                data=teacher['teacher_id']
            )
            teacher_checkboxes.append(checkbox)
        
        def save_teachers(e):
            for teacher_id in current_teacher_ids:
                self.db.remove_group_teacher_relation(self.group_id, teacher_id)
            
            for checkbox in teacher_checkboxes:
                if checkbox.value:
                    self.db.add_group_teacher_relation(self.group_id, checkbox.data)
            
            self._load_teachers()
            if self.on_refresh:
                self.on_refresh()
            self.page.update()
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Воспитатели группы: {self.group['group_name']}"),
            content=ft.Container(
                content=ft.Column(teacher_checkboxes, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_teachers),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _load_children(self):
        """Загрузить список детей"""
        children = self.db.get_children_by_group(self.group_id)
        
        if not children:
            self.children_column.controls = [
                ft.Container(
                    content=ft.Text("В группе пока нет детей", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        else:
            self.children_column.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.MALE if child['gender'] == 'М' else ft.Icons.FEMALE, 
                                       color=ft.Colors.BLUE if child['gender'] == 'М' else ft.Colors.PINK, size=40),
                                ft.Column([
                                    ft.Text(f"{child['last_name']} {child['first_name']} {child.get('middle_name', '')}", 
                                           size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Возраст: {self._calculate_age(child['birth_date'])}", size=14),
                                    ft.Text(f"Дата рождения: {self._format_date(child['birth_date'])}", size=14)
                                ], expand=True)
                            ])
                        ], spacing=10),
                        padding=15
                    )
                ) for child in children
            ]
    
    def _load_teachers(self):
        """Загрузить список воспитателей"""
        teachers = self.db.get_teachers_by_group(self.group_id)
        
        if not teachers:
            self.teachers_column.controls = [
                ft.Container(
                    content=ft.Text("В группе нет назначенных воспитателей", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        else:
            self.teachers_column.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON, size=40),
                                ft.Column([
                                    ft.Text(teacher.get('full_name', ''), size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Телефон: {teacher.get('phone', 'Не указан')}", size=14),
                                    ft.Text(f"Email: {teacher.get('email', 'Не указан')}", size=14)
                                ], expand=True)
                            ])
                        ], spacing=10),
                        padding=15
                    )
                ) for teacher in teachers
            ]
    

    
    def _info_row(self, label: str, value: str):
        """Создать строку с информацией"""
        return ft.Row([
            ft.Text(f"{label}:", size=16, weight=ft.FontWeight.BOLD, width=200),
            ft.Text(str(value), size=16)
        ])
    
    def _stat_row(self, label: str, value: str, icon=None, color=None):
        """Создать строку статистики"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color) if icon else ft.Container(width=24),
                ft.Text(label, weight=ft.FontWeight.BOLD, width=200),
                ft.Text(value, size=16, color=color)
            ], spacing=10),
            padding=5
        )
    
    def _format_date(self, date_str):
        """Форматировать дату"""
        if not date_str:
            return "Не указано"
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str)
                return dt.strftime("%d.%m.%Y")
            return date_str
        except:
            return date_str
    
    def _calculate_age(self, birth_date_str):
        """Вычислить возраст"""
        if not birth_date_str:
            return "Не указан"
        
        try:
            if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            else:
                birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
            
            today = date.today()
            age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
            
            if age % 10 == 1 and age % 100 != 11:
                return f"{age} год"
            elif age % 10 in [2, 3, 4] and age % 100 not in [12, 13, 14]:
                return f"{age} года"
            else:
                return f"{age} лет"
        except:
            return "Не указан"

    def show_edit_menu(self, e):
        """Показать меню редактирования"""
        menu_items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INFO),
                title=ft.Text("Редактировать информацию"),
                on_click=lambda e: [self.page.close(menu_dialog), self.edit_group_info()]
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CHILD_CARE),
                title=ft.Text("Управление детьми"),
                on_click=lambda e: [self.page.close(menu_dialog), self.manage_children(e)]
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("Управление воспитателями"),
                on_click=lambda e: [self.page.close(menu_dialog), self.manage_teachers(e)]
            )
        ]
        
        menu_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редактирование группы"),
            content=ft.Container(
                content=ft.Column(menu_items, tight=True),
                width=400
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=lambda e: self.page.close(menu_dialog))
            ]
        )
        
        self.page.overlay.append(menu_dialog)
        menu_dialog.open = True
        self.page.update()
    
    def edit_group_info(self):
        """Редактировать информацию о группе"""
        group_name_field = ft.TextField(label="Название группы", value=self.group['group_name'], width=300)
        age_category_dropdown = ft.Dropdown(
            label="Возрастная категория",
            width=300,
            value=self.group['age_category'],
            options=[ft.dropdown.Option(k, v) for k, v in AGE_CATEGORIES.items()]
        )
        
        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редактировать группу"),
            content=ft.Container(
                content=ft.Column([
                    group_name_field,
                    age_category_dropdown
                ], spacing=10),
                width=400
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=lambda e: self.save_group_changes(edit_dialog, group_name_field, age_category_dropdown)),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(edit_dialog))
            ]
        )
        
        self.page.overlay.append(edit_dialog)
        edit_dialog.open = True
        self.page.update()
    
    def save_group_changes(self, dialog, group_name_field, age_category_dropdown):
        """Сохранить изменения группы"""
        if not group_name_field.value or not age_category_dropdown.value:
            return
        
        self.db.update_group(
            self.group_id,
            group_name=group_name_field.value,
            age_category=age_category_dropdown.value
        )
        
        from settings.logger import app_logger
        username = self.page.client_storage.get("username") if self.page else None
        app_logger.log('UPDATE', username, 'Group', f"Updated group: {group_name_field.value}")
        
        self.group = self.db.get_group_by_id(self.group_id)
        self.tabs.tabs[0].content = self._create_info_tab()
        self.content.controls[0].controls[0].value = self.group['group_name']
        
        if self.on_refresh:
            self.on_refresh()
        
        self.page.close(dialog)
        self.page.update()
