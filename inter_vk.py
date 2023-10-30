from datetime import date
import requests
import vk_api


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.vk = vk_api.VkApi(token=access_token)
        self.api = self.vk.get_api()

    def common_params(self):
        return {
            'access_token': self.token,
            'v': self.version
        }

    def get_profile_photo(self, user_id):
        params = self.common_params()
        params.update({"owner_id": user_id, "count": 3, "album_id": "profile", "photo_sizes": "0", "extended": "1", "rev": 1})
        response = requests.get('https://api.vk.com/method/photos.get', params=params).json()
        response = response['response']
        photos_list = []
        for item in response['items']:
            photo = max([size['height'] for size in item['sizes']])
            for size in item['sizes']:
                if size['height'] == photo:
                    photos_list.append(size['url'])
        return photos_list

    def get_info_user(self):
        params = self.common_params()
        params.update({"user_id": self.id, "fields": 'city, bdate, sex'})
        response = requests.get('https://api.vk.com/method/users.get', params=params)
        return response.json()

    def get_members(self, group_id, fields: str):  # записать участников группы в бд
        params = self.common_params()
        params.update({"group_id": group_id, "fields": fields})
        response = requests.get('https://api.vk.com/method/groups.getMembers', params=params)
        return response.json()

    def search_people(self, city, age, sex): # поменять count на 1000
        params = self.common_params()
        params.update({"user_id": self.id, "count": 5, "city": city, "age_from": age - 2, "age_to": age + 5, "sex": sex, "fields": "id, domain, city, bdate, sex"})
        response = requests.get('https://api.vk.com/method/users.search', params=params)
        return response.json()

    def calculate_age(self, b_date):
        today = date.today()
        day, month, year = b_date.split('.')
        day, month, year = int(day), int(month), int(year)
        age = today.year - year - ((today.month, today.day) < (month, day))
        return age

    def get_matches(self): # выбрать пользователей по параметрам
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

    def users_list(self): # список фамилий,имен, ссылок пользователей + 3 фотографии
        try:
            matches_file = self.get_matches()
            matches_file = matches_file['response']['items']
            final_file = []
            for item in matches_file:
                try:
                    id = item['id']
                    users_photos = self.get_profile_photo(id)
                    item.update(dict(photos=users_photos))
                except KeyError:
                    item.update(dict(photos='Нет фотографий:('))
            for match in matches_file:
                if match['photos'] != 'Нет фотографий:(':
                    photos = '\n'.join(match['photos'])
                else:
                    photos = match['photos']
                link = match['domain']
                full_name = match['first_name'] + ' ' + match['last_name']
                final_file.append([full_name, link, photos])
            return final_file
        except TypeError:
            return self.get_matches()

