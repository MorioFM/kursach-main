"""
Детальное представление информации о родителе с вкладками
"""
import flet as ft


class ParentDetailView(ft.Container):
    """Детальное представление информации о родителе"""
    
    def __init__(self, db, parent_id: int, on_close, page=None, on_refresh=None):
        super().__init__()
        self.db = db
        self.parent_id = parent_id
        self.on_close = on_close
        self.page = page
        self.on_refresh = on_refresh
        self.is_admin = page.client_storage.get("user_role") == "admin" if page else True
        
        # Получаем данные родителя
        self.parent_data = self.db.get_parent_by_id(parent_id)
        if not self.parent_data:
            return
        
        parent_name = f"{self.parent_data['last_name']} {self.parent_data['first_name']} {self.parent_data.get('middle_name', '')}"
        
        # Вкладки
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Общая информация", icon=ft.Icons.INFO, content=self._create_info_tab()),
                ft.Tab(text="Дети", icon=ft.Icons.CHILD_CARE, content=self._create_children_tab())
            ],
            expand=True
        )
        
        # Кнопка редактирования для всех пользователей
        header_buttons = [
            ft.IconButton(icon=ft.Icons.EDIT, tooltip="Редактировать", on_click=self.edit_parent),
            ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: on_close())
        ]
        
        self.content = ft.Column([
            ft.Row([
                ft.Text(parent_name, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True)
            ] + header_buttons),
            ft.Divider(),
            self.tabs
        ], expand=True)
        self.expand = True
    
    def _create_info_tab(self):
        """Создать вкладку с общей информацией"""
        return ft.Container(
            content=ft.Column([
                self._info_row("ФИО", f"{self.parent_data['last_name']} {self.parent_data['first_name']} {self.parent_data.get('middle_name', '')}"),
                self._info_row("Телефон", self.parent_data.get('phone', 'Не указан')),
                self._info_row("Email", self.parent_data.get('email', 'Не указан')),
                self._info_row("Адрес", self.parent_data.get('address', 'Не указан'))
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20
        )
    
    def _create_children_tab(self):
        """Создать вкладку с детьми"""
        self.children_column = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self._load_children()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Дети", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Настроить", icon=ft.Icons.SETTINGS, on_click=self.manage_children)
                ]),
                ft.Divider(),
                self.children_column
            ], spacing=10),
            padding=20
        )
    
    def _load_children(self):
        """Загрузить список детей"""
        children = self.db.get_children_by_parent(self.parent_id)
        
        if not children:
            self.children_column.controls = [
                ft.Container(
                    content=ft.Text("Дети не указаны", size=16, color=ft.Colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            ]
        else:
            self.children_column.controls = []
            for child in children:
                child_full_name = f"{child.get('last_name', '')} {child.get('first_name', '')} {child.get('middle_name', '') or ''}".strip()
                if not child_full_name:
                    child_full_name = child.get('full_name', 'Неизвестно')
                
                self.children_column.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.CHILD_CARE, size=40),
                                    ft.Column([
                                        ft.Text(child_full_name, size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Степень родства: {child.get('relationship', 'Не указано')}", size=14)
                                    ], expand=True)
                                ]),
                                ft.Divider(),
                                ft.Text(f"Группа: {child.get('group_name', 'Без группы')}", size=14),
                                ft.Text(f"Дата рождения: {child.get('birth_date', 'Не указана')}", size=14)
                            ], spacing=10),
                            padding=15
                        )
                    )
                )
    
    def manage_children(self, e):
        """Управление детьми родителя"""
        all_children = self.db.get_all_children()
        current_children = self.db.get_children_by_parent(self.parent_id)
        current_child_ids = [c['child_id'] for c in current_children]
        
        child_checkboxes = []
        relationship_fields = {}
        child_rows = []
        
        for child in all_children:
            is_selected = child['child_id'] in current_child_ids
            current_relationship = next((c['relationship'] for c in current_children if c['child_id'] == child['child_id']), "")
            
            checkbox = ft.Checkbox(
                label=f"{child.get('last_name', '')} {child.get('first_name', '')}",
                value=is_selected,
                data=child['child_id']
            )
            
            relationship_field = ft.TextField(
                label="Степень родства",
                value=current_relationship,
                width=150,
                hint_text="Мама, Папа..."
            )
            
            child_checkboxes.append(checkbox)
            relationship_fields[child['child_id']] = relationship_field
            child_rows.append(ft.Row([checkbox, relationship_field], spacing=10))
        
        def save_relations(e):
            for child_id in current_child_ids:
                self.db.remove_parent_child_relation(self.parent_id, child_id)
            
            for checkbox in child_checkboxes:
                if checkbox.value:
                    relationship = relationship_fields[checkbox.data].value or "Родитель"
                    self.db.add_parent_child_relation(self.parent_id, checkbox.data, relationship)
            
            self._load_children()
            bs.open = False
            self.page.update()
        
        def cancel_manage(e):
            bs.open = False
            self.page.update()
        
        bs = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Дети: {self.parent_data['last_name']} {self.parent_data['first_name']}"),
            content=ft.Container(
                content=ft.Column(child_rows, scroll=ft.ScrollMode.AUTO),
                width=500,
                height=400
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_relations),
                ft.TextButton("Отмена", on_click=cancel_manage)
            ],
            open=True
        )
        
        self.page.overlay.append(bs)
        self.page.update()
    
    def edit_parent(self, e):
        """Редактировать родителя"""
        last_name_field = ft.TextField(label="Фамилия", value=self.parent_data['last_name'], width=300)
        first_name_field = ft.TextField(label="Имя", value=self.parent_data['first_name'], width=300)
        middle_name_field = ft.TextField(label="Отчество", value=self.parent_data.get('middle_name', ''), width=300)
        
        phone = self.parent_data.get('phone', '')
        country_code = '+7'
        phone_number = ''
        if phone:
            if phone.startswith('+375'):
                country_code = '+375'
                phone_number = phone[4:]
            elif phone.startswith('+1'):
                country_code = '+1'
                phone_number = phone[2:]
            elif phone.startswith('+7'):
                country_code = '+7'
                phone_number = phone[2:]
            else:
                phone_number = phone
        
        country_code_dropdown = ft.Dropdown(
            label="Код страны",
            width=140,
            value=country_code,
            options=[
                ft.dropdown.Option("+7", "+7 (Россия)"),
                ft.dropdown.Option("+375", "+375 (Беларусь)"),
                ft.dropdown.Option("+1", "+1 (США)")
            ]
        )
        
        def format_phone(e):
            value = e.control.value
            digits = ''.join(filter(str.isdigit, value))
            if len(digits) > 10:
                digits = digits[:10]
            
            code = country_code_dropdown.value
            if code == "+1":
                if len(digits) <= 3:
                    formatted = digits
                elif len(digits) <= 6:
                    formatted = f"{digits[:3]}-{digits[3:]}"
                else:
                    formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            elif code == "+375":
                if len(digits) <= 2:
                    formatted = digits
                elif len(digits) <= 5:
                    formatted = f"{digits[:2]}-{digits[2:]}"
                elif len(digits) <= 7:
                    formatted = f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
                else:
                    formatted = f"{digits[:2]}-{digits[2:5]}-{digits[5:7]}-{digits[7:]}"
            else:
                if len(digits) <= 3:
                    formatted = digits
                elif len(digits) <= 6:
                    formatted = f"{digits[:3]}-{digits[3:]}"
                elif len(digits) <= 8:
                    formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                else:
                    formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
            
            e.control.value = formatted
            e.control.update()
        
        phone_field = ft.TextField(label="Телефон", value=phone_number, width=150, on_change=format_phone)
        email_field = ft.TextField(label="Email", value=self.parent_data.get('email', ''), width=300)
        address_field = ft.TextField(label="Адрес", value=self.parent_data.get('address', ''), width=300, multiline=True, max_lines=2)
        
        def save_changes(e):
            if not last_name_field.value or not first_name_field.value:
                return
            
            full_phone = None
            if phone_field.value and phone_field.value.strip():
                full_phone = country_code_dropdown.value + phone_field.value
            
            parent_data = {
                'last_name': last_name_field.value,
                'first_name': first_name_field.value,
                'middle_name': middle_name_field.value or None,
                'phone': full_phone,
                'email': email_field.value or None,
                'address': address_field.value or None
            }
            
            self.db.update_parent(self.parent_id, **parent_data)
            
            from settings.logger import app_logger
            username = self.page.client_storage.get("username") if self.page else None
            app_logger.log('UPDATE', username, 'Parent', f"Updated parent: {parent_data['last_name']} {parent_data['first_name']}")
            
            self.parent_data = self.db.get_parent_by_id(self.parent_id)
            self.tabs.tabs[0].content = self._create_info_tab()
            self.content.controls[0].controls[0].value = f"{self.parent_data['last_name']} {self.parent_data['first_name']} {self.parent_data.get('middle_name', '')}"
            
            if self.on_refresh:
                self.on_refresh()
            
            bs.open = False
            self.page.update()
        
        def cancel_edit(e):
            bs.open = False
            self.page.update()
        
        bs = ft.AlertDialog(
            modal=True,
            title=ft.Text("Редактировать родителя"),
            content=ft.Container(
                content=ft.Column([
                    last_name_field,
                    first_name_field,
                    middle_name_field,
                    ft.Row([country_code_dropdown, phone_field]),
                    email_field,
                    address_field
                ], spacing=10, scroll=ft.ScrollMode.AUTO),
                width=500,
                height=400
            ),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=save_changes),
                ft.TextButton("Отмена", on_click=cancel_edit)
            ],
            open=True
        )
        
        self.page.overlay.append(bs)
        self.page.update()
    
    def _info_row(self, label: str, value: str):
        """Создать строку с информацией"""
        return ft.Row([
            ft.Text(f"{label}:", size=16, weight=ft.FontWeight.BOLD, width=200),
            ft.Text(str(value), size=16)
        ])
