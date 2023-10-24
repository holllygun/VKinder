import vk_api
from pprint import pprint
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def sender(id, text, **kwargs):  # функция для отправки сообщений
    vk.messages.send(user_id=id, message=text, random_id=0, **kwargs)


def user_name(user_id):  # достать имя пользователя
    user_get = vk.users.get(user_ids=user_id)
    user_get = user_get[0]['first_name']
    return user_get


def standart_keyboard():
    keyboard = VkKeyboard(one_time=True)
    buttons = ['Дальше', 'Добавить', 'Закончить', 'Избранное']
    buttons_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.SECONDARY]
    for btn, btn_color in zip(buttons, buttons_colors):
        keyboard.add_button(btn, btn_color)
    return keyboard.get_keyboard()


def longpoll_event():  # отправить ответ и создать клавиатуру
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg = event.text.lower()
                id = event.user_id
                # user_city = get_user_info(id)
                # # user_city = user_city['response'][0]['city'][0]
                if msg == 'привет' or msg == 'начать':
                    keyboard = VkKeyboard(one_time=True)
                    buttons = ['Да!', 'Я передумал']
                    buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
                    for btn, btn_color in zip(buttons, buttons_colors):
                        keyboard.add_button(btn, btn_color)
                    sender(id, f'Привет, {user_name(id)}! Начнем?', keyboard=keyboard.get_keyboard())

                elif msg == 'да!' or msg == 'вернуться':
                    sender(id, f'Выберите действие', keyboard=standart_keyboard())

                elif msg == 'дальше':
                    sender(id, f'Едем дальше', keyboard=standart_keyboard())

                elif msg == 'добавить':
                    sender(id, f'Добавили в избранное', keyboard=standart_keyboard())

                elif msg == 'закончить' or msg == 'я передумал':
                    sender(id, 'Пока:(')

                elif msg == 'избранное':
                    keyboard = VkKeyboard(one_time=True)
                    buttons = ['Вернуться', 'Закончить']
                    buttons_colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
                    for btn, btn_color in zip(buttons, buttons_colors):
                        keyboard.add_button(btn, btn_color)
                    sender(id, 'Избранные профили: ', keyboard=keyboard.get_keyboard())

                else:
                    sender(id, 'Я вас не понимаю:(')


if __name__ == '__main__':
    token = open('group_token.txt').read()
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    try:
        longpoll_event()
    except KeyboardInterrupt:
        print('Работа приостановлена.')
