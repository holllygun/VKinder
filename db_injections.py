import requests
from pprint import pprint
from datetime import date
import time
from models import Users, Photos, Favorites, UserActions, UserActionsAssociation
from sqlalchemy.orm import sessionmaker
from models import engine
from sqlalchemy import exc


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version

    def common_params(self):
        return{
            'access_token': self.token,
            'v': self.version
        }

    def get_info_user(self):
        params = self.common_params()
        params.update({"user_id": self.id, "fields": "city, bdate, sex, domain"})
        response = requests.get('https://api.vk.com/method/users.get', params=params).json()
        return response["response"][0]

    def get_profile_photo(self, user_id):  # Получение фото
        params = self.common_params()
        params.update(
            {"owner_id": user_id, "count": 3, "album_id": "profile", "photo_sizes": "0", "extended": "1", "rev": 1})
        response = requests.get('https://api.vk.com/method/photos.get', params=params).json()
        time.sleep(0.1)
        response = response['response']

        photos_list = []
        for item in response['items']:
            photo = max([size['height'] for size in item['sizes']])
            for size in item['sizes']:
                if size['height'] == photo:
                    photos_list.append({size['url']: item['likes']['count']})
        print(f"user photos: {photos_list}")
        return photos_list

    def search_people(self, city, age, sex):#change to 1000
        params = self.common_params()
        params.update(
            {"user_id": self.id, "count": 100, "city": city, "age_from": age - 2, "age_to": age + 5, "sex": sex,
             "fields": "id, domain, city, bdate, sex"}
        )
        response = requests.get('https://api.vk.com/method/users.search', params=params).json()
        return response['response']

    def calculate_age(self, b_date):
        today = date.today()
        day, month, year = b_date.split('.')
        day, month, year = int(day), int(month), int(year)
        age = today.year - year - ((today.month, today.day) < (month, day))
        return age

    def users_params(self):
        try:
            user = self.get_info_user()
            city = user['city']['id']
            gender = user['sex']
            if gender == 1:
                match_gender = 2
            else:
                match_gender = 1
            age = self.calculate_age(user['bdate'])
            info_param_user = {"city": city, "sex": match_gender, "age": age}
        except KeyError:
            return 'Недостаточно информации для добавления в список'
        return info_param_user

    def get_matches(self):
        current_user = self.get_info_user()
        try:
            city = current_user['city']['id']
            sex = current_user['sex']
            if sex == 1:
                match_gender = 2
            else:
                match_gender = 1
            age = self.calculate_age(current_user['bdate'])
            matches_for_user = self.search_people(city, age, match_gender)
        except KeyError:
            return 'Недостаточно информации для поиска. Пожалуйста, добавьте в личные данные ваш возраст и/или город.'
        print('MATCHES', matches_for_user)
        return matches_for_user['items']

    def users_list(self):
        matches_file = self.get_matches()
        print(f'matches_from_vk:{matches_file}')
        matches_list = []
        for match in matches_file:
            try:
                if match['is_closed'] is True:  # исключаем закрытые профили
                    continue
                else:
                    matches_list.append(self.user_info_for_db(match))
            except KeyError:
                continue
        pprint(matches_list)
        return matches_list

    def user_info_for_db(self, user_dict):
        name = user_dict['first_name']
        last_name = user_dict['last_name']
        sex = user_dict['sex']
        age = self.calculate_age(user_dict['bdate'])
        city = user_dict['city']['id']
        vk_id = user_dict['id']
        vk_link = f"https://vk.com/{user_dict['domain']}"
        users_photos = self.get_profile_photo(vk_id)
        user = [name, last_name, age, sex, city, vk_id, users_photos, vk_link]
        return user


class Methods:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def clear_tables(self):
        self.session.query(UserActionsAssociation).delete()
        self.session.query(Photos).delete()
        self.session.query(Favorites).delete()
        self.session.query(UserActions).delete()
        self.session.query(Users).delete()
        self.session.commit()
        print("Таблицы очищены")

    def create_user(self, info_user: list):
        try:
            self.name = info_user[0]
            self.surname = info_user[1]
            self.age = info_user[2]
            self.sex = info_user[3]
            self.city = info_user[4]
            self.vk_id = info_user[5]
            self.link = info_user[7]
            user = Users(name=self.name, surname = self.surname, age = self.age, gender=self.sex, city=self.city, vk_id=self.vk_id, vk_link=self.link)
            self.session.add(user)
            self.session.commit()
            print(f"Пользователь добавлен: ID {user.user_id}, {user.name}, {user.surname}, {user.age}, {user.gender}, {user.city}")
        except exc.IntegrityError:
            self.session.rollback()
            print("Пользователь с таким ID уже существует")

    def add_photo(self, info_user: list):
        photography = info_user[6]
        try:
            user = self.session.query(Users).filter(Users.vk_id.like(str(info_user[5]))).all()
            for u in user:
                user_id = u.user_id
            # Проверяем количество фотографий у пользователя
            photo_count = self.session.query(Photos).filter(Photos.user_id == user_id).count()

            if photo_count < 3:
                if isinstance(photography, list):
                    for i in photography:
                        for k, j in i.items():
                            url_photo = k
                            likes = j

                            # Проверяем, существует ли фотография с таким URL в базе
                            existing_photo = self.session.query(Photos).filter(Photos.url_photo == url_photo).first()

                            if not existing_photo:
                                # Фотографии с таким URL еще нет, добавляем ее
                                photo = Photos(user_id=user_id, url_photo=url_photo, likes=likes)
                                self.session.add(photo)
                                self.session.commit()
                                print(f"Фотография добавлена: ID {photo.photo_id}, Пользователь ID {photo.user_id}, URL {photo.url_photo}, Лайки {photo.likes}")
                            else:
                                print(f"Фотография с URL {url_photo} уже существует и не будет добавлена.")

            else:
                print("У пользователя уже есть 3 фотографии, новые фотографии не добавлены.")

        except exc.IntegrityError:
            self.session.rollback()
            print("Произошла ошибка при добавлении фотографии.")

    def add_to_favorites(self, id, user):
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(id))).all()
        user_id = user_id[0][0]
        try:
            added_user_id = user
            favorite = Favorites(added_user_id=added_user_id, user_id=user_id)
            self.session.add(favorite)
            self.session.commit()
            print(f"Пользователь добавлен.")
        except exc.IntegrityError:
            self.session.rollback()
            print("Пользователь с таким ID уже существует")
            return "Пользователь с таким ID уже существует"

    def add_action_type(self):
        try:
            action1 = UserActions(action_type='start')
            self.session.add(action1)
            action2 = UserActions(action_type='next_match')
            self.session.add(action2)
            action3 = UserActions(action_type='show favorites')
            self.session.add(action3)
            action4 = UserActions(action_type='add_user')
            self.session.add(action4)
            action5 = UserActions(action_type='stop')
            self.session.add(action5)
            self.session.commit()
        except exc.IntegrityError:
            self.session.rollback()

    def add_actions(self, msg, u_id):
        print('u_id', u_id)
        user_id = self.session.query(Users.user_id).filter(Users.vk_id.like(str(u_id))).all()
        print('TABLES', user_id)
        user_id = user_id[0][0]
        print('TABLES', user_id)
        if msg =='привет':
            action_id = self.session.query(UserActions.action_id).filter(UserActions.action_type.like('start')).all()
            action_id = action_id[0][0]
            action_association = UserActionsAssociation(user_id=user_id, action_id=action_id)
            self.session.add(action_association)
            self.session.commit()
        elif msg == 'дальше':
            action_id = self.session.query(UserActions.action_id).filter(UserActions.action_type.like('next_match')).all()
            action_id = action_id[0][0]
            action_association = UserActionsAssociation(user_id=user_id, action_id=action_id)
            self.session.add(action_association)
            self.session.commit()
        elif msg == 'избранное':
            action_id = self.session.query(UserActions.action_id).filter(UserActions.action_type.like('show favorites')).all()
            action_id = action_id[0][0]
            action_association = UserActionsAssociation(user_id=user_id, action_id=action_id)
            self.session.add(action_association)
            self.session.commit()
        elif msg == 'закончить' or msg == 'я передумал':
            action_id = self.session.query(UserActions.action_id).filter(UserActions.action_type.like('stop')).all()
            action_id = action_id[0][0]
            action_association = UserActionsAssociation(user_id=user_id, action_id=action_id)
            self.session.add(action_association)
            self.session.commit()
        elif msg == 'добавить':
            action_id = self.session.query(UserActions.action_id).filter(UserActions.action_type.like('add_user')).all()
            action_id = action_id[0][0]
            action_association = UserActionsAssociation(user_id=user_id, action_id=action_id)
            self.session.add(action_association)
            self.session.commit()

