from models import Users, Photos, Favorites, UserActions, UserActionsAssociation
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


def create_session():
    password = input("Введите пароль для PostgreSQL: ")
    engine = create_engine(f"postgresql://postgres:{password}@localhost:5432/vkinder_db")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_user_action_and_association(session, user_id, action_type):
    action = UserActions(user_id=user_id, action_type=action_type)
    session.add(action)
    session.flush()

    association = UserActionsAssociation(user_id=user_id, action_id=action.action_id)
    session.add(association)
    session.commit()

def create_user():
    name = input("Введите имя: ")
    surname = input("Введите фамилию: ")
    age = int(input("Введите возраст: "))
    gender = input("Введите пол: ")
    city = input("Введите город: ")
    vk_id = input("Введите VK ID: ")

    user = Users(name=name, surname=surname, age=age, gender=gender, city=city, vk_id=vk_id)
    session.add(user)
    session.commit()
    print(f"Пользователь добавлен: ID {user.user_id}, {user.name}, {user.surname}, {user.age}, {user.gender}, {user.city}")


def add_photo():
    user_id = int(input("Введите ID пользователя, к которому принадлежит фото: "))
    url_photo = input("Введите URL фотографии: ")
    likes = int(input("Введите количество лайков: "))

    photo = Photos(user_id=user_id, url_photo=url_photo, likes=likes)
    session.add(photo)
    session.commit()
    print(f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")


def add_favorite():
    user_id = int(input("Введите ID пользователя, который добавляет другого пользователя в избранное: "))
    added_user_id = int(input("Введите ID пользователя, которого добавляют в избранное: "))

    favorite = Favorites(user_id=user_id, added_user_id=added_user_id)
    session.add(favorite)
    session.commit()
    print(f"Избранное добавлено: ID {favorite.favorite_id}, Пользователь ID {favorite.user_id}, Избранный п-ль ID {favorite.added_user_id}")


def add_action(session):
    user_id = int(input("Введите ID пользователя, который выполняет действие: "))
    action_type = input("Введите тип действия: ")

    add_user_action_and_association(session, user_id, action_type)


def clear_tables(session):
    session.query(UserActionsAssociation).delete()
    session.query(Photos).delete()
    session.query(Favorites).delete()
    session.query(UserActions).delete()
    session.query(Users).delete()

    session.commit()
    print("Таблицы очищены")


session = create_session()

while True:
    print("Выберите действие:")
    print("1. Добавить пользователя")
    print("2. Добавить фотографию")
    print("3. Добавить в избранное")
    print("4. Добавить действие пользователя")
    print("5. Очистить таблицы")
    print("0. Завершить")

    choice = input("Введите номер действия (или 0 для завершения): ")

    if choice == "1":
        create_user()
    elif choice == "2":
        add_photo()
    elif choice == "3":
        add_favorite()
    elif choice == "4":
        add_action(session)
    elif choice == "5":
        clear_tables(session)
    elif choice == "0":
        break
