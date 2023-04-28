import telebot
from telebot import types
from PIL import Image, ImageDraw

bot = telebot.TeleBot('5610082254:AAF0SoX8VoY7aCYGMT3jPD8bktFTJpoeifg')#токен
board = [' ' for x in range(10)] #поле
gameon = False #запущена ли игра
games = 0 #количество сыгранных игр
s = '3'#размер поля
nu = 2 #номер удаляемого сообщения, используется в playermove и player_move
run = True #прерывает цикл в playermove и player_move


@bot.message_handler(commands=['start'])
def start(message): #краткое описание бота
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    a = types.KeyboardButton('/play')
    b = types.KeyboardButton('/size 3')
    c = types.KeyboardButton('/size 4')
    markup.row(a)
    markup.row(b, c)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Этот бот сыграет с вами '
                                      f'в Крестики Нолики. Вы можете выбрать размер поля с помощью /size'
                                      f' (/size 3 или /size 4).  '
                                      f'Введите /play чтобы начать игру, /help чтобы посмотреть правила. ',
                                        reply_markup=markup)


@bot.message_handler(commands=['stop'])
def stop(message):#прерывание игры игроком
    global gameon
    gameon = False
    delete(message, 2)
    bot.send_message(message.chat.id, "Игра завершена")


@bot.message_handler(commands=['help'])
def help(message):#полное описание бота
    bot.send_message(message.chat.id, 'Этот бот умеет играть в Крестики Нолики. '
                                      'Правила: '
                                      'Игрок и компьютер по очереди ставят свои фишки на поле 3х3. '
                                      'Фишки - крестики и нолики. Первыми ходят крестики. '
                                      'В каждой новой игре игрок и бот меняются фишками. '
                                      'Цель игры: собрать три свои фишки по горизонтали, вертикали или диагонали первым.'
                                      ' Введите /play чтобы начать и /stop чтобы закончить игру. '
                                      'Чтобы изменить размер поля введите /size <3 или 4>. ')


def change_size(n):
    global s, board
    s = n


@bot.message_handler(commands=['size'])
def size(message):#установка размера поля
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    a = types.KeyboardButton('/play')
    b = types.KeyboardButton('/size 3')
    c = types.KeyboardButton('/size 4')
    markup.row(a)
    markup.row(b, c)
    if not gameon:
        try:
            if message.text[6:8] == '3' or message.text[6:8] == '4':
                change_size(message.text[6:8])
                bot.send_message(message.chat.id, f'Установлен размер поля {message.text[6:8]}', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Неверный размер. Доступен только 3 и 4', reply_markup=markup)
        except:
            bot.send_message(message.chat.id, 'Неверный формат. Введите /size 3 или /size 4', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Размер поля изменить нельзя. Сначала закончите игру')


@bot.message_handler(commands=['play'])
def play(message):#
    global s
    global games
    global gameon
    global board
    gameon = True
    if int(s) == 4:
        board = [' ' for x in range(17)]
    else:
        board = [' ' for x in range(10)]
    bot.send_photo(message.chat.id, draw_board(board, s))
    if games % 2 == 0:#если первым ходит игрок
        while not (isboardfull(board)):
            if not (iswinner(board, 'O')):
                if s == '3':
                    playermove(message)
                else:
                    player_move(message)
            else:
                bot.send_message(message.chat.id, "Простите, бот выиграл этот раунд!")
                end_game(message)
                break

            if not (iswinner(board, 'X')):
                if size == '3':
                    move = computermove()
                else:
                    move = computer_move()
                if move == 0:
                    bot.send_message(message.chat.id, "Ничья!")
                    end_game(message)
                    break
                else:
                    insertletter('O', move)
                    bot.send_message(message.chat.id, f"Бот поставил 'O' в ячейку {move} :")
            else:
                bot.send_message(message.chat.id, f"{message.from_user.first_name}, вы выиграли!")
                end_game(message)
                break
            if isboardfull(board):
                bot.send_message(message.chat.id, 'Ничья!')
                end_game(message)
                break
            bot.send_photo(message.chat.id, draw_board(board, s))
    else:#если первым ходит бот
        while not (isboardfull(board)):
            if not (iswinner(board, 'O')):
                if size == '3':
                    move = computermove()
                else:
                    move = computer_move()
                if move == 0:
                    bot.send_message(message.chat.id, "Ничья!")
                    end_game(message)
                    break
                else:
                    insertletter('X', move)
                    bot.send_message(message.chat.id, f"Бот поставил 'X' в ячейку {move} :")
            else:
                bot.send_message(message.chat.id, f"{message.from_user.first_name}, вы выиграли!"
                                                  f" Чтобы сыграть ещё раз введите /play")
                end_game(message)
                break

            if isboardfull(board) and not iswinner(board, 'X'):
                bot.send_message(message.chat.id, "Ничья!")
                end_game(message)
                break
            bot.send_photo(message.chat.id, draw_board(board, s))

            if not (iswinner(board, 'X')):
                if s == '3':
                    playermove(message)
                else:
                    player_move(message)
            else:
                bot.send_message(message.chat.id, "Простите, бот выиграл этот раунд!")
                end_game(message)
                break

    games += 1


def iswinner(bo, le):#проверка на победителя
    global s
    if s == '3':
        return ((bo[7] == le and bo[8] == le and bo[9] == le) or
                (bo[4] == le and bo[5] == le and bo[6] == le) or
                (bo[1] == le and bo[2] == le and bo[3] == le) or
                (bo[7] == le and bo[4] == le and bo[1] == le) or
                (bo[8] == le and bo[5] == le and bo[2] == le) or
                (bo[9] == le and bo[6] == le and bo[3] == le) or
                (bo[7] == le and bo[5] == le and bo[3] == le) or
                (bo[9] == le and bo[5] == le and bo[1] == le))
    else:
        return ((bo[1] == le and bo[2] == le and bo[3] == le and bo[4] == le) or
                (bo[5] == le and bo[6] == le and bo[7] == le and bo[8] == le) or
                (bo[9] == le and bo[10] == le and bo[11] == le and bo[12] == le) or
                (bo[13] == le and bo[14] == le and bo[15] == le and bo[16] == le) or
                (bo[1] == le and bo[5] == le and bo[9] == le and bo[13] == le) or
                (bo[2] == le and bo[6] == le and bo[10] == le and bo[14] == le) or
                (bo[3] == le and bo[7] == le and bo[11] == le and bo[15] == le) or
                (bo[4] == le and bo[8] == le and bo[12] == le and bo[16] == le) or
                (bo[1] == le and bo[6] == le and bo[11] == le and bo[16] == le) or
                (bo[4] == le and bo[7] == le and bo[10] == le and bo[13] == le))


def isboardfull(board):
    if board.count(' ') > 1:
        return False
    else:
        return True


def selectrandom(li):
    import random
    ln = len(li)
    r = random.randrange(0, ln)
    return li[r]


def draw_board(board, s):#рисование поля
    s = int(s)
    im = Image.new("RGB", (s * 100, s * 100), (255, 255, 255))
    drawer = ImageDraw.Draw(im)

    for i in range(s):
        for j in range(s):
            drawer.rectangle(((100 * j, 100 * i), ((j + 1) * 100 - 1, (i + 1) * 100 - 1)), (255, 255, 255), (0, 0, 0),
                             2)
            if s == 3: index = i * 3 + j + 1
            else: index = i * 4 + j + 1
            if board[index] == 'X':
                drawer.line(((100 * j + 10, 100 * i + 10), ((j + 1) * 100 - 10, (i + 1) * 100 - 10)), (0, 0, 0), 4)
                drawer.line((((j + 1) * 100 - 10, 100 * i + 10), (100 * j + 10, (i + 1) * 100 - 10)), (0, 0, 0), 4)
            elif board[index] == 'O':
                drawer.ellipse(((100 * j + 10, 100 * i + 10), ((j + 1) * 100 - 10, (i + 1) * 100 - 10)),
                               (255, 255, 255), (0, 0, 0), 4)
    im.save('rez.png')
    file = open('rez.png', 'rb')
    return file


def insertletter(letter, pos):
    board[pos] = letter


def spaceisfree(pos):
    return board[pos] == ' '


def delete(message, n):#удаление лишних картинок
    global games
    if games % 2 == 1 and board.count('O') == 1:
        bot.delete_message(message.chat.id, message.message_id - n - 2)
    bot.delete_message(message.chat.id, message.message_id - n)


def playermove(message):#ход игрока для поля 3 на 3
    global games, run, nu
    run = True
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    first, second, fird = types.KeyboardButton('1'), types.KeyboardButton('2'), types.KeyboardButton('3')
    fourth, fith, sixth = types.KeyboardButton('4'), types.KeyboardButton('5'), types.KeyboardButton('6')
    seventh, eighth, ninth = types.KeyboardButton('7'), types.KeyboardButton('8'), types.KeyboardButton('9')
    markup.row(first, second, fird)
    markup.row(fourth, fith, sixth)
    markup.row(seventh, eighth, ninth)

    def change():
        global run
        run = False

    def get_letter():
        if games % 2 == 0:
            return 'X'
        elif games % 2 == 1:
            return 'O'

    bot.send_message(message.chat.id, f"Пожалуйста, выберите ячейку чтобы поставить {get_letter()} (1-9): ",
                     reply_markup=markup)
    nu = 2

    while run:
        @bot.message_handler()
        def message_input_step(message):
            global nu
            if gameon and s == '3':
                try:
                    move = int(message.text)
                    if 10 > move > 0:
                        if spaceisfree(move):
                            insertletter(get_letter(), move)
                            delete(message, nu)
                            change()
                        else:
                            nu += 2
                            bot.send_message(message.chat.id, "Простите, это место занято!", reply_markup=markup)
                    else:
                        nu += 2
                        bot.send_message(message.chat.id, f"Пожалуйста, введите число от 1 до 9!", reply_markup=markup)
                except ValueError:
                    nu += 2
                    bot.send_message(message.chat.id, "Пожалуйста, введите число", reply_markup=markup)
            elif not gameon:
                bot.send_message(message.chat.id, "Игра не запущена", reply_markup=markup)


def player_move(message):#ход игрока для поля 4 на 4
    global run, gameon, nu
    run = True
    nu = 2
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    first, second, fird, fourth = types.KeyboardButton('1'), types.KeyboardButton('2'), types.KeyboardButton('3'),\
                                  types.KeyboardButton('4')
    fith, sixth, seventh, eighth = types.KeyboardButton('5'), types.KeyboardButton('6'), types.KeyboardButton('7'),\
                                   types.KeyboardButton('8')
    ninth, tenth, elev, tw = types.KeyboardButton('9'), types.KeyboardButton('10'), types.KeyboardButton('11'),\
                             types.KeyboardButton('12')
    thirt, fort, fift, six = types.KeyboardButton('13'), types.KeyboardButton('14'), types.KeyboardButton('15'), \
                             types.KeyboardButton('16')
    markup.row(first, second, fird, fourth)
    markup.row(fith, sixth, seventh, eighth)
    markup.row(ninth, tenth, elev, tw)
    markup.row(thirt, fort, fift, six)

    def change():
        global run
        run = False

    def get_letter():
        if games % 2 == 0:
            return 'X'
        elif games % 2 == 1:
            return 'O'

    bot.send_message(message.chat.id, f"Пожалуйста, выберите ячейку чтобы поставить '{get_letter()}' (1-16): ",
                     reply_markup=markup)

    while run:
        @bot.message_handler()
        def message_input_step(message):
            global nu
            try:
                move = int(message.text)
                if 17 > move > 0:
                    if spaceisfree(move):
                        insertletter(get_letter(), move)
                        delete(message, nu)
                        change()
                    else:
                        nu += 2
                        bot.send_message(message.chat.id, "Простите, это место занято!")
                else:
                    nu += 2
                    bot.send_message(message.chat.id, f"Пожалуйста, введите число от 1 до 16!")
            except ValueError:
                nu += 2
                bot.send_message(message.chat.id, "Пожалуйста, введите число")


def computermove():#ход бота для поля 3 на 3
    possiblemoves = [x for x, letter in enumerate(board) if letter == ' ' and x != 0]
    move = 0

    for let in ['O', 'X']:
        for i in possiblemoves:
            boardcopy = board[:]
            boardcopy[i] = let
            if iswinner(boardcopy, let):
                move = i
                return move

    cornersopen = []
    for i in possiblemoves:
        if i in [1, 3, 7, 9]:
            cornersopen.append(i)

    if len(cornersopen) > 0:
        move = selectrandom(cornersopen)
        return move

    if 5 in possiblemoves:
        move = 5
        return move

    edgesppen = []
    for i in possiblemoves:
        if i in [2, 4, 6, 8]:
            edgesppen.append(i)

    if len(edgesppen) > 0:
        move = selectrandom(edgesppen)

    return move


def computer_move():#ход бота для поля 4 на 4
    possiblemoves = [x for x, letter in enumerate(board) if letter == ' ' and x != 0]
    move = 0

    for let in ['O', 'X']:
        for i in possiblemoves:
            boardcopy = board[:]
            boardcopy[i] = let
            if iswinner(boardcopy, let):
                move = i
                return move

    cornersopen = []
    for i in possiblemoves:
        if i in [1, 4, 13, 16]:
            cornersopen.append(i)

    if len(cornersopen) > 0:
        move = selectrandom(cornersopen)
        return move

    if 6 in possiblemoves:
        move = 6
        return move

    edgesppen = []
    for i in possiblemoves:
        if i in [2, 3, 5, 7, 8, 9, 10, 11, 12, 14, 15]:
            edgesppen.append(i)

    if len(edgesppen) > 0:
        move = selectrandom(edgesppen)

    return move


def end_game(message):#конец игры в общем случае
    global gameon
    bot.send_photo(message.chat.id, draw_board(board, s))
    gameon = False
    bot.delete_message(message.chat.id, message.message_id - 3)


bot.polling(none_stop=True)

#запускать лучше на дебаггере