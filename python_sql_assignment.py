#!/usr/bin/python2.7
#
# Interface for the assignement
#

import psycopg2
from psycopg2 import sql

def getOpenConnection(user='postgres', password='1234', dbname='postgres'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")


def loadRatings(ratingstablename, ratingsfilepath, openconnection):

    cur = openconnection.cursor()
    cur.execute(sql.SQL("""CREATE TABLE {}(
    UserID integer,
    MovieID integer,
    Rating float)""").format(sql.Identifier(ratingstablename)))
    openconnection.commit()
    
    infile = open(ratingsfilepath, 'r') 
    lines = infile.readlines()
    for line in lines:
        data = line.strip().split('::')
        UserID = int(data[0])
        MovieID = int(data[1])
        Rating = float(data[2])
        cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(ratingstablename)),
        (UserID, MovieID, Rating))
    openconnection.commit()
    pass

def rangePartition(ratingstablename, numberofpartitions, openconnection):

    lst = [0,0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5];
    upperBound = max(lst)
    lowerBound = min(lst)
    stride =  (upperBound / numberofpartitions - lowerBound / numberofpartitions)
    
    global rangepartitions;
    rangepartitions = numberofpartitions
    
    bounds = []
    tableNames = []
    for n in range(0,numberofpartitions+1):
        bound = lowerBound  +  n*stride
        name = ('range_part'+str(n))
        bounds.append(bound)
        tableNames.append(name)
    tableNames = (tableNames[0:-1])
    
    cur = openconnection.cursor()
    cur.execute(sql.SQL("""CREATE TABLE {} AS
    SELECT *
    FROM ratings
    WHERE rating >= %s AND rating <= %s
    """).format(sql.Identifier(tableNames[0])),
        (bounds[0], bounds[1]))

    openconnection.commit()
    
    
    if numberofpartitions>1:
        for j in range(1,len(tableNames)):
            cur = openconnection.cursor()
            cur.execute(sql.SQL("""CREATE TABLE {} AS
            SELECT *
            FROM ratings
            WHERE rating > %s AND rating <= %s
            """).format(sql.Identifier(tableNames[j])),
                (bounds[j], bounds[j+1]))
            openconnection.commit()

    pass

def roundRobinPartition(ratingstablename, numberofpartitions, openconnection):
    
    cur = openconnection.cursor()
    cur.execute(sql.SQL("""CREATE TABLE roundrobinmeta(
    partition text,
    nextpartition text)"""))
    openconnection.commit()

    tableNames = []
    for n in range(0,numberofpartitions):
        name = ('rrobin_part'+str(n))
        tableNames.append(name)
        cur = openconnection.cursor()
        cur.execute(sql.SQL("""CREATE TABLE {}(
        UserID integer,
        MovieID integer,
        Rating float)""").format(sql.Identifier(name)))
        openconnection.commit()
        
        
    cur = openconnection.cursor()
    cur.execute("""select * from ratings""")
    data = cur.fetchall()
    
    table_num = 0
    for record in data:
        
        NewTable = tableNames[table_num]
        
        UserID = int(record[0])
        MovieID = int(record[1])
        Rating = float(record[2])
        cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(NewTable)),
        (UserID, MovieID, Rating))
        
        
        if table_num < (numberofpartitions-1):
            table_num += 1
        else:
            table_num = 0
            
        cur.execute(sql.SQL("INSERT INTO roundrobinmeta VALUES (%s, %s)").format(sql.Identifier(NewTable)),
        (NewTable, tableNames[table_num]))
        
    openconnection.commit()
            
    
    pass

def roundrobininsert(ratingstablename, userid, itemid, rating, openconnection):
    
    cur = openconnection.cursor()
    cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(ratingstablename)),
    (userid, itemid, rating))
    openconnection.commit()
    
    cur = openconnection.cursor()
    cur.execute("""select * from roundrobinmeta""")
    last = cur.fetchall()[-1][1]
    
    cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(last)),
    (userid, itemid, rating))
    openconnection.commit()
    
    pass

def rangeinsert(ratingstablename, userid, itemid, rating, openconnection):
    cur = openconnection.cursor()
    cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(ratingstablename)),
    (userid, itemid, rating))
    openconnection.commit()
    
    lst = [0,0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5];
    upperBound = max(lst)
    lowerBound = min(lst)
    stride =  (upperBound / rangepartitions - lowerBound / rangepartitions)
    
    if(0 <= rating <= stride):
            name = ('range_part'+str(0))
            cur = openconnection.cursor()
            cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(name)),
            (userid, itemid, rating))
            openconnection.commit()
    
    for n in range(1,rangepartitions):
        if(stride*n < rating <= stride*(n+1)):
            name = ('range_part'+str(n))
            cur = openconnection.cursor()
            cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s)").format(sql.Identifier(name)),
            (userid, itemid, rating))
            openconnection.commit()


    pass
