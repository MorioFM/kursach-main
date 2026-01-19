"""
Детальное представление информации о ребенке с вкладками
"""
import flet as ft
from datetime import datetime, date


class ChildDetailView(ft.Container):
    """Детальное представление информации о ребенке"""
    
    def __init__(self, db, child_id: int, on_close, page=None, on_refresh=None):
        super().__init__()
        self.db = db
        self.child_id = child_id
        self.on_close = on_close
        self.page = page
        self.on_refresh = on_refresh
        
        # Получаем данные ребенка
        self.child = self.db.get_child_by_id(child_id)
        if not self.child:
            return
        
        child_name = f"{self.child['last_name']} {self.child['first_name']} {self.child.get('middle_name', '')}"
        
        # Вкладки
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Общая информация", icon=ft.Icons.INFO, content=self._create_info_tab()),
                ft.Tab(text="Медкарта", icon=ft.Icons.MEDICAL_INFORMATION, content=self._create_medical_tab()),
                ft.Tab(text="Родители", icon=ft.Icons.FAMILY_RESTROOM, content=self._create_parents_tab())
            ],
            expand=True
        )
        
        self.content = ft.Column([
            ft.Row([
                ft.Text(child_name, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Редактировать", on_click=self.edit_child),
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: on_close())
            ]),
            ft.Divider(),
            self.tabs
        ], expand=True)
        self.expand = True
    
    def _create_info_tab(self):
        """Создать вкладку с общей информацией"""
        # Вычисляем возраст
        try:
            birth_date_str = self.child['birth_date']
            if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            else:
                birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
            
            today = date.today()
            age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
        except:
            age = "Неизвестно"
        
        from settings.config import GENDERS
        gender_text = GENDERS.get(self.child['gender'], self.child['gender'])
        
        return ft.Container(
            content=ft.Column([
                self._info_row("ФИО", f"{self.child['last_name']} {self.child['first_name']} {self.child.get('middle_name', '')}"),
                self._info_row("Дата рождения", self.child['birth_date']),
                self._info_row("Возраст", f"{age} лет"),
                self._info_row("Пол", gender_text),
                self._info_row("Группа", self.child.get('group_name', 'Без группы')),
                self._info_row("Дата зачисления", self.child['enrollment_date'])
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    def _create_medical_tab(self):
        """Создать вкладку с медицинской картой"""
        from view.medical_card_view import MedicalCardView
        
        return MedicalCardView(
            db=self.db,
            child_id=self.child_id,
            child_name=f"{self.child['last_name']} {self.child['first_name']}",
            on_close=lambda: None,
            page=self.page,
            embedded=True
        )
    
    def _create_parents_tab(self):
        """Создать вкладку с родителями"""
        self.parents_column = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self._load_parents()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Родители", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Настроить", icon=ft.Icons.SETTINGS, on_click=self.manage_parents)
                ]),
                ft.Divider(),
                self.parents_column
            ], spacing=10),
            padding=20
        )
    
    def _load_parents(self):
        """Загрузить список родителей"""
        parents = self.db.get_parents_by_child(self.child_id)
        
        if not parents:
            self.parents_column.controls = [
                ft.Container(
                    content=ft.Text("Родители не указаны", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        else:
            self.parents_column.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON, size=40),
                                ft.Column([
                                    ft.Text(parent.get('full_name', ''), size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Степень родства: {parent.get('relationship', 'Не указано')}", size=14)
                                ], expand=True)
                            ]),
                            ft.Divider(),
                            ft.Text(f"Телефон: {parent.get('phone', 'Не указан')}", size=14),
                            ft.Text(f"Email: {parent.get('email', 'Не указан')}", size=14),
                            ft.Text(f"Адрес: {parent.get('address', 'Не указан')}", size=14)
                        ], spacing=10),
                        padding=15
                    )
                ) for parent in parents
            ]
    
    def manage_parents(self, e):
        """Управление родителями ребенка"""
        all_parents = self.db.get_all_parents()
        current_parents = self.db.get_parents_by_child(self.child_id)
        current_parent_ids = [p['parent_id'] for p in current_parents]
        
        parent_checkboxes = []
        relationship_fields = {}
        parent_rows = []
        
        for parent in all_parents:
            is_selected = parent['parent_id'] in current_parent_ids
            current_relationship = next((p['relationship'] for p in current_parents if p['parent_id'] == parent['parent_id']), "")
            
            checkbox = ft.Checkbox(
                label=f"{parent.get('last_name', '')} {parent.get('first_name', '')}",
                value=is_selected,
                data=parent['parent_id']
            )
            
            relationship_field = ft.TextField(
                label="Степень родства",
                value=current_relationship,
                width=150,
                hint_text="Мама, Папа..."
            )
            
            parent_checkboxes.append(checkbox)
            relationship_fields[parent['parent_id']] = relationship_field
            parent_rows.append(ft.Row([checkbox, relationship_field], spacing=10))
        
        def save_relations(e):
            for parent_id in current_parent_ids:
                self.db.remove_parent_child_relation(parent_id, self.child_id)
            
            for checkbox in parent_checkboxes:
                if checkbox.value:
                    relationship = relationship_fields[checkbox.data].value or "Родитель"
                    self.db.add_parent_child_relation(checkbox.data, self.child_id, relationship)
            
            self._load_parents()
            self.page.update()
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Родители: {self.child['last_name']} {self.child['first_name']}"),
            content=ft.Container(
                content=ft.Column(parent_rows, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_relations),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def edit_child(self, e):
        """Редактировать ребенка"""
        from settings.config import GENDERS
        
        groups = self.db.get_all_groups()
        
        last_name_field = ft.TextField(label="Фамилия", value=self.child['last_name'], width=300)
        first_name_field = ft.TextField(label="Имя", value=self.child['first_name'], width=300)
        middle_name_field = ft.TextField(label="Отчество", value=self.child.get('middle_name', ''), width=300)
        birth_date_field = ft.TextField(label="Дата рождения", value=self.child['birth_date'], width=300, hint_text="дд-мм-гггг")
        gender_dropdown = ft.Dropdown(
            label="Пол",
            width=300,
            value=self.child['gender'],
            options=[ft.dropdown.Option(k, v) for k, v in GENDERS.items()]
        )
        group_dropdown = ft.Dropdown(
            label="Группа",
            width=300,
            value=str(self.child['group_id']) if self.child.get('group_id') else "0",
            options=[ft.dropdown.Option("0", "Без группы")] + [ft.dropdown.Option(str(g['group_id']), g['group_name']) for g in groups]
        )
        enrollment_date_field = ft.TextField(label="Дата зачисления", value=self.child['enrollment_date'], width=300, hint_text="дд-мм-гггг")
        
        def save_changes(e):
            if not last_name_field.value or not first_name_field.value or not birth_date_field.value or not gender_dropdown.value or not enrollment_date_field.value:
                return
            
            child_data = {
                'last_name': last_name_field.value,
                'first_name': first_name_field.value,
                'middle_name': middle_name_field.value or None,
                'birth_date': birth_date_field.value,
                'gender': gender_dropdown.value,
                'group_id': int(group_dropdown.value) if group_dropdown.value and group_dropdown.value != "0" else None,
                'enrollment_date': enrollment_date_field.value
            }
            
            self.db.update_child(self.child_id, **child_data)
            
            from settings.logger import app_logger
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('UPDATE', username, 'Child', f"Updated child: {child_data['last_name']} {child_data['first_name']}")
            
            self.child = self.db.get_child_by_id(self.child_id)
            self.tabs.tabs[0].content = self._create_info_tab()
            self.content.controls[0].controls[0].value = f"{self.child['last_name']} {self.child['first_name']} {self.child.get('middle_name', '')}"
            
            if self.on_refresh:
                self.on_refresh()
            
            self.page.update()
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редактировать ребенка"),
            content=ft.Container(
                content=ft.Column([
                    last_name_field,
                    first_name_field,
                    middle_name_field,
                    birth_date_field,
                    gender_dropdown,
                    group_dropdown,
                    enrollment_date_field
                ], spacing=10, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=500
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_changes),
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _info_row(self, label: str, value: str):
        """Создать строку с информацией"""
        return ft.Row([
            ft.Text(f"{label}:", size=16, weight=ft.FontWeight.BOLD, width=200),
            ft.Text(str(value), size=16)
        ])
