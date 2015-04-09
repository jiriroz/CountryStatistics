import Tkinter as tk
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

class GetData:
    """Class that takes care of user interface, getting data
       from the database and getting it to the user."""

    def __init__(self):
        self.selectedRows = []
        self.selectedColumns = []
        try:
            self.connectDatabase()
            self.loadColumnsAndKeys()

            self.setupWindow()
            self.window.mainloop()
        finally:
            self.closeDatabase()

    def connectDatabase(self):
        self.connection = sqlite3.connect("countries.db")
        self.cursor = self.connection.cursor()

    def loadColumnsAndKeys(self):
        file = open("dbinfo.txt","r")
        self.columns = (file.read()).split("\n")[:-1]
        file.close()
        self.columns.sort()
        self.columnsDisplay = map(lambda x:x.replace("_"," "), self.columns)
        command = "SELECT country from Countries"
        self.cursor.execute(command)
        self.countries = map(lambda x:x[0], self.cursor.fetchall())

    def setupWindow(self):
        self.window = tk.Tk()
        self.window.geometry("600x400")
        self.window.resizable(width=False, height=False)
        self.window.title("World Factbook Statistics")

        countryX = 100
        countryY = 50
        optionsX = 300
        optionsY = 50

        self.countrySel = tk.Listbox(self.window,selectmode="extended")
        self.countrySel.place(x=countryX,y=countryY)
        self.addOptions(self.countrySel,self.countries)

        self.parameterSel = tk.Listbox(self.window,selectmode="multiple")
        self.parameterSel.place(x=optionsX,y=optionsY)
        self.addOptions(self.parameterSel,self.columnsDisplay)

        self.addButton = tk.Button(self.window,text="Add",command=self.add).place(x=195,y=225)
        self.plotButton = tk.Button(self.window,text="Plot",command=self.getAndVisualizeData).place(x=258,y=225)
        self.clearButton = tk.Button(self.window,text="Clear Selection",command=self.clearSelection).place(x=320,y=225)


    def addOptions(self,listbox,options):
        for i in range(len(options)):
            listbox.insert(i+1,options[i])

    #update current selection
    def add(self):
        rows = self.countrySel.curselection()
        cols = self.parameterSel.curselection()
        self.selectedRows += rows
        self.selectedColumns += cols

    #clear selection
    def clearSelection(self):
        self.selectedRows = []
        self.selectedColumns = []

    def getAndVisualizeData(self):
        self.add()
        self.selectedRows = list(set(self.selectedRows))
        rows = [self.countries[i] for i in self.selectedRows]
        colX = self.columns[self.selectedColumns[0]]
        colY = self.columns[self.selectedColumns[1]]
        xData,yData = self.query(rows,colX,colY)
        xLabel = self.columnsDisplay[self.selectedColumns[0]]
        yLabel = self.columnsDisplay[self.selectedColumns[1]]
        self.clearSelection();
        self.plot(rows,xLabel,yLabel,xData,yData)

    def query(self,rows,colX,colY):
        xData = self.getColumn(rows,colX)
        yData = self.getColumn(rows,colY)
        xData = map(lambda x:x[0], xData)
        yData = map(lambda x:x[0], yData)
        return xData,yData

    def getColumn(self,rows,col):
        result = []
        select = 'SELECT %s FROM Countries WHERE country="' % col
        for country in rows:
            command = select + country + '"'
            self.cursor.execute(command)
            row = self.cursor.fetchone()
            result.append(row)
        return result

    def plot(self,countries,xLabel,yLabel,xData,yData):
        figure = plt.figure(1)
        plot = figure.add_subplot(111)
        plot.plot(xData,yData,marker='o',color='#0066cc',ls='None')
        plot.set_xlabel(xLabel)
        plot.set_ylabel(yLabel)
        plot.set_title(xLabel + " vs. " + yLabel)

        coords = zip(xData,yData)
        for i in range(len(countries)):
            if coords[i][0] != None and coords[i][1] != None:
                plot.annotate(countries[i],xy=coords[i])
        plt.show()


    def closeDatabase(self):
        self.connection.commit()
        self.connection.close()


getData = GetData()
