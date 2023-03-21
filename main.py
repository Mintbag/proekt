import sys
import sqlite3
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5 import QtWidgets, uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QMainWindow
import hashlib
import os.path
from pyuac import main_requires_admin
import time
import threading
import subprocess


@main_requires_admin
def main():
    pass


if __name__ == "__main__":
    main()


def thread_function(name, arg1, arg2):
    hosts = r'C:\Windows\System32\drivers\etc\hosts'
    redirect_url = '127.0.0.1'
    with open(hosts, 'r+') as f:
        src = f.readlines()
        f.seek(0)

        for line in src:
            if name not in line:
                f.write(line)
            f.truncate()
    time.sleep(int(arg1) * 60)
    subprocess.call("TASKKILL /F /IM chrome.exe", shell=True)
    subprocess.call("TASKKILL /F /IM firefox.exe", shell=True)
    subprocess.call("TASKKILL /F /IM edge.exe", shell=True)
    with open(hosts, 'r+') as f:
        f.read()
        f.write(f'{redirect_url} www.{name}\n')
        f.write(f'{redirect_url} {name}\n')
    time.sleep(int(arg2) * 60)
    with sqlite3.connect('database.db') as db:
        curs = db.cursor()
        curs.execute(f"UPDATE progs SET Permission='yes' WHERE Site=?", (name,))


hosts = r'C:\Windows\System32\drivers\etc\hosts'
redirect_url = '127.0.0.1'


with sqlite3.connect('database.db') as db:
    curs = db.cursor()
    curs.execute(f'CREATE TABLE IF NOT EXISTS progs(Site TEXT PRIMARY KEY, Using_time TEXT, Rest_time TEXT,'
                 f' Permission TEXT)')
    db.commit()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('introtrue.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run_2)
        self.count = 0
        self.secondWin = None
        db = QSqlDatabase.addDatabase('QSQLITE')

        # 2. Вызовите setDatabaseName(), чтобы установить имя базы данных, которое будет использоваться.
        #    Вам нужно только написать путь, а имя файла заканчивается на .db
        #   (если база данных уже существует, используйте базу данных; если она не существует,
        #    будет создана новая);
        db.setDatabaseName('database.db')  # !!! ваша db

        # 3. Вызовите метод open(), чтобы открыть базу данных.
        #    Если открытие прошло успешно, оно вернет True, а в случае неудачи - False.
        db.open()

        # Создайте модель QSqlTableModel и вызовите setTable(),
        # чтобы выбрать таблицу данных для обработки.
        self.model = QSqlTableModel(self)
        self.model.setTable('progs')  # !!! тавлица в db

        # вызовите метод select(), чтобы выбрать все данные в таблице, и соответствующее
        # представление также отобразит все данные;
        self.model.select()
        self.tableView.setModel(self.model)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def run(self):
        if not os.path.isfile('password.txt'):
            self.passw = PasswordWindow()
            self.passw.show()
            self.hide()
        else:
            self.firstWin = FirstWindow()
            self.firstWin.show()
            self.hide()

    def run_2(self):
        self.st = self.tableView.currentIndex().row()
        if self.tableView.model().index(self.st, 3).data() == 'yes':
            name = self.tableView.model().index(self.st, 0).data()
            arg1 = self.tableView.model().index(self.st, 1).data()
            arg2 = self.tableView.model().index(self.st, 2).data()
            with sqlite3.connect('database.db') as db:
                curs = db.cursor()
                curs.execute(f"UPDATE progs SET Permission='no' WHERE Site=?", (name,))
            x = threading.Thread(target=thread_function, args=(name, int(arg1), int(arg2)))
            x.start()
        # with sqlite3.connect('database.db') as db:
        #     curs = db.cursor()
        #     ls = list(curs.execute('SELECT * FROM progs'))
        #     curs.execute('DELETE FROM progs')
        #     ls.sort()
        #     for i in range(len(ls)):
        #         curs.execute('INSERT INTO progs VALUES(?, ?, ?)', ls[i])
        #     db.commit()
        self.MainWin = MainWindow()
        self.MainWin.show()
        self.hide()


class FirstWindow(QMainWindow):
    def __init__(self):
        super(FirstWindow, self).__init__()
        uic.loadUi('first.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run_2)

    def run(self):
        with open('password.txt', 'r') as f:
            self.ps = self.lineEdit.text()
            self.hash = hashlib.md5(self.ps.encode()).hexdigest()
            pasw = f.readline().strip()
            if self.hash == pasw:
                self.label_2.setText('')
                self.admWin = AdministratorWindow()
                self.admWin.show()
                self.hide()
            else:
                self.label_2.setText('Неверный пароль!')

    def run_2(self):
        self.MainWin = MainWindow()
        self.MainWin.show()
        self.hide()


class SecondWindow(QMainWindow):
    def __init__(self, values=None):
        super(SecondWindow, self).__init__()
        uic.loadUi('interfeice.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run_2)
        self.pushButton_3.clicked.connect(self.run_3)
        self.pushButton_4.clicked.connect(self.run_4)
        # for i in ls:
        #     self.widget(self.pr, [f'{i}'])
        if values:
            self.lineEdit.setText(values[0])
            self.lineEdit_2.setText(values[1])
            self.lineEdit_3.setText(values[2])
            self.lineEdit.setEnabled(False)
    #
    # def _display_selected(self):
    #     selected_items = self.treeWidget.selectedItems()
    #     self.itm = [item.text(0) for item in selected_items][0]
    #     self.lineEdit.setText(self.itm)

    def run(self):
        name = self.lineEdit.text()
        us_t = self.lineEdit_2.text()
        res_t = self.lineEdit_3.text()
        if name != '' and us_t != '' and res_t != '':
            with sqlite3.connect('database.db') as db:
                curs = db.cursor()
                curs.execute(
                    f'CREATE TABLE IF NOT EXISTS progs(Site TEXT PRIMARY KEY, Using_time TEXT, Rest_time TEXT)')
                try:
                    curs.execute(f"INSERT INTO progs(Site, Using_time, Rest_time, Permission)"
                                 f" VALUES('{name}', '{us_t}', '{res_t}', 'yes')")
                    with open(hosts, 'r+') as f:
                        f.read()
                        f.write(f'{redirect_url} www.{name}\n')
                        f.write(f'{redirect_url} {name}\n')
                except sqlite3.IntegrityError:
                    pass
                db.commit()
            self.label.setText('')
        else:
            self.label.setText('Введите все данные!')
        self.admWin = AdministratorWindow()
        self.admWin.show()
        self.hide()

    def run_2(self):
        name = self.lineEdit.text()
        ut = int(self.lineEdit_2.text())
        rt = int(self.lineEdit_3.text())
        with sqlite3.connect('database.db') as db:
            curs = db.cursor()
            curs.execute(
                f'CREATE TABLE IF NOT EXISTS progs(Site TEXT PRIMARY KEY, Using_time TEXT, Rest_time TEXT)')
            try:
                curs.execute(f'UPDATE progs SET Using_time={ut}, Rest_time={rt} WHERE Site=?', (name,))
            except sqlite3.IntegrityError:
                pass
            db.commit()
        self.admWin = AdministratorWindow()
        self.admWin.show()
        self.hide()

    def run_3(self):
        self.admWin = AdministratorWindow()
        self.admWin.show()
        self.hide()

    def run_4(self):
        self.outWin = OutWindow()
        self.outWin.show()
        self.hide()


class OutWindow(QMainWindow):
    def __init__(self):
        super(OutWindow, self).__init__()
        uic.loadUi('outro.ui', self)
        self.show()
        self.pushButton_3.clicked.connect(self.run)

    def run(self):
        self.secondWin = SecondWindow()
        self.secondWin.show()
        self.hide()


class PasswordWindow(QMainWindow):
    def __init__(self):
        super(PasswordWindow, self).__init__()
        uic.loadUi('new_password.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.a = self.lineEdit.text()
        self.b = self.lineEdit_2.text()
        if self.a == self.b and self.a != '':
            self.label_4.setText('')
            my_file = open("password.txt", "w+")
            my_file.write(hashlib.md5(self.a.encode()).hexdigest())
            my_file.close()
            self.firstWin = FirstWindow()
            self.firstWin.show()
            self.hide()
        elif self.a == '' or self.b == '':
            self.label_4.setText('Введите пароль!')
        else:
            self.label_4.setText('Пароли не совпадают!')


class AdministratorWindow(QMainWindow):
    def __init__(self):
        super(AdministratorWindow, self).__init__()
        uic.loadUi('adm.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run_2)
        self.pushButton_3.clicked.connect(self.run_3)
        # self.pushButton_4.clicked.connect(self.run_4)
        self.pushButton_5.clicked.connect(self.run_5)
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('database.db')
        db.open()
        self.model = QSqlTableModel(self)
        self.model.setTable('progs')
        self.model.select()
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.tableView.setSortingEnabled(True)

        self.tableView.setModel(self.proxyModel)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def run(self):
        self.secondWin = SecondWindow()
        self.secondWin.show()
        self.hide()

    def run_2(self):
        self.st = self.tableView.currentIndex().row()
        self.current_list = [self.tableView.model().index(self.st, 0).data(),
                             self.tableView.model().index(self.st, 1).data(),
                             self.tableView.model().index(self.st, 2).data()]
        if self.st != -1:
            self.secondWin = SecondWindow(self.current_list)
            self.secondWin.show()
            self.hide()

    def run_3(self):
        self.cell_value = self.tableView.model().index(self.tableView.currentIndex().row(), 0).data()
        print(self.cell_value)
        with sqlite3.connect('database.db') as db:
            curs = db.cursor()
            try:
                curs.execute('DELETE FROM progs WHERE Site=?', (self.cell_value,))
                with open(hosts, 'r+') as f:
                    src = f.readlines()
                    f.seek(0)

                    for line in src:
                        if self.cell_value not in line:
                            f.write(line)
                        f.truncate()
            except sqlite3.IntegrityError:
                pass
            db.commit()
        self.admWin = AdministratorWindow()
        self.admWin.show()
        self.hide()

    def run_4(self):
        with sqlite3.connect('database.db') as db:
            curs = db.cursor()
            ls = list(curs.execute('SELECT * FROM progs'))
            curs.execute('DELETE FROM progs')
            ls.sort()
            for i in range(len(ls)):
                curs.execute('INSERT INTO progs VALUES(?, ?, ?)', ls[i])
            db.commit()
        self.admWin = AdministratorWindow()
        self.admWin.show()
        self.hide()

    def run_5(self):
        self.MainWin = MainWindow()
        self.MainWin.show()
        self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWin = MainWindow()
    sys.exit(app.exec_())
