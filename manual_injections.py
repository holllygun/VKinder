from models import Users, Photos, Favorites, UserActions, UserActionsAssociation
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import engine
from sqlalchemy import exc

Session = sessionmaker(bind=engine)


class Metods:
    def __init__(self) -> None:
        self.session = Session()
        pass

    def add_user_action_and_association(self, user_id, action_type):
        action = UserActions(user_id=user_id, action_type=action_type)
        self.session.add(action)
        self.session.flush()

        association = UserActionsAssociation(user_id=user_id, action_id=action.action_id)
        self.session.add(association)
        self.session.commit()

    def create_user(self, info_user: list):  # Добавление пользователей в базу данных
        try:
            self.name = info_user[0]
            self.surname = info_user[1]
            self.age = info_user[2]
            self.sex = info_user[3]
            self.city = info_user[4]
            self.vk_id = info_user[5]
            self.link = info_user[7]
            self.params = info_user[8]
            print(info_user[8])

            if self.sex == 1:
                self.sex = "women"
            elif self.sex == 2:
                self.sex = "men"
            user = Users(name=self.name, surname=self.surname, age=self.age, gender=self.sex, city=self.city,
                         vk_id=self.vk_id)
            self.session.add(user)
            self.session.commit()
            print(
                f"Пользователь добавлен: ID {user.user_id}, {user.name}, {user.surname}, {user.age}, {user.gender}, {user.city}")
        except  exc.IntegrityError:
            self.session.rollback()
            print("Пользователь с таким ID уже существует")

    # def add_photo(self, info_user: list):
    #     self.photosnimok = info_user[6]
    #     try:
    #         u = self.session.query(Users).filter(Users.vk_id == f"{info_user[5]}").all()
    #         for i in u:
    #             self.user_id = i.user_id
    #         print(self.user_id)
    #
    #         # Проверяем количество фотографий у пользователя
    #         photo_count = self.session.query(Photos).filter(Photos.user_id == self.user_id).count()
    #
    #         if photo_count < 3:
    #             if isinstance(info_user[6], list):
    #                 for i in info_user[6]:
    #                     for k, j in i.items():
    #                         self.url_photo = k
    #                         self.likes = j
    #                         photo = Photos(user_id=self.user_id, url_photo=self.url_photo, likes=self.likes)
    #                         self.session.add(photo)
    #                         self.session.commit()
    #                         print(
    #                             f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")
    #
    #             else:
    #                 self.url_photo = info_user[6]
    #                 self.likes = 0
    #                 photo = Photos(user_id=self.user_id, url_photo=self.url_photo, likes=self.likes)
    #                 self.session.add(photo)
    #                 self.session.commit()
    #                 print(
    #                     f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")
    #         else:
    #             print("У пользователя уже есть 3 фотографии, новые фотографии не добавлены.")
    #
    #     except exc.IntegrityError:
    #         self.session.rollback()
    #         print("Фотография с таким URL уже существует")
    #
    def add_photo(self, info_user: list):
        self.photosnimok = info_user[6]
        try:
            u = self.session.query(Users).filter(Users.vk_id == f"{info_user[5]}").all()
            for i in u:
                self.user_id = i.user_id
            print(self.user_id)

            # Проверяем количество фотографий у пользователя
            photo_count = self.session.query(Photos).filter(Photos.user_id == self.user_id).count()

            if photo_count < 3:
                if isinstance(info_user[6], list):
                    for i in info_user[6]:
                        for k, j in i.items():
                            self.url_photo = k
                            self.likes = j

                            # Проверяем, существует ли фотография с таким URL в базе
                            existing_photo = self.session.query(Photos).filter(
                                Photos.url_photo == self.url_photo).first()

                            if not existing_photo:
                                # Фотографии с таким URL еще нет, добавляем ее
                                photo = Photos(user_id=self.user_id, url_photo=self.url_photo, likes=self.likes)
                                self.session.add(photo)
                                self.session.commit()
                                print(
                                    f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")
                            else:
                                print(f"Фотография с URL {self.url_photo} уже существует и не будет добавлена.")

                else:
                    self.url_photo = info_user[6]
                    self.likes = 0

                    # Проверяем, существует ли фотография с таким URL в базе
                    existing_photo = self.session.query(Photos).filter(Photos.url_photo == self.url_photo).first()

                    if not existing_photo:
                        # Фотографии с таким URL еще нет, добавляем ее
                        photo = Photos(user_id=self.user_id, url_photo=self.url_photo, likes=self.likes)
                        self.session.add(photo)
                        self.session.commit()
                        print(
                            f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")
                    else:
                        print(f"Фотография с URL {self.url_photo} уже существует и не будет добавлена.")
            else:
                print("У пользователя уже есть 3 фотографии, новые фотографии не добавлены.")

        except exc.IntegrityError:
            self.session.rollback()
            print("Произошла ошибка при добавлении фотографии.")

    def add_favorite(self):  # Добавление пользователя в избранное .Нужно доработать
        user_id = int(input("Введите ID пользователя, который добавляет другого пользователя в избранное: "))
        added_user_id = int(input("Введите ID пользователя, которого добавляют в избранное: "))

        favorite = Favorites(user_id=user_id, added_user_id=added_user_id)
        self.session.add(favorite)
        self.session.commit()
        print(
            f"Избранное добавлено: ID {favorite.favorite_id}, Пользователь ID {favorite.user_id}, Избранный п-ль ID {favorite.added_user_id}")

    def add_action(self, id):  # Добавление действия.Нужно доработать
        user_id = id
        action_type = input("Введите тип действия: ")

        self.add_user_action_and_association(self.session, user_id, action_type)

    def clear_tables(self):
        self.session.query(UserActionsAssociation).delete()
        self.session.query(Photos).delete()
        self.session.query(Favorites).delete()
        self.session.query(UserActions).delete()
        self.session.query(Users).delete()

        self.session.commit()
        print("Таблицы очищены")

    def get_users(self):  # Получение списка людей (имя, фамилия,вк id) по параметрам пользователя
        print(self.params)
        city = self.params["city"]
        print(city)
        new_sex = self.params['sex']
        age = self.params['age']
        list_name = []
        # for i in self.session.query(Users).filter(Users.city == city, Users.gender == new_sex, Users.age == age).all():
        #     list_name.append([i.name,i.surname,i.vk_id])
        for i in self.session.query(Users).filter(Users.city == str(city), Users.gender == str(new_sex),
                                                  Users.age == str(age)).all():
            list_name.append([i.name, i.surname, i.vk_id])

        return list_name

    def get_message(self, msg: None):  # Вывод сообщения в бота
        count = 0
        result = self.get_users()
        # gh = result[0]
        # if msg == "дальше":
        #      count+=1
        #      gh =result[count]
        # return f"{gh[0]} {gh[1]}\n https://vk.com/id{self.get_users[count][2]}\n {self.photosnimok[0]}\n {self.photosnimok[1]}\n {self.photosnimok[2]}"
        if result:
            gh = result[0]
            if msg == "дальше" and count < len(result) - 1:
                count += 1
                gh = result[count]
            return f"{gh[0]} {gh[1]}\n https://vk.com/id{gh[2]}\n {self.photosnimok[0]}\n {self.photosnimok[1]}\n {self.photosnimok[2]}"
        else:
            return "Список пользователей пуст"

# metods_instance = Metods()
# metods_instance.clear_tables()
