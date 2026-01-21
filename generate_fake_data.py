"""
Скрипт для генерации тестовых данных
"""
from database import KindergartenDB

def generate_fake_data():
    """Генерация тестовых данных"""
    db = KindergartenDB("kindergarten.db")
    db.connect()
    db.create_tables()
    
    # Воспитатели
    teachers = [
        {"last_name": "Иванова", "first_name": "Мария", "middle_name": "Петровна", 
         "phone": "+7 (999) 123-45-67", "email": "ivanova@example.com", 
         "birth_date": "1985-03-15", "education": "Высшее педагогическое", "experience": 12},
        
        {"last_name": "Смирнова", "first_name": "Елена", "middle_name": "Сергеевна", 
         "phone": "+7 (999) 234-56-78", "email": "smirnova@example.com", 
         "birth_date": "1990-07-22", "education": "Высшее педагогическое", "experience": 8},
        
        {"last_name": "Петрова", "first_name": "Ольга", "middle_name": "Викторовна", 
         "phone": "+7 (999) 345-67-89", "email": "petrova@example.com", 
         "birth_date": "1988-11-10", "education": "Среднее специальное", "experience": 10},
        
        {"last_name": "Козлова", "first_name": "Анна", "middle_name": "Дмитриевна", 
         "phone": "+7 (999) 456-78-90", "email": "kozlova@example.com", 
         "birth_date": "1992-05-18", "education": "Высшее педагогическое", "experience": 6}
    ]
    
    for teacher in teachers:
        db.add_teacher(**teacher)
    
    # Дети
    children = [
        {"last_name": "Алексеев", "first_name": "Дмитрий", "middle_name": "Иванович", 
         "birth_date": "2019-03-15", "gender": "М", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Белова", "first_name": "Анастасия", "middle_name": "Петровна", 
         "birth_date": "2019-05-22", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Васильев", "first_name": "Артем", "middle_name": "Сергеевич", 
         "birth_date": "2018-08-10", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Григорьева", "first_name": "София", "middle_name": "Александровна", 
         "birth_date": "2019-01-18", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Дмитриев", "first_name": "Максим", "middle_name": "Викторович", 
         "birth_date": "2018-11-25", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Егорова", "first_name": "Мария", "middle_name": "Дмитриевна", 
         "birth_date": "2019-07-08", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Жуков", "first_name": "Иван", "middle_name": "Андреевич", 
         "birth_date": "2018-04-12", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Зайцева", "first_name": "Полина", "middle_name": "Игоревна", 
         "birth_date": "2019-09-30", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Иванов", "first_name": "Александр", "middle_name": "Михайлович", 
         "birth_date": "2018-06-14", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Козлова", "first_name": "Виктория", "middle_name": "Сергеевна", 
         "birth_date": "2019-02-20", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Лебедев", "first_name": "Егор", "middle_name": "Павлович", 
         "birth_date": "2018-10-05", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Морозова", "first_name": "Дарья", "middle_name": "Владимировна", 
         "birth_date": "2019-04-17", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Новиков", "first_name": "Кирилл", "middle_name": "Алексеевич", 
         "birth_date": "2018-12-28", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Орлова", "first_name": "Елизавета", "middle_name": "Романовна", 
         "birth_date": "2019-06-11", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Павлов", "first_name": "Никита", "middle_name": "Денисович", 
         "birth_date": "2018-03-23", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Романова", "first_name": "Алиса", "middle_name": "Артемовна", 
         "birth_date": "2019-08-09", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Соколов", "first_name": "Тимофей", "middle_name": "Максимович", 
         "birth_date": "2018-05-16", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Титова", "first_name": "Ксения", "middle_name": "Игоревна", 
         "birth_date": "2019-10-27", "gender": "Ж", "enrollment_date": "2023-09-01"},
        
        {"last_name": "Федоров", "first_name": "Матвей", "middle_name": "Владимирович", 
         "birth_date": "2018-07-19", "gender": "М", "enrollment_date": "2022-09-01"},
        
        {"last_name": "Чернова", "first_name": "Варвара", "middle_name": "Николаевна", 
         "birth_date": "2019-11-04", "gender": "Ж", "enrollment_date": "2023-09-01"}
    ]
    
    for child in children:
        db.add_child(**child, group_id=None)
    
    print("✅ Успешно добавлено:")
    print(f"   - Воспитателей: {len(teachers)}")
    print(f"   - Детей: {len(children)}")
    
    db.close()

if __name__ == "__main__":
    generate_fake_data()
