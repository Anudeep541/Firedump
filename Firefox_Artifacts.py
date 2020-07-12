'''
Author: Jane1729
Date: 09-07-2020
Description: Dumps Forensic Artificats of Firefox Browser with GUI in Windows
'''
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path
import sqlite3
import csv

profile_dbs = {}
usr_content = {}
profil_dict = {}
db_path = ''
opted_usr = ''
opted_profile = ''
chosen_chkbox_ls = []

def fire():

    #### Getting the users and storing in a list ####
    users = [x.name for x in Path(r'C:\Users').glob('*') if x.name not in ['Public', 'All Users'] and x.name.find('Default') and x.name.find('default') and x.is_dir()]
    #print (users)

    for usrname in users:
        folder_path = 'C:/Users/'+usrname+'/AppData/Roaming/Mozilla/Firefox/Profiles'
        ##### Getting the profiles in Firefox for a particular user #####
        folder_names = [f.name for f in Path(folder_path).glob('*')]

        if len(folder_names) == 0:
            continue

        else:
            for var in folder_names:
                profile_dbs.update({var:folder_path+'/'+var+'/places.sqlite'})          # Putting profile name and respective database path in a dictionary 
        usr_content.update({usrname:profile_dbs})                                       # Putting profiles and database paths of particular user in another dictionary


class Ui_MainWindow(object):

    def load_history(self):
        connection = sqlite3.connect(db_path)
        ruc = connection.cursor()
        ruc.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='moz_places' ''')

        #if the count is 1, then table exists
        if ruc.fetchone()[0]!=1 :
            connection.commit()
            connection.close()
            return 'no_tab'
        else:
            ruc.execute("select url,title,visit_count,datetime(last_visit_date/1000000,'unixepoch','localtime') from moz_places")
            data = ruc.fetchall()
            connection.commit()
            connection.close()
            return data
    
    def load_books(self):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='moz_bookmarks' ''')

        #if the count is 1, then table exists
        if cur.fetchone()[0]!=1 :
            conn.commit()
            conn.close()
            return 'no_tab'
        else:
            rows = cur.execute("select title,datetime(dateAdded/1000000,'unixepoch','localtime'),datetime(lastModified/1000000,'unixepoch','localtime') from moz_bookmarks")
            rows = cur.fetchall()
            conn.commit()
            conn.close()
            return rows
    
    def load_downloads(self):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='moz_annos' ''')

        #if the count is 1, then table exists
        if cur.fetchone()[0]!=1 :
            conn.commit()
            conn.close()
            return 'no_tab'
        else:
            cur.execute("select content,datetime(dateAdded/1000000,'unixepoch','localtime'),datetime(lastModified/1000000,'unixepoch','localtime') from moz_annos where content NOT LIKE '%state%' and content NOT LIKE '%endtime%'")
            rows = cur.fetchall()
            conn.commit()
            conn.close()
            return rows


    def get_history(self):
        data = self.load_history()

        if data == 'no_tab':
            self.err_labl.setText('No Data avaialble for Selected Artifact')
            self.err_labl.show()
        else:
            self.err_labl.hide()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(['URL','Title','Visit Count','Last Visited'])
            for row_num, row_dat in enumerate(data):
                self.tableWidget.insertRow(row_num)
                for col_num,col_dat in enumerate(row_dat):
                    self.tableWidget.setItem(int(row_num),int(col_num),QtWidgets.QTableWidgetItem(str(col_dat)))

    def get_downloads(self):
        rows = self.load_downloads()

        if rows == 'no_tab':
            self.err_labl.setText('No Data avaialble for Selected Artifact')
            self.err_labl.show()
        else:
            self.err_labl.hide()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(['File Location','Date Added','Last Modified'])
            for row_num, row_dat in enumerate(rows):
                self.tableWidget.insertRow(row_num)
                for col_num,col_dat in enumerate(row_dat):
                    self.tableWidget.setItem(int(row_num),int(col_num),QtWidgets.QTableWidgetItem(str(col_dat)))

    def get_books(self):
        rows = self.load_books()

        if rows == 'no_tab':
            self.err_labl.setText('No Data avaialble for Selected Artifact')
            self.err_labl.show()
        else:
            self.err_labl.hide()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(['Title','Date Added','Last Modified'])
            for row_num, row_dat in enumerate(rows):
                self.tableWidget.insertRow(row_num)
                for col_num,col_dat in enumerate(row_dat):
                    self.tableWidget.setItem(int(row_num),int(col_num),QtWidgets.QTableWidgetItem(str(col_dat)))

    def artifacts(self,index):
        opted_artifact = self.artifacts_combo.itemText(index)

        if opted_artifact == 'Bookmarks':
            self.get_books()
        
        if opted_artifact == 'History':
            self.get_history()

        if opted_artifact == 'Downloads':
            self.get_downloads()

    def get_profile_artifacts(self,index):
        global opted_profile
        opted_profile = self.profiles_combo.itemText(index)
        
        if opted_profile == '':
            self.err_labl.setText('Please Select a Valid Profile')
            self.err_labl.show()
        
        else:
            self.err_labl.hide()
            global db_path
            db_path = profil_dict[opted_profile]
            self.artifacts_combo.activated.connect(self.artifacts)

    def get_profiles(self,index):
        global opted_usr
        opted_usr = self.user_names_combo.itemText(index)

        if opted_usr == '':
            self.err_labl.setText('Please Select a Valid User')
            self.err_labl.show()
        
        else:
            self.err_labl.hide()
            global profil_dict
            profil_dict = usr_content[opted_usr]

            self.profiles_combo.clear()
            self.profiles_combo.addItem("")
            self.profiles_combo.setItemText(0, "")

            for profile_name in profil_dict:
                self.profiles_combo.addItem(str(profile_name))
        
            self.profiles_combo.activated.connect(self.get_profile_artifacts)


    def histy_chkbox_event(self,checked):
        if checked:
            chosen_chkbox_ls.append('history_chkbox')
    
    def books_chkbox_event(self,checked):
        if checked:
            chosen_chkbox_ls.append('books_chkbox')

    def downs_chkbox_event(self,checked):
        if checked:
            chosen_chkbox_ls.append('downloads_chkbox')

    '''
    def error_func(self):
            QMessageBox.about(self,"Error","Choose something from checkbox")
    '''
    def export_artifacts(self):
        '''
        if len(chosen_chkbox_ls) == 0:
            self.error_func()
        '''
        for string in chosen_chkbox_ls:
            if string == 'books_chkbox':
                file_name = opted_usr+'_'+opted_profile+'_bookmarks.csv'
                info = self.load_books()

                if info == 'no_tab':
                    self.err_labl.setText('No Data avaialble for Selected Artifact')
                    self.err_labl.show()
                else:
                    self.err_labl.hide()
                    with open(file_name,'w',newline='',encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerows(info)
            
            if string == 'downloads_chkbox':
                file_name = opted_usr+'_'+opted_profile+'_downloads.csv'
                data = self.load_downloads()

                if data == 'no_tab':
                    self.err_labl.setText('No Data avaialble for Selected Artifact')
                    self.err_labl.show()
                else:
                    self.err_labl.hide()
                    with open(file_name,'w',newline='',encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerows(data)
            
            if string == 'history_chkbox':
                file_name = opted_usr+'_'+opted_profile+'_history.csv'
                rows = self.load_history()

                if rows == 'no_tab':
                    self.err_labl.setText('No Data avaialble for Selected Artifact')
                    self.err_labl.show()
                else:
                    self.err_labl.hide()
                    with open(file_name,'w',newline='',encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerows(rows)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(782, 562)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.artifacts_combo = QtWidgets.QComboBox(self.centralwidget)
        self.artifacts_combo.setGeometry(QtCore.QRect(290, 80, 171, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(60)
        self.artifacts_combo.setFont(font)
        self.artifacts_combo.setAcceptDrops(False)
        self.artifacts_combo.setObjectName("artifacts_combo")
        self.artifacts_combo.addItem("")
        self.artifacts_combo.setItemText(0, "")
        self.artifacts_combo.addItem("")
        self.artifacts_combo.addItem("")
        #self.artifacts_combo.addItem("")
        self.artifacts_combo.addItem("")
        self.history_chkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.history_chkbox.setGeometry(QtCore.QRect(530, 53, 70, 17))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.history_chkbox.setObjectName("history_chkbox")

        self.history_chkbox.stateChanged.connect(self.histy_chkbox_event)

        self.downloads_chkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.downloads_chkbox.setGeometry(QtCore.QRect(590, 83, 91, 17))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.downloads_chkbox.setObjectName("downloads_chkbox")

        self.downloads_chkbox.stateChanged.connect(self.downs_chkbox_event)

        self.books_chkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.books_chkbox.setGeometry(QtCore.QRect(670, 53, 70, 17))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.books_chkbox.setObjectName("books_chkbox")

        self.books_chkbox.stateChanged.connect(self.books_chkbox_event)

        '''
        self.cookies_chkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.cookies_chkbox.setGeometry(QtCore.QRect(670, 80, 70, 17))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.cookies_chkbox.setObjectName("cookies_chkbox")
        '''
        self.export_bttn = QtWidgets.QPushButton(self.centralwidget)
        self.export_bttn.setGeometry(QtCore.QRect(594, 112, 71, 31))
        self.export_bttn.setObjectName("export_bttn")
        
        self.export_bttn.clicked.connect(self.export_artifacts)

        self.export_labl = QtWidgets.QLabel(self.centralwidget)
        self.export_labl.setGeometry(QtCore.QRect(570, 20, 121, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.export_labl.setFont(font)
        self.export_labl.setAlignment(QtCore.Qt.AlignCenter)
        self.export_labl.setObjectName("export_labl")
        self.artif_labl = QtWidgets.QLabel(self.centralwidget)
        self.artif_labl.setGeometry(QtCore.QRect(100, 80, 171, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.artif_labl.setFont(font)
        self.artif_labl.setAlignment(QtCore.Qt.AlignCenter)
        self.artif_labl.setObjectName("artif_labl")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(40, 150, 721, 371))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(5)
        self.profil_labl = QtWidgets.QLabel(self.centralwidget)
        self.profil_labl.setGeometry(QtCore.QRect(250, 20, 101, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.profil_labl.setFont(font)
        self.profil_labl.setAlignment(QtCore.Qt.AlignCenter)
        self.profil_labl.setObjectName("profil_labl")
        self.profiles_combo = QtWidgets.QComboBox(self.centralwidget)
        self.profiles_combo.setGeometry(QtCore.QRect(360, 20, 141, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(60)
        self.profiles_combo.setFont(font)
        self.profiles_combo.setAcceptDrops(False)
        self.profiles_combo.setObjectName("profiles_combo")
        self.profiles_combo.addItem("")
        self.profiles_combo.setItemText(0, "")


        self.usr_labl = QtWidgets.QLabel(self.centralwidget)
        self.usr_labl.setGeometry(QtCore.QRect(40, 20, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.usr_labl.setFont(font)
        self.usr_labl.setAlignment(QtCore.Qt.AlignCenter)
        self.usr_labl.setObjectName("usr_labl")
        self.user_names_combo = QtWidgets.QComboBox(self.centralwidget)
        self.user_names_combo.setGeometry(QtCore.QRect(100, 20, 141, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(60)
        self.user_names_combo.setFont(font)
        self.user_names_combo.setAcceptDrops(False)
        self.user_names_combo.setObjectName("user_names_combo")
        self.user_names_combo.addItem("")
        self.user_names_combo.setItemText(0, "")

        ### Inserting User Names from System into combobox ###
        for usr in usr_content:
            self.user_names_combo.addItem(str(usr))
        ### Getting Firefox Profiles for selected User ###
        self.user_names_combo.activated.connect(self.get_profiles)
        
        self.err_labl = QtWidgets.QLabel(self.centralwidget)
        self.err_labl.setGeometry(QtCore.QRect(210, 120, 251, 20))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.err_labl.setFont(font)
        self.err_labl.setStyleSheet("color: rgb(255, 0, 0);")
        self.err_labl.setAlignment(QtCore.Qt.AlignCenter)
        self.err_labl.setObjectName("err_labl")
        self.err_labl.hide()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 782, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.artifacts_combo.setItemText(1, _translate("MainWindow", "History"))
        self.artifacts_combo.setItemText(2, _translate("MainWindow", "Downloads"))
        #self.artifacts_combo.setItemText(3, _translate("MainWindow", "Most Frequently Visited"))
        self.artifacts_combo.setItemText(3, _translate("MainWindow", "Bookmarks"))
        self.history_chkbox.setText(_translate("MainWindow", "History"))
        self.downloads_chkbox.setText(_translate("MainWindow", "Downloads"))
        self.books_chkbox.setText(_translate("MainWindow", "Bookmarks"))
        #self.cookies_chkbox.setText(_translate("MainWindow", "Cookies"))
        self.export_bttn.setText(_translate("MainWindow", "Export"))
        self.export_labl.setText(_translate("MainWindow", "Export to CSV"))
        self.artif_labl.setText(_translate("MainWindow", "              Artifact "))
        self.profil_labl.setText(_translate("MainWindow", "Profile Name"))
        self.usr_labl.setText(_translate("MainWindow", "Users"))
        self.err_labl.setText(_translate("MainWindow", "No Data avaialble for Selected Artifact"))


if __name__ == "__main__":
    import sys
    fire()                                                          # To get the users and their associated Firefox profiles
    #print (usr_content)
    #print (profile_dbs)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
