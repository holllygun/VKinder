import vk_api
import yaml
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from db_injections import VK
from db_injections import Methods
from pick_data_from_db import Db_data

# Чтение значений из файла конфигурации config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

GROUP_TOKEN = config.get('GROUP_TOKEN', '')
ACCESS_TOKEN = config.get('ACCESS_TOKEN', '')

vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

methods = Methods()
db_picker = Db_data()
methods.add_action_type()


class Bot:
    def __init__(self):
        pass

    def sender(self, id, text, photo: None, **kwargs):  # функция для отправки сообщений
        vk.messages.send(user_id=id, message=text, attachment=photo, random_id=0, **kwargs)

    def user_name(self, user_id):  # достать имя пользователя
        user_get = vk.users.get(user_ids=user_id)
        user_get = user_get[0]['first_name']
        return user_get

    def favorites_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        buttons = ['Вернуться', 'Закончить']
        buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)
        return keyboard.get_keyboard()

    def yes_no_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        buttons = ['Да!', 'Я передумал']
        buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)
        return keyboard.get_keyboard()

    def standart_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        buttons = ['Дальше', 'Добавить', 'Закончить']
        buttons_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)
        keyboard.add_line()
        keyboard.add_button('Избранное', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    def longpoll_event(self):  # отправить ответ и создать клавиатуру
        counter = -1
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    id = event.user_id
                    vk = VK(ACCESS_TOKEN, id)
                    msg = event.text.lower()
                    param = vk.users_params()
                    print('VK PARAMS:', param)
                    user = vk.get_info_user()
                    user_list = vk.user_info_for_db(user)
                    methods.create_user(user_list)
                    if msg == 'привет' or msg == 'начать':
                        methods.add_actions(msg, id)
                        self.sender(id, f'Привет, {self.user_name(id)}! Начнем?💞 Сбор информации может занять несколько минут:)', None, keyboard=self.yes_no_keyboard())
                        counter = -1
                        for user in vk.users_list():
                            methods.create_user(user)
                            methods.add_photo(user)
                        matches = db_picker.get_matches_list(param)
                    elif msg == 'да!' or msg == 'вернуться':
                        methods.add_actions(msg, id)
                        counter += 1
                        if counter < len(matches):
                            user_id = matches[counter]['user_id']
                            self.sender(id, f'Выберите действие{db_picker.print_users(matches[counter])}', db_picker.three_photos(user_id), keyboard=self.standart_keyboard())
                        else:
                            self.sender(id, 'Пользователи закончились:( Начать сначала?', None, keyboard=self.yes_no_keyboard())
                            counter = -1
                    elif msg == 'дальше' or msg == 'вернуться':
                        methods.add_actions(msg, id)
                        counter += 1
                        if counter < len(matches):
                            user_id = matches[counter]['user_id']
                            self.sender(id, f"Следующий пользователь: {db_picker.print_users(matches[counter])}", db_picker.three_photos(user_id), keyboard=self.standart_keyboard())
                        else:
                            self.sender(id, 'Пользователи закончились:( Начать сначала?', None, keyboard=self.yes_no_keyboard())
                            counter = -1
                    elif msg == 'добавить':
                        methods.add_actions(msg, id)
                        user_id = matches[counter]['user_id']
                        action = methods.add_to_favorites(id, user_id)
                        if action == "Пользователь с таким ID уже существует":
                            self.sender(id, f'Пользователь был добавлен в избранное ранее', None, keyboard=self.favorites_keyboard())
                        else:
                            self.sender(id, f'Добавили в избранное👌', None, keyboard=self.favorites_keyboard())
                    elif msg == 'закончить' or msg == 'я передумал':
                        methods.add_actions(msg, id)
                        self.sender(id, 'Пока:(', None)
                    elif msg == 'избранное':
                        methods.add_actions(msg, id)
                        self.sender(id, f'Избранные профили 📃:\n {db_picker.show_favorites(id)}', None, keyboard=self.favorites_keyboard())
                    else:
                        self.sender(id, 'Я вас не понимаю:(', None)
