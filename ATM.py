from datetime import datetime
import requests
from bs4 import BeautifulSoup as Bs

"""
This program is imitation system Atm, use OOP. 
"""


class Atm:
    """
    class Atm is control for balance ATM.
    """
    __balance = 3000

    def __add__(self, other):
        self.__balance = self.__balance + other

    def __sub__(self, other):
        self.__balance = self.__balance - other

    @property
    def get_balance(self):
        return self.__balance

    @get_balance.setter
    def get_balance(self, value):
        self.__balance = self.__balance - value

    @property
    def put_money(self):
        return self.__balance

    @put_money.setter
    def put_money(self, value):
        self.__balance = self.__balance + value


class ValidUser:
    """Valid users"""

    def __set_name__(self, owner, name):
        self.__name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.__name]

    def __set__(self, instance, value):
        if self.__name == '_balance':
            if isinstance(value, (int, float)) and value > 0:
                instance.__dict__[self.__name] = value
            else:
                raise TypeError('Balance must be integer or float and more than 0')

        if self.__name == '__password':
            if isinstance(value, int) and 10000 > value > 999:
                instance.__dict__[self.__name] = value
            else:
                raise TypeError('Password must be integer and more than 999 and less, 10000')


class User:
    _balance = ValidUser()
    __password = ValidUser()
    counter = 0
    user_currency_money = {}

    @staticmethod
    def make_dict_w(operation):
        name_file = operation + '.json'
        with open(name_file, 'a', encoding="utf-8") as f:
            date_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            dct = dict()
            dct[date_time] = operation
            f.write(str(f'{dct},\n'))

    def __init__(self, balance, password):
        self._balance = balance
        self.__password = password

    def __add__(self, other):
        self._balance = self._balance + other

    def __sub__(self, other):
        self._balance = self._balance - other

    def get_money(self, money):
        self.__sub__(money)
        print('Pick up your money!')
        self.make_dict_w('get_money')

    def put_money(self, money):
        self.__add__(money)
        print('Insert your money into the bill acceptor!')
        self.make_dict_w('put_money')

    def exchange_rate(self, currency):
        self.make_dict_w('exchange_rate')
        rate = ExchangeRate(currency)
        return rate.return_rate()

    def exchange_currency(self, currency, money):
        self.make_dict_w('exchange_currency')
        rate = ExchangeCurrency(currency)
        rate.change(money)
        if rate.currency in self.user_currency_money:
            self.user_currency_money[rate.currency] += rate.change(money)
        else:
            self.user_currency_money[rate.currency] = rate.change(money)
        self.make_dict_w(f'change, {currency} = {rate.change(money)}')

    @property
    def balance(self):
        return self._balance


class ExchangeRate:
    """
    parse exchange rate
    """
    url_usd = 'https://www.google.com/search?q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D0%B3%D1%80%D0%' \
              'B8%D0%B2%D0%BD%D0%B5&oq=%D0%B4%D0%BE%D0%BB%D0%B0%D1%80+%D0%BA&aqs=chrome.2.69i57j35i39j0i10i' \
              '433i512j0i512l2j0i10i131i433i512j0i10i433i512j69i61.10602j1j7&sourceid=chrome&ie=UTF-8'
    url_euro = 'https://www.google.com/search?q=%D0%B5%D0%B2%D1%80%D0%BE+%D0%BA+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%' \
               'B5&sxsrf=ALiCzsaoRgta6SKYzrKY86_7XYU3XXckbA%3A1670582903166&ei=dxKTY97TCc-G9u8P0v2toAo&oq=edhj+%D0%B' \
               'A+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B5&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQARgAMgcIABCABBANMgcIABCABBANMgcI' \
               'ABCABBANMgcIABCABBANMgcIABCABBANMgcIABCABBANMgcIABCABBANMgcIABCABBANMgcIABCABBANMgcIABCABBANOgoIABBH' \
               'ENYEELADOg0IABBHENYEEMkDELADOggIABCSAxCwAzoSCC4QxwEQ0QMQyAMQsAMQQxgBOgcIIxCxAhAnOgYIABAHEB46BAgAEEM' \
               '6CAgAEAUQBxAeOgUIABCiBDoHCAAQHhCiBEoECEEYAEoECEYYAFC6DVjYQGDyUWgCcAF4AIABfYgByweSAQM4LjKYAQCgAQHIAQv' \
               'AAQHaAQQIARgI&sclient=gws-wiz-serp'
    url_pln = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B7%D0%BB%D0%BE%D1%82%D0%BE%D0%B3%D0%BE' \
              '+%D0%BA+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B5&sxsrf=ALiCzsZUnG17rykKIGNhlqQKL6y5UcrzRQ%3A1670583861527&' \
              'ei=NRaTY4LtH9jQqwGTvJuQCw&oq=+%D0%BA+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B5&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQ' \
              'ARgDMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMg' \
              'YIABAHEB46DQgAEEcQ1gQQyQMQsAM6CggAEEcQ1gQQsAM6CAgAEJIDELADOgcIABCwAxBDOgcIIxCxAhAnOggIABAHEB4QCkoECEEY' \
              'AEoECEYYAFCcC1j6DmCRMWgCcAF4AIABXIgB3AKSAQE0mAEAoAEByAEKwAEB&sclient=gws-wiz-serp'

    url_gbp = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D1%84%D1%83%D0%BD%D1%82%D0%B0+%D0%BA+%D0%' \
              'B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B5&sxsrf=ALiCzsZn1szzy0O0_JByYYIYFUKr93f7bw%3A1670584155785&ei=WxeTY5vH' \
              'L-L3qwHh-ayYBQ&oq=%D0%BA%D1%83%D1%80%D1%81++%D0%BA+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B5&gs_lcp=Cgxnd' \
              '3Mtd2l6LXNlcnAQAxgFMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMgYIABAHEB4yBggAEAcQHjIGCAAQBxAeMgYIABAHEB4yBggA' \
              'EAcQHjIGCAAQBxAeMgYIABAHEB46CggAEEcQ1gQQsAM6BwgAELADEEM6BwgjELECECc6BQgAEIAESgQIQRgASgQIRhgAULgMWP0VY' \
              'NlCaAFwAXgAgAFgiAGABZIBATeYAQCgAQHIAQrAAQE&sclient=gws-wiz-serp'

    def __init__(self, currency):
        self.currency = currency

    def return_rate(self):
        if self.currency == 'usd':
            url = self.url_usd
        elif self.currency == 'euro':
            url = self.url_euro
        elif self.currency == 'pln':
            url = self.url_pln
        elif self.currency == 'gbp':
            url = self.url_gbp
        else:
            print('Incorrect currency')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36'}
        responce = requests.get(url, headers=headers)
        html = Bs(responce.content, 'html.parser')
        cur = html.findAll('span', {'class': 'DFlfde SwHCTb'})
        return float(cur[0].text.replace(',', '.'))


class ExchangeCurrency(ExchangeRate):
    def change(self, amount):
        cur_money = amount / self.return_rate()
        return cur_money


password_user = 1111
count_try = 0
while count_try < 3:
    balance = float(input('Input balance.'))
    password = int(input('Input your password.'))
    if password == password_user:
        user = User(balance, password)
        atm = Atm()
        while True:
            choise_op = input('You can use those operation: \n'
                              '1. Withdraw cash.\n'
                              '2. Put money on the card.\n'
                              '3. View exchange rate.\n'
                              '4. Exchange currency.\n'
                              'Or you can exit.\n'
                              'input number (1,2,3,4) or exit.\n')
            if choise_op == '1':
                withdraw_num = float(input('How much do you want to withdraw cash?\n'))
                if user.balance > withdraw_num and atm.get_balance > withdraw_num:
                    user.get_money(withdraw_num)
                    atm.get_balance = withdraw_num
                    print(f'Atm balance {atm.get_balance}')
                    print(f'User balance {user.balance}')
            elif choise_op == '2':
                put_cash = float(input('Hoe much do you want to put money?\n'))
                user.put_money(put_cash)
                atm.put_money = put_cash
                print(f'Atm balance {atm.get_balance}')
                print(f'User balance {user.balance}')
            elif choise_op == '3':
                currency = input('What currency do you want to know rate? You can view those currency:\n'
                                 'usd - American dollar\n'
                                 'euro - Euro \n'
                                 'pln - Poland zloty\n'
                                 'gbp - Great Britain pound\n').lower()
                print(f'{currency.upper()} - {user.exchange_rate(currency)}')
            elif choise_op == '4':
                currency = input('What currency do you want to know rate? You can view those currency:\n'
                                 'usd - American dollar\n'
                                 'euro - Euro \n'
                                 'pln - Poland zloty\n'
                                 'gbp - Great Britain pound\n').lower()
                amount = float(input('How much do tou want to change?'))
                if amount < user.balance:
                    user.exchange_currency(currency, amount)
                print(f'Currency : {user.user_currency_money}')
            elif choise_op == "exit":
                print('Thank you for to using our system!')
                count_try = 4
                break
    else:
        count_try += 1
        print('Incorrect password. Try again')
