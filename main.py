from pprint import pprint

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from bot_vk.bot_vk import Bot

if __name__ == '__main__':
  
    bot1 = Bot()
    try:
        bot1.longpoll_event()
    except KeyboardInterrupt:
        print('Работа приостановлена.')