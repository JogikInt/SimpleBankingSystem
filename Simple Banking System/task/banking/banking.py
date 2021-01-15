# JetBrains Academy Simple Banking System project. Solution by Evgeniy Svirin

from random import randint
import sqlite3


class BankingSystem:
    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        try:  # trying to create the card table
            self.cur.execute('CREATE TABLE card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER '
                             'DEFAULT 0);')
            self.conn.commit()
        except sqlite3.OperationalError:  # if the table already exists, skip the step
            pass
        self.start_menu()

    def start_menu(self):
        user_input = input('1. Create an account\n2. Log into account\n0. Exit\n')
        if user_input == '0':
            print('\nBye')
            quit()
        elif user_input == '1':
            self.db_card_add()
        elif user_input == '2':
            self.login()
        else:
            print('Wrong input!')
        self.start_menu()

    def db_card_add(self):
        card_number = self.luhn_card_create()  # we create the card number accorfing to Luhn algorithm
        pin = str(randint(1, 9999)).zfill(4)
        self.cur.execute(f'INSERT INTO card (number, pin) VALUES ({card_number}, {pin});')
        self.conn.commit()
        print(f'\nYour card has been created\nYour card number:\n{card_number}\nYour card PIN:\n{pin}\n')

    def login(self):
        card_number = input('\nEnter your card number:\n')
        pin = input('Enter your PIN:\n')
        if self.check_login(card_number, pin):
            print('\nYou have successfully logged in!\n')
            self.logged_in_menu(card_number)
        print('\nWrong card number or PIN!\n')
        self.start_menu()

    def check_login(self, card_number, pin):  # to check login, we look for the entry with the provided number and pin
        self.cur.execute(f'SELECT id FROM card WHERE number = {card_number} AND pin = {pin};')
        return bool(self.cur.fetchall())

    def logged_in_menu(self, card_number):
        user_input = input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n')
        if user_input == '0':
            print('\nBye')
            quit()
        elif user_input == '1':
            print(f'\nBalance: {self.check_balance(card_number)}\n')
        elif user_input == '2':
            self.add_income(card_number)
        elif user_input == '3':
            self.transfer(card_number)
        elif user_input == '4':
            self.close_account(card_number)
            self.start_menu()
        elif user_input == '5':
            self.start_menu()
        else:
            print('Wrong input!')
        self.logged_in_menu(card_number)

    def check_balance(self, card_number):
        self.cur.execute(f'SELECT balance FROM card WHERE number = {card_number};')
        return self.cur.fetchall()[0][0]

    def add_income(self, card_number):
        amount = int(input('Enter income:\n'))
        self.change_balance(card_number, amount)
        print('Income was added!')

    def transfer(self, card_number):
        target = input('Enter card number:\n')
        if not self.luhn_card_check(target):  # check whether card number is in accordance with the Luhn rule
            print('Probably you made a mistake in the card number. Please try again!')
        elif target == card_number:  # and if the target card number is not identical to the source card
            print('You can\'t transfer money to the same account!\n')
        elif self.cur.execute(f'SELECT id FROM card WHERE number = {target};').fetchall():
            # ask for the amount to transfer and check whether the input is positive integer
            try:
                amount = int(input('Enter how much money you want to transfer:\n'))
                if amount <= 0:
                    print('Input should be a positive integer')
                    self.logged_in_menu(card_number)
                # next check whether the balance is enough to transfer the required amount
                elif self.cur.execute(f'SELECT id FROM card WHERE number = {card_number} '
                                      f'AND balance >= {amount};').fetchall():
                    self.change_balance(card_number, -amount)
                    self.change_balance(target, amount)
                    print('Success!')
                else:
                    print('Not enough money!')
            except ValueError:
                print('Input should be a positive integer')
        else:
            print('Such a card does not exist.')

    def change_balance(self, card_number, amount):
        self.cur.execute(f'''UPDATE card
                SET balance = balance + {amount}
                WHERE number = {card_number};''')
        self.conn.commit()

    def close_account(self, card_numbner):
        self.cur.execute(f'DELETE FROM card WHERE number = {card_numbner};')
        self.conn.commit()
        print('The account has been closed!')

    @staticmethod
    def luhn_card_create():
        card_number = [int(x) for x in list('4000000') + [str(randint(0, 9)) for _ in range(8)]]
        card_digits = [card_number[x] * 2 if x % 2 == 0 else card_number[x] for x in range(len(card_number))]
        card_digits = [x - 9 if x > 9 else x for x in card_digits]
        checksum = 10 - (sum(card_digits) % 10) if sum(card_digits) % 10 != 0 else 0
        card_number.append(checksum)
        return ''.join(list(map(str, card_number)))

    @staticmethod
    def luhn_card_check(card_number):
        card_digits = [int(x) for x in card_number]
        checksum = card_digits.pop(-1)
        card_digits = [card_digits[x] * 2 if x % 2 == 0 else card_digits[x] for x in range(len(card_digits))]
        card_digits = [x - 9 if x > 9 else x for x in card_digits]
        return (sum(card_digits) + checksum) % 10 == 0


if __name__ == '__main__':
    banking_system = BankingSystem()
