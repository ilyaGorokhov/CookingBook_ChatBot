from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi
from help import help
from data import db_session, __all_models
from command_structure import AddMeal, HowToPrepare, WhatToCookFrom, RandomMeal, Help


def create_keyboard(*options_of_buttons):
    keyboard = VkKeyboard(one_time=False)
    for button, color in options_of_buttons:
        if button + color == '//':
            keyboard.add_line()
            continue
        if color == 'зелёный':
            color = VkKeyboardColor.POSITIVE
        elif color == 'красный':
            color = VkKeyboardColor.NEGATIVE
        elif color == 'белый':
            color = VkKeyboardColor.SECONDARY
        elif color == 'синий':
            color = VkKeyboardColor.PRIMARY
        keyboard.add_button(button, color=color)
    return keyboard.get_keyboard()


def work_bot(longpoll, vk_session, *commands):
    buttons = [['?какприготовить', 'белый'],
               ['/', '/'],
               ['?чтоприготовитьиз', 'белый'],
               ['?случайноеблюдо', 'белый'],
               ['/', '/'],
               ['?добавитьблюдо', 'белый'], ['Помощь', 'зелёный']]
    opened_keyboard = create_keyboard(*buttons)
    closed_keyboard = VkKeyboard.get_empty_keyboard()
    vk = vk_session.get_api()
    vk.messages.send(peer_id=471188496, message='бот начал свою работу', keyboard=opened_keyboard, random_id=0)
    # vk.messages.send(peer_id=314826563, message='бот специально написал милашке', keyboard=opened_keyboard, random_id=0)
    poll = iter(longpoll.listen())
    for event in poll:
        print(event.type, event.peer_id, event.attachments, event.extra, event.flags, sep='\n', end='\n\n\n')
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if event.from_chat:
                    if event.type == VkEventType.CHAT_UPDATE:
                        text = '''Приветствую вас! Я Бот Кулинарная книга.
Я смогу (когда-нибудь) написать определённый рецепт блюда, 
написать список блюд, у которых есть рецепт в книге,
добавлять в список новые блюда и прочие действия.'''
                        vk.messages.send(peer_id=event.peer_id,
                                         message=text,
                                         keyboard=opened_keyboard,
                                         random_id=0)
                        continue
                    print('Новое сообщение:')
                    print('Для меня от чата', event.chat_id)
                    print('Текст:', event.text)
                    text = event.text.lstrip('[club210739018|@club210739018] ')
                    splitted_event_text = text.split('; ')
                    print(splitted_event_text)
                    if splitted_event_text[0].lower() in ['помощь', 'помогите', 'help']:
                        vk.messages.send(peer_id=event.peer_id,
                                         message=help(),
                                         keyboard=opened_keyboard,
                                         random_id=0)
                        continue
                    for command in commands:
                        if command.get_name() == splitted_event_text[0] == '?случайноеблюдо':  # проверка на ?случайноеблюдо
                            result = command.execute()
                            vk.messages.send(peer_id=event.peer_id,
                                             message=result,
                                             keyboard=opened_keyboard,
                                             random_id=0)
                            break
                        elif command.get_name() == splitted_event_text[0] == '?добавитьблюдо':  # остальные команды
                            try:
                                if len(splitted_event_text) != 1:
                                    result = command.execute(event.user_id, *splitted_event_text[1:])
                                else:
                                    user_text = []
                                    user_id = event.user_id
                                    text = '''добавление блюда. 
пока пользователь не закончит функцию, 
никто не может использовать бота'''
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=text,
                                                     keyboard=create_keyboard(['остановить', 'красный']),
                                                     random_id=0)
                                    for text in ['напишите ' + a for a in ['название блюда',
                                                                           'его ингредиенты',
                                                                           'способ приготовления'
                                                                                                ]]:
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=text,
                                                         keyboard=create_keyboard(['остановить', 'красный']),
                                                         random_id=0)
                                        for event in poll:
                                            if not event.from_me:
                                                if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
                                                    user_text.append(event.text)
                                    print(user_text)
                                    result = command.execute(event.user_id, *user_text)
                            except StopIteration:
                                result = 'функция была прервана, можете вызвать другие функции'
                            # except Exception as e:
                            #     print(e)
                            #     result = 'скорее всего нельзя получить информацию про пользователя'
                            finally:
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=result,
                                                 keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                        elif command.get_name() == splitted_event_text[0] == '?какприготовить':
                            if len(splitted_event_text) != 1:
                                result = command.execute(*splitted_event_text[1:])
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=result,
                                                 keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                            else:
                                user_id = event.user_id
                                text = '''Напишите название блюда. 
(пока пользователь не напишет блюдо,
другие не могут использовать бота)'''
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=text,
                                                 keyboard=create_keyboard(['остановить', 'красный']),
                                                 random_id=0)
                                for event in poll:
                                    if not event.from_me:
                                        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
                                            if event.text == 'остановить':
                                                result = 'функция остановлена, можете использовать меня для ещё чего-то'
                                            else:
                                                result = command.execute(event.text)
                                            break
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=result,
                                                 keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                        elif command.get_name() == splitted_event_text[0] == '?чтоприготовитьиз':
                            if len(splitted_event_text) != 1:
                                result = command.execute(*splitted_event_text[1:])
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=result,
                                                 keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                            else:
                                user_text = []
                                user_id = event.user_id
                                text = f'''Напишите ингредиенты блюда, каждый должен быть в новом сообщении. 
(пока пользователь  @{user_id} не напишет блюдо,
другие не могут использовать бота)'''
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=text,
                                                 keyboard=create_keyboard(['конец', 'белый'], ['/', '/'],
                                                                          ['остановить', 'красный']),
                                                 random_id=0)
                                for event in poll:
                                    if not event.from_me:
                                        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
                                            if event.text.lstrip('[club210739018|@club210739018] ') == 'конец':
                                                user_text = '/'.join(user_text)
                                                result = command.execute(user_text)
                                                vk.messages.send(peer_id=event.peer_id,
                                                                 message=result,
                                                                 keyboard=opened_keyboard,
                                                                 random_id=0)
                                                break
                                            elif event.text.lstrip('[club210739018|@club210739018] ') == '':
                                                result = 'функция была прервана, можете вызвать другие функции'
                                                vk.messages.send(peer_id=event.peer_id,
                                                                 message=text,
                                                                 keyboard=opened_keyboard,
                                                                 random_id=0)
                                                break
                                            else:
                                                user_text.append(event.text.lstrip('[club210739018|@club210739018] '))
                                                text = 'если у вас ещё есть игредиент, то пишите его название, или пишите "конец"'
                                                vk.messages.send(peer_id=event.peer_id,
                                                                 message=text,
                                                                 keyboard=create_keyboard(['конец', 'белый'], ['/', '/'],
                                                                 ['остановить', 'красный']),
                                                                 random_id=0)
                                break
                elif event.from_user:
                    user = vk.users.get(user_id=event.user_id, fields='domain')[0]
                    print('лс')
                    print('Новое сообщение:')
                    print(user)
                    print('Для меня от:', f'{user["first_name"]} {user["last_name"]}: @{user["domain"]}')
                    print('Текст:', event.text)
                    print(event.peer_id)
                    splitted_event_text = event.text.split('; ')
                    print(splitted_event_text)
                    if splitted_event_text[0].lower() in ['start', 'привет', 'вечер в хату']:
                        text = '''Приветствую вас! Я Бот Кулинарная книга.
Я смогу (когда-нибудь) написать определённый рецепт блюда, 
написать список блюд, у которых есть рецепт в книге,
добавлять в список новые блюда и прочие действия.'''
                        vk.messages.send(peer_id=event.peer_id,
                                         message=text,
                                         keyboard=opened_keyboard,
                                         random_id=0)
                    if splitted_event_text[0].lower() in ['помощь', 'помогите', 'help']:
                        vk.messages.send(peer_id=event.peer_id,
                                         message=help(),
                                         keyboard=opened_keyboard,
                                         random_id=0)
                        continue
                    for command in commands:
                        if command.get_name() == splitted_event_text[0] == '?случайноеблюдо':  # проверка на ?случайноеблюдо
                            result = command.execute()
                            vk.messages.send(peer_id=event.peer_id, message=result, keyboard=opened_keyboard,
                                             random_id=0)
                            break
                        elif command.get_name() == splitted_event_text[0] == '?добавитьблюдо':  # остальные команды
                            try:
                                if len(splitted_event_text) != 1:
                                    result = command.execute(event.user_id, *splitted_event_text[1:])
                                else:
                                    user_text = []
                                    user_id = event.user_id
                                    text = '''добавление блюда. 
пока пользователь не закончит функцию, 
никто не может использовать бота'''
                                    vk.messages.send(peer_id=event.peer_id,
                                                     message=text,
                                                     keyboard=create_keyboard(['остановить', 'красный']),
                                                     random_id=0)
                                    for text in ['напишите ' + a for a in ['название блюда',
                                                                           'его ингредиенты',
                                                                           'способ приготовления']]:
                                        vk.messages.send(peer_id=event.peer_id,
                                                         message=text,
                                                         keyboard=create_keyboard(['остановить', 'красный']),
                                                         random_id=0)
                                        for event in poll:
                                            if not event.from_me:
                                                if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
                                                    if event.text == 'остановить':
                                                        raise StopIteration
                                                    else:
                                                        user_text.append(event.text)
                                                        break
                                    print(user_text)
                                    result = command.execute(event.user_id, *user_text)
                            except StopIteration:
                                result = 'функция была прервана, можете вызвать другие функции'
                            except Exception as e:
                                print(e)
                                result = 'скорее всего нельзя получить информацию про пользователя'
                            finally:
                                vk.messages.send(peer_id=event.peer_id, message=result, keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                        elif command.get_name() == splitted_event_text[0] == '?какприготовить':
                            if len(splitted_event_text) != 1:
                                result = command.execute(*splitted_event_text[1:])
                                vk.messages.send(peer_id=event.peer_id, message=result, keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                            else:
                                user_id = event.user_id
                                text = '''Напишите название блюда. 
(пока пользователь не напишет блюдо,
другие не могут использовать бота)'''
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=text,
                                                 keyboard=create_keyboard(['остановить', 'красный']),
                                                 random_id=0)
                                for event in poll:
                                    if not event.from_me:
                                        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
                                            if event.text == 'остановить':
                                                result = 'функция остановлена, можете использовать меня для ещё чего-то'
                                            else:
                                                result = command.execute(event.text)
                                                if result == None:
                                                    result = 'такого рецепта нет в книге'
                                            break
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=result,
                                                 keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                        elif command.get_name() == splitted_event_text[0] == '?чтоприготовитьиз':
                            if len(splitted_event_text) != 1:
                                result = command.execute(*splitted_event_text[1:])
                                vk.messages.send(peer_id=event.peer_id, message=result, keyboard=opened_keyboard,
                                                 random_id=0)
                                break
                            else:
                                user_text = []
                                user_id = event.user_id
                                text = f'''Напишите ингредиенты блюда, каждый должен быть в новом сообщении. 
(пока пользователь  @{user_id} не напишет блюдо,
другие не могут использовать бота)'''
                                vk.messages.send(peer_id=event.peer_id,
                                                 message=text,
                                                 keyboard=create_keyboard(['конец', 'белый'], ['/', '/'],
                                                                          ['остановить', 'красный']),
                                                 random_id=0)
                                for event in poll:
                                    if not event.from_me:
                                        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
                                            if event.text == 'конец':
                                                print(user_text)
                                                user_text = '/'.join(user_text)
                                                result = command.execute(user_text)
                                                vk.messages.send(peer_id=event.peer_id, message=result,
                                                                 keyboard=opened_keyboard,
                                                                 random_id=0)
                                                break
                                            elif event.text == 'остановить':
                                                result = 'функция остановлена, можете использовать меня для ещё чего-то'
                                                vk.messages.send(peer_id=event.peer_id,
                                                                 message=result,
                                                                 keyboard=opened_keyboard,
                                                                 random_id=0)
                                                break
                                            else:
                                                user_text.append(event.text)
                                                text = 'если у вас ещё есть игредиент, то пишите его название, или пишите "конец"'
                                                vk.messages.send(peer_id=event.peer_id,
                                                                 message=text,
                                                                 keyboard=create_keyboard(['конец', 'белый'],
                                                                                          ['/', '/'],
                                                                                          ['остановить', 'красный']),
                                                                 random_id=0)


class CookingBot:
    def __init__(self, token):
        self.token = token
        self.init()

    def init(self):
        db_session.global_init("db/test_cooking.db")
        self.vk_session = VkApi(
            token=self.token)
        add_m = AddMeal(self, '?добавитьблюдо', 'добавление блюда в базу данных')
        how_to_pr = HowToPrepare(self, '?какприготовить', 'получение рецепта блюда')
        what_to_cook = WhatToCookFrom(self, '?чтоприготовитьиз', 'получение названия блюда, которое можно сделать из \
                                                                 введенных ингридиентов')
        help = Help(self, 'help', 'информация о командах')
        rand_meal = RandomMeal(self, '?случайноеблюдо', 'получение названия случайного блюда из базы данных')
        longpoll = VkLongPoll(self.vk_session)
        print('работаем')
        work_bot(longpoll, self.vk_session, add_m, how_to_pr, what_to_cook, rand_meal, help)


if __name__ == '__main__':
    bot = CookingBot(token='1960805a354085e3eff3b7604706f98fb505669be7f68e3564080a4b19c5efb032c8de2530676593c891f')
    vk = bot.vk_session.get_api()
    vk.messages.send(peer_id=471188496,
                     message='бот прекратил свою работу',
                     random_id=0)
