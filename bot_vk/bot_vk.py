import vk_api
import yaml
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from inter_vk.inter_vk import VK
from manual_injections import Metods

# Чтение значений из файла конфигурации config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

GROUP_TOKEN = config.get('GROUP_TOKEN', '')
ACCESS_TOKEN = config.get('ACCESS_TOKEN', '')

vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

metods = Metods()


class Bot:
    def __init__(self):
        pass

    def sender(self, id, text, **kwargs):  # функция для отправки сообщений
        vk.messages.send(user_id=id, message=text, random_id=0, **kwargs)

    def sender_photo(self, id, photo, **kwargs):  # функция для отправки фото. Доработать надо .
        vk.messages.send(user_id=id, attachment=photo, random_id=0, **kwargs)

    def user_name(self, user_id):  # достать имя пользователя
        user_get = vk.users.get(user_ids=user_id)
        user_get = user_get[0]['first_name']
        return user_get

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
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    id = event.user_id
                    vk = VK(ACCESS_TOKEN, id)
                    msg = event.text.lower()
                    if msg == 'привет' or msg == 'начать':
                        keyboard = VkKeyboard(one_time=True)
                        buttons = ['Да!', 'Я передумал']
                        buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
                        for btn, btn_color in zip(buttons, buttons_colors):
                            keyboard.add_button(btn, btn_color)
                        self.sender(id, f'Привет, {self.user_name(id)}! Начнем?💞', keyboard=keyboard.get_keyboard())
                    elif msg == 'да!' or msg == 'вернуться':
                        for user in vk.users_list():
                            metods.create_user(user)
                            metods.add_photo(user)
                        metods.get_message(msg)
                        self.sender(id, f'Выберите действие', keyboard=self.standart_keyboard())
                    elif msg == 'дальше':
                        self.sender(id, f"Едем дальше", keyboard=self.standart_keyboard())
                        metods.get_message(msg)
                    elif msg == 'добавить':
                        self.sender(id, f'Добавили в избранное', keyboard=self.standart_keyboard())
                    elif msg == 'закончить' or msg == 'я передумал':
                        self.sender(id, 'Пока:(')
                    elif msg == 'избранное':

                        keyboard = VkKeyboard(one_time=True)
                        buttons = ['Вернуться', 'Закончить']
                        buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
                        for btn, btn_color in zip(buttons, buttons_colors):
                            keyboard.add_button(btn, btn_color)
                        self.sender(id, 'Избранные профили: ', keyboard=keyboard.get_keyboard())

                    else:
                        self.sender(id, 'Я вас не понимаю:(')