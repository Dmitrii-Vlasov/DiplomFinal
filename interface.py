# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import datetime
from config import comunity_token, acces_token, db_url_object
from core import VkTools
from DB import DataBase
# отправка сообщений


class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.database = DataBase(db_url_object)
        self.database.create_table()
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

    def get_profile_from_db(self, worksheet):
        data = self.database.select()
        flag = False
        for i in data:
            if i[1] == worksheet['id']:
                flag = True
                break
            else:
                flag = False
        return flag

    def get_parameter(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event.text

# обработка событий / получение сообщений
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Привет друг, {self.params["name"]}')
                    # Проверка полученных данных о пользвоателе
                    for i in self.params:
                        if self.params[i] is None:
                            if self.params['name'] is None:
                                self.message_send(event.user_id, 'Введите ваше имя и фамилию:')
                                self.params['name'] = self.get_parameter()
                            elif self.params['sex'] is None:
                                self.message_send(event.user_id, 'Введите свой пол (1-м, 2-ж):')
                                self.params['sex'] = int(self.get_parameter())
                            elif self.params['city'] is None:
                                self.message_send(event.user_id, 'Введите город:')
                                self.params['city'] = self.get_parameter()
                            elif self.params['year'] is None:
                                self.message_send(event.user_id, 'Введите дату рождения (дд.мм.гггг):')
                                self.params['year'] = datetime.now().year - int(self.get_parameter().split('.')[2])

                    self.message_send(event.user_id, 'Успешная регистрация!')

                elif event.text.lower() == 'поиск':
                    '''Логика для поиска анкет'''
                    self.message_send(
                        event.user_id, 'Начинаем поиск')

                    while True:
                        if self.worksheets:
                            worksheet = self.worksheets.pop()
                            '''првоерка анкеты в бд в соотвествие с event.user_id'''
                            data_flag = self.get_profile_from_db(worksheet)
                            if data_flag is False:
                                """добавить анкету в бд в соотвествие с event.user_id"""
                                self.database.insert(event.user_id, worksheet['id'])
                                break
                        else:
                            self.worksheets = self.vk_tools.search_worksheet(
                                self.params, self.offset)
                            self.offset+=10

                    photos = self.vk_tools.get_photos(worksheet['id'])

                    photo_string = ''
                    for photo in photos:
                        photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                    self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}',
                        attachment=photo_string
                    )

                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч')
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()
