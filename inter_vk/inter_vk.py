import requests
from datetime import date
from pprint import pprint
import time


class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version

    def common_params(self):
        return {
            'access_token': self.token,
            'v': self.version
        }

    def get_profile_photo(self, user_id):  # Получение фото
        params = self.common_params()
        params.update(
            {"owner_id": user_id, "count": 3, "album_id": "profile", "photo_sizes": "0", "extended": "1", "rev": 1})
        response = requests.get('https://api.vk.com/method/photos.get', params=params).json()
        time.sleep(0.5)

        print(response)
        response = response['response']

        photos_list = []
        for item in response['items']:
            photo = max([size['height'] for size in item['sizes']])
            for size in item['sizes']:
                if size['height'] == photo:
                    photos_list.append({size['url']: item['likes']['count']})
        return photos_list

    def get_info_user(self):
        params = self.common_params()
        params.update({"user_id": self.id, "fields": 'city, bdate, sex'})
        response = requests.get('https://api.vk.com/method/users.get', params=params)

        return response.json()

    # def get_info_user(self):
    #     params = self.common_params()
    #     params.update({"user_id": self.id, "fields": 'city, bdate, sex'})
    #     response = requests.get('https://api.vk.com/method/users.get', params=params)
    #     json_data = response.json()
    #
    #     with open('user_info.json', 'w', encoding='utf-8') as json_file:
    #         json.dump(json_data, json_file, ensure_ascii=False, indent=4)
    #
    #     return json_data

    def get_members(self, group_id, fields: str):  # записать участников группы в бд
        params = self.common_params()
        params.update({"group_id": group_id, "fields": fields})
        response = requests.get('https://api.vk.com/method/groups.getMembers', params=params)
        return response.json()

    def search_people(self, city, age, sex):  # поменять count на 1000
        params = self.common_params()
        params.update(
            {"user_id": self.id, "count": 10, "city": city, "age_from": age - 2, "age_to": age + 5, "sex": sex,
             "fields": "id, domain, city, bdate, sex"})
        response = requests.get('https://api.vk.com/method/users.search', params=params)
        return response.json()

    def calculate_age(self, b_date):
        today = date.today()
        day, month, year = b_date.split('.')
        day, month, year = int(day), int(month), int(year)
        age = today.year - year - ((today.month, today.day) < (month, day))
        return age

    def get_matches(self):  # выбрать пользователей по параметрам
        user = self.get_info_user()
        try:
            city = user['response'][0]['city']['id']
            sex = user['response'][0]['sex']
            if sex == 1:
                new_sex = 2
            else:
                new_sex = 1
            age = self.calculate_age(user['response'][0]['bdate'])
            people = self.search_people(city, age, new_sex)

        except KeyError:
            return 'Недостаточно информации для поиска. Пожалуйста, добавьте в личные данные ваш возраст и/или город.'
        return people

    def param_user(self):
        # info_param_user = []
        try:
            user = self.get_info_user()
            city = user['response'][0]['city']['id']
            sex = user['response'][0]['sex']
            if sex == 1:
                new_sex = 2
            else:
                new_sex = 1
            age = self.calculate_age(user['response'][0]['bdate'])
            info_param_user = {"city": city, "sex": new_sex, "age": age}
            print(info_param_user)
        except KeyError:
            return 'Недостаточно информации для поиска. Пожалуйста, добавьте в личные данные ваш возраст и/или город.'

        return info_param_user

    # def users_list(self):  # список фамилий, имен, ссылок пользователей + 3 фотографии
    #     matches_file = self.get_matches()
    #     print(matches_file)
    #     matches_file = matches_file['response']['items']
    #     final_file = []
    #     for match in matches_file:
    #         name = match['first_name']
    #         surname = match['last_name']
    #         age = self.calculate_age(match['bdate'])
    #         sex = match['sex']
    #         city = match['city']['title']
    #         id = match['id']
    #         users_photos = self.get_profile_photo(id)
    #         link = f"https://vk.com/{match['domain']}"
    #         final_file.append([name, surname, age, sex, city, id, users_photos, link, self.param_user()])
    #     return final_file
    def users_list(self):  # список фамилий, имен, ссылок пользователей + 3 фотографии
        matches_file = self.get_matches()
        print(f"matches_file: {matches_file}")
        matches_file = matches_file['response']['items']
        final_file = []
        for match in matches_file:
            name = match['first_name']
            surname = match['last_name']
            age = self.calculate_age(match['bdate'])
            sex = match['sex']
            city = match['city']['title']
            id = match['id']
            users_photos = self.get_profile_photo(id)
            print(f"User {name} {surname} ({id}): {users_photos}")
            link = f"https://vk.com/{match['domain']}"
            final_file.append([name, surname, age, sex, city, id, users_photos, link, self.param_user()])
        return final_file

