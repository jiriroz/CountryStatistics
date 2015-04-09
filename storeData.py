import sqlite3
import re
import os
import sys

"""
Command line arguments:
all: gets all text files
file1.txt, file2.txt, ...: gets only specified files
You can load any data text file from CIA World Factbook.
For format see example files.

Process and save files' contents.
Create a database and a table.
For each statistics create a new column in the db,
save all statistics into the database."""

def parseArguments():
    args = []
    i = 1
    while True:
        try:
            args.append(sys.argv[i])
        except IndexError:
            break
        i += 1
    if len(args) == 0:
        raise Exception("No command line arguments.")
    return args


def getTextFiles(fileNames):
    ignore = ["dbinfo.txt"]
    files = []
    allfiles = [f for f in os.listdir('.') if f.endswith('.txt')
             and f not in ignore]
    if fileNames[0] == "-all":
        files = allfiles
    else:
        files = [f for f in fileNames if f in allfiles]
    return files

def readFile(fileName):
    file = open(fileName,'r')
    contents = file.read()
    file.close()
    return contents

def processData(data):
    data = data.split('\r')
    data = map(lambda x: x.split('\t'), data)[:-1]
    data = map(lambda x: x[1:], data)
    for x in range(len(data)):
        data[x][1] = re.sub("[\$\s\,]", "", data[x][1])
        data[x][1] = float(data[x][1])
    return data

def createDatabase(cursor,columns):
    body = " ,"
    for x in columns:
        body += x + " REAL, "
    body = body[:-2]
    try:
        cursor.execute("DROP TABLE Countries")
    except sqlite3.OperationalError:
        pass
    create = """
    CREATE TABLE Countries (
    country TEXT PRIMARY KEY""" + body + ");"
    cursor.execute(create)

def updateDatabase(cursor,processed):
    check = "SELECT 1 FROM Countries WHERE country = "
    for stats in processed:
        for country_stats in processed[stats]:
            country = country_stats[0]
            value = country_stats[1]
            cursor.execute(check + '"' + country + '";')
            result = cursor.fetchone()
            if result == None:
                #key not present, create new entry
                command = 'INSERT INTO Countries (country) VALUES ("%s");' % country
                cursor.execute(command)
            command = "UPDATE Countries SET %s =? WHERE country=?;" % stats
            try:
                cursor.execute(command, (value,country))
            except Exception as e:
                print ("failed to update: ",stats,value,country)
                print (e)

def createDatabaseInfo(columns):
    file = open("dbinfo.txt","w")
    for cname in columns:
        file.write(cname + "\n")
    file.close()

arguments = parseArguments()
files = getTextFiles(arguments)
processed = dict()

for f in files:
    data = readFile(f)
    data = processData(data)
    name = f[:-4]
    processed[name] = data

connection = sqlite3.connect("countries.db")
cursor = connection.cursor()

cols = [x for x in processed]

createDatabaseInfo(cols)

createDatabase(cursor,cols)

updateDatabase(cursor,processed)

connection.commit()
connection.close()

