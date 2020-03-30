#COPYRIGHT MICHEAL NESTOR 30/03/2020 MICHEALNESTOR@OUTLOOK.COM
#This is a program which uses a database of stocknames and urls to their historical prices page on yahoo finance, to find data about these stocks and display it to a user:
#I coded this program to:
# - Learn how to integrate matplotlib with pyqt5 (I will need this knowlege in my upcoming computer science coursework)
# - Practice pyqt5
# - Learn the matplotlib module
# - practice webscraping data
#I am happy with the outcome of the program, a small kink I would iron out if I had more time to focus on the program, would be dealing with changes in the webscraped data:
# - for example at some points in yahoo finances something called dividens occours, I have a very limited knowlege of stocks so I dont know what that means, however there is
#   no price data for those dates, so I implemented a error message that occours if you try to retrieve data when an dividend appears, if I had more time I would find a way to
#   plot an average of the day before and after, and find a way to highlight the fact that I have done so:
#If I had more time I would also of added a window for an admin to add new stock URLS to the program. 

#All of the modules needed for this program to run:
import sys
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QTableWidgetItem
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

#A class that controlls the plotting of the graph
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4))
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    #plot allows you to pass data and the name of the stock and it will plot the data that is passed onto a line graph titled 'price graph for {stockname}'
    def plot(self, data, stockName):
        averagePrice = []
        lowPrice = []
        highPrice = []
        #the data variable holds the data for all 3 lines that I want to plot,  so I use this loop to split the data into 3 individual datasets
        for i in range(len(data)):
            if i > 0:
                averagePrice.append(data[i][0])
                lowPrice.append(data[i][1])
                highPrice.append(data[i][2])
            else:
                averagePrice.append(data[i+1][0])
                lowPrice.append(data[i+1][1])
                highPrice.append(data[i + 1][2])
        #draws the graph itself:
        ax = self.figure.add_subplot(111)
        ax.set_xlim((len(data)-1), 1)
        ax.grid(True)
        ax.patch.set_alpha(0.5)
        ax.set_xlabel('days')
        ax.plot(averagePrice, 'b-')
        ax.plot(lowPrice, 'r-')
        ax.plot(highPrice, 'g-')
        ax.set_title(f'Price Graph for {stockName}')
        self.draw()

    #This function is used to clear the graph before plotting more lines. 
    def clear(self):
        self.figure.clf()

#Class for my qyqt5 window, which is used to manage user inputs and the user interface:
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        #The following lines set up all the elements of the user interface:
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(891, 571)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.SearchButton = QtWidgets.QPushButton(self.centralwidget)
        self.SearchButton.setGeometry(QtCore.QRect(530, 180, 351, 31))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(16)
        self.SearchButton.setFont(font)
        self.SearchButton.setObjectName("SearchButton")
        self.Title = QtWidgets.QLabel(self.centralwidget)
        self.Title.setGeometry(QtCore.QRect(10, 10, 501, 71))
        font.setPointSize(38)
        font.setUnderline(True)
        self.Title.setFont(font)
        self.Title.setAlignment(QtCore.Qt.AlignCenter)
        self.Title.setObjectName("Title")
        self.Key = QtWidgets.QLabel(self.centralwidget)
        self.Key.setGeometry(QtCore.QRect(10, 100, 501, 31))
        font.setPointSize(18)
        font.setUnderline(False)
        self.Key.setFont(font)
        self.Key.setAlignment(QtCore.Qt.AlignCenter)
        self.Key.setObjectName("Key")
        self.StockNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.StockNameLabel.setGeometry(QtCore.QRect(530, 10, 341, 41))
        font.setPointSize(17)
        font.setUnderline(True)
        self.StockNameLabel.setFont(font)
        self.StockNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.StockNameLabel.setObjectName("StockNameLabel")
        self.StockNames = QtWidgets.QComboBox(self.centralwidget)
        self.StockNames.setGeometry(QtCore.QRect(530, 60, 351, 21))
        self.StockNames.setObjectName("StockNames")
        self.DaysLabel = QtWidgets.QLabel(self.centralwidget)
        self.DaysLabel.setGeometry(QtCore.QRect(530, 90, 351, 41))
        self.DaysLabel.setFont(font)
        self.DaysLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.DaysLabel.setObjectName("DaysLabel")
        self.DaysSelect = QtWidgets.QSpinBox(self.centralwidget)
        self.DaysSelect.setGeometry(QtCore.QRect(530, 140, 351, 22))
        self.DaysSelect.setMinimum(3)
        self.DaysSelect.setMaximum(60)
        self.DaysSelect.setObjectName("DaysSelect")
        self.DataTable = QtWidgets.QTableWidget(self.centralwidget)
        self.DataTable.setGeometry(QtCore.QRect(530, 220, 351, 341))
        self.DataTable.setObjectName("DataTable")
        self.DataTable.setColumnCount(3)
        self.DataTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.DataTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.DataTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.DataTable.setHorizontalHeaderItem(2, item)
        #the next 3 lines add the names of all the stocks in the database, to the 'StockNames' combo box
        stockNames = databaseAccess('SELECT StockName FROM tblStocks')
        for records in stockNames:
            self.StockNames.addItem(records[0])
        #the next two lines set up the canvas where data will be plotted
        self.m = PlotCanvas(self.centralwidget)
        self.m.move(20, 150)
        MainWindow.setCentralWidget(self.centralwidget)
        #the next line links the search push button the the class method 'searchButtonMethod'
        self.SearchButton.clicked.connect(self.searchButtonMethod)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    #this method adds text to all of the widgets set up in the 'setupUi' method 
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Stock Market Viewer"))
        self.SearchButton.setText(_translate("MainWindow", "Search For Data"))
        self.Title.setText(_translate("MainWindow", "Stock Market Search"))
        self.Key.setText(_translate("MainWindow", "Low: RED     average: BLUE     high: GREEN"))
        self.StockNameLabel.setText(_translate("MainWindow", "Stock Name:"))
        self.DaysLabel.setText(_translate("MainWindow", "How Many Days?"))
        item = self.DataTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Average Price"))
        item = self.DataTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Low"))
        item = self.DataTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "High"))

    #Function that runs after a user presses the search button
    def searchButtonMethod(self):
        #The next two lines take the user selections for the time fram they want data for and which stock they want data for
        selectedName = self.StockNames.currentText()
        selectedDays = self.DaysSelect.value()
        #The next line gets the URL of the selected stock from the database I mentioned at the top of this file, it uses my database access function
        URL = databaseAccess('SELECT URL FROM tblStocks WHERE StockName = ?', (selectedName, ))
        URL = URL[0][0]
        #The search function is a webscraping function that gets the data from a specific amount of days from a yahoo finance stock history page
        #This means that the program always shows up to date data, and I don't need to use up storage storing price histories. 
        data = search(URL, selectedDays)
        #pyqt5 tables can only take strings and matplotlib graphs can only take floats so I make two lists, one filled with floats one with strings
        refinedList = []
        numberList = []
        length = len(data)
        error = False
        #this loop converts the data sourced from yahoo finance and turns it into usefull data
        for i in range(length):
            place = 7 * i
            if place < (length - 4):
                if place > 0:
                    refinedList.append([data[place + 1], data[place + 3], data[place + 2]])
                    try:
                        numberList.append([float(data[place + 1]), float(data[place + 3]), float(data[place + 2])])
                    #if a dividend appears (read the top of the page) then this exception runs and an error message is sent to the user. 
                    except:
                        error = True
        if error == True:
            messageBox('Data Retrieval Error', 'Unfortunately in this time period, a dividend must have occoured, and so we can not display data for this time period')
        else:
            #if no dividend appears then the following lines update the qt table with the new data and then plot this data onto the matplotlib graph.
            length = len(refinedList)
            self.DataTable.setRowCount(length)
            _translate = QtCore.QCoreApplication.translate
            for i in range(length):
                item = QtWidgets.QTableWidgetItem()
                self.DataTable.setVerticalHeaderItem(i, item)
                item = self.DataTable.verticalHeaderItem(i)
                item.setText(_translate("MainWindow", f"Day {str(i)}"))
                for x in range(3):
                    self.DataTable.setItem(i,x, QTableWidgetItem(refinedList[i][x]))
            self.m.clear()
            self.m.plot(numberList, selectedName)

#function I made to make calling message boxes easier
def messageBox(title, content):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(content)
    msgBox.setWindowTitle(title)
    msgBox.exec()

#fucntion I made to make accessing a specific database easier
def databaseAccess(query, args=0):
    databaseFile = 'StocksDatabase.db'
    databaseConnection = sqlite3.connect(databaseFile)
    cursor = databaseConnection.cursor()
    if args == 0:
        cursor.execute(query)
    else:
        cursor.execute(query, args)
    fetchedData = cursor.fetchall()
    databaseConnection.commit()
    return fetchedData

#function for searching through yahoo finance historical pages and storing the data on the price table for a set amount of days.
def search(URL, days):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    stocktable = soup.find('table', attrs={'class': 'W(100%) M(0)'})
    tablebody = stocktable.find('tbody')
    tablerecords = tablebody.find_all('tr')
    dayCount = 0
    stockdata = []
    for tablerecord in tablerecords:
        dayCount += 1
        recorddataset = tablerecord.find_all('td')
        for recorddata in recorddataset:
            stockdata.append(recorddata.text)
        if dayCount == days:
            break
    return stockdata

#method that creates a Ui_MainWindow object and runs it
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()
