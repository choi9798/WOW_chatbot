import sys

import telegram
from flask import Flask, request
from transitions import State
from transitions.extensions import GraphMachine as Machine

class Library(object):
    flag = True
    book_name = ""
    room_thing = ""
    def print_menu(self):
        guide = "歡迎來到WOW圖書館ChatBot\n"
        guide += "請選擇想要的服務(輸入數字代號)\n"
        guide += "1. 新書推介\n"
        guide += "2. 書本預約\n"
        guide += "3. 自修室預約\n"
        guide += "4. 查看已預約的書或已預約的自修室\n"
        guide += "在任何狀態下可輸入exit()回到主目錄"
        return guide
    def recom(self):
        sh = "本月推薦書籍\n"
        sh += "AA-134 二十四個比利\n"
        sh += "FJ-095 你以為你以為的就是你以為的嗎\n"
        sh += "FJ-334 戰爭的藝術\n"
        return sh
    def menutobook(self):
        sh = "請輸入想預約書本的編號"
        return sh
    def menutoroom(self):
        sh = "請輸入預約時間\n"
        sh += "例： 1/15 15:00"
        return sh
    def menutoinfo(self):
        sh = "1. 查看已預約的書本\n"
        sh += "2. 查看已預約的自修室"
        return sh
    def booktoconfirm(self, name):
        self.book_name = name
        sh =  "你輸入的書本為：" + name + "\n"
        sh += "1. 確定\n"
        sh += "2. 返回"
        return sh
    def bookconfirm_after(self):
        file = open("book.txt", "a")
        file.write(self.book_name+"\n")
        file.close()
        sh = self.book_name + "預約成功\n"
        sh += "繼續預約書本？\n"
        sh += "1. 是\n"
        sh += "2. 否"
        return sh
    def roomtoconfirm(self, room):
        self.room_thing = room
        sh = "你想預約的時間為：" + room + "\n"
        sh += "1. 確定\n"
        sh += "2. 返回"
        return sh
    def roomconfirm_after(self):
        file = open("room.txt", "a")
        file.write(self.room_thing+"\n")
        file.close()
        sh = self.room_thing + "\n預約成功\n"
        sh += "繼續預約？\n"
        sh += "1. 是\n"
        sh += "2. 否"
        return sh
    def showbook(self):
        sh = ""
        file = open("book.txt", "r")
        for line in file:
            sh += line
        file.close()
        return sh
    def showroom(self):
        sh = ""
        file = open("room.txt", "r")
        for line in file:
            sh += line
        file.close()
        return sh

app = Flask(__name__)
bot = telegram.Bot(token='536502197:AAGB1eRfdmat7MXcD4P77NI5-XTTDyg7Cto')

lib = Library()
states = ['menu', 'book_borrowing', 'book_confirm', 'bookafter_confirm', 'room_booking', 'room_confirm', 'roomafter_confirm', 'info', 'book_info', 'room_info']
transitions = [
               ['goto_book_bor', 'menu', 'book_borrowing'], #menu
               ['goto_room_bok', 'menu', 'room_booking'],
               ['goto_info', 'menu', 'info'],
               
               ['book_entered', 'book_borrowing', 'book_confirm'], #book_borrow
               ['book_confirmed', 'book_confirm', 'bookafter_confirm'],
               ['back_book_bor', 'bookafter_confirm', 'book_borrowing'],
               
               ['room_entered', 'room_booking', 'room_confirm'], #room_booking
               ['room_confirmed', 'room_confirm', 'roomafter_confirm'],
               ['back_room_bok', 'roomafter_confirm', 'room_booking'],
               
               ['quit', '*', 'menu']
        ]


machine = Machine(model = lib, states = states, transitions = transitions, initial = 'menu', title = 'WOW chatbot diagram')

lib.get_graph().draw('state.png', prog = 'dot')

def _set_webhook():
    status = bot.set_webhook('https://13651afa.ngrok.io/hook')
    if not status:
        print('Webhook setup failed')
        sys.exit(1)


@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        text = update.message.text
        update.message.reply_text(test(text))
    
    return 'ok'

def test(a):
    if lib.flag == True:
        lib.flag = False
        return lib.print_menu()

    if lib.state == "menu":
        if a == "1":
            return lib.recom()
        elif a == "2":
            lib.goto_book_bor()
            return lib.menutobook()
        elif a == "3":
            lib.goto_room_bok()
            return lib.menutoroom()
        elif a == "4":
            lib.goto_info()
            return lib.menutoinfo()
        else:
            return "輸入了錯誤代號"

    if lib.state == "book_borrowing":
        if a == "exit()":
            lib.quit()
            return lib.print_menu()
        else:
            lib.book_entered()
            return lib.booktoconfirm(a)

    if lib.state == "book_confirm":
        if a == "1":
            lib.book_confirmed()
            return lib.bookconfirm_after()
        elif a == "2" or a == "exit()":
            lib.quit()
            return lib.print_menu()
        else:
            return "輸入了錯誤代號"

    if lib.state == "bookafter_confirm":
        if a == "1":
            lib.back_book_bor()
            return lib.menutobook()
        elif a == "exit()" or a == "2":
            lib.quit()
            return lib.print_menu()
        else:
            return "輸入了錯誤代號"

    if lib.state == "room_booking":
        if a == "exit()":
            lib.quit()
            return lib.print_menu()
        else:
            lib.room_entered()
            return lib.roomtoconfirm(a)
    if lib.state == "room_confirm":
        if a == "1":
            lib.room_confirmed()
            return lib.roomconfirm_after()
        elif a == "2" or a == "exit()":
            lib.quit()
            return lib.print_menu()
        else:
            return "輸入了錯誤代號"
    if lib.state == "roomafter_confirm":
        if a == "1":
            lib.back_room_bok()
            return lib.menutoroom()
        elif a == "exit()" or a == "2":
            lib.quit()
            return lib.print_menu()
        else:
            return "輸入了錯誤代號"

    if lib.state == "info":
        if a == "1":
            return lib.showbook() + "\n\n" + lib.menutoinfo()
        elif a == "2":
            return lib.showroom() + "\n\n" + lib.menutoinfo()
        elif a == "exit()":
            lib.quit()
            return lib.print_menu()
        else:
            return "輸入了錯誤的代號"



if __name__ == "__main__":
    file = open("book.txt", "a")
    file.close()
    file = open("room.txt", "a")
    file.close()
    _set_webhook()
    app.run(port=8000)
