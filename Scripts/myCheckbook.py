
"""
    myCheckbook is a python script to track/analyze a personal checking account.
    Input: bank transaction data downloaded in CSV format
    Storage: Sqlite3 database in a local disk file

MIT License

Copyright (c) 2020 Tom Imlay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import os
import sqlite3
import sys
import csv
import datetime
from datetime import date
import random
from sqlite3 import Error
import PySimpleGUI as sg
from six import string_types, text_type

my_db_file = 'C:/Users/imlay/Downloads/myCheckbook_appdata.db'
# my_db_file = '../myCheckbook_appdata.db'

lightblue = '#b9def4'  # color used by PySimpleGUIdef __init__(self, logfile, table='LogEntries'):
mediumblue = '#d2d2df'  # color used by PySimpleGUI
mediumblue2 = '#534aea'  # color used by PySimpleGUI
mediumgreen = '#66b3b3'  # color used by PySimpleGUI
mediumgreen2 = '#00aaaa'  # color used by PySimpleGUIs
charcoal = '#6a6a6a'


def drawgraph(datalist, graph, scalefactor=None, lableangle=None, flipgraph=None):

    BAR_WIDTH = 20
    BAR_SPACING = 24
    EDGE_OFFSET = 0

    myfont = "Ariel 10"
    if scalefactor is None:
        scalefactor = 1

    if lableangle is None:
        lableangle = 60

    graph.erase()
    for i in (range(len(datalist))):
        display_value = (float(datalist[i][1])).__round__(0)
        lable_value = datalist[i][0]
        graph_value = (float(datalist[i][1])/scalefactor).__round__(0)    # divide by scalefactor to make the bars fit on the chart
        # print('graph_value', graph_value)
        if flipgraph:
            graph_value = graph_value * -1

        graph.draw_rectangle(top_left=(i * BAR_SPACING + EDGE_OFFSET, graph_value),
                bottom_right=(i * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=mediumblue2)
        graph.draw_text(text=str(display_value),
            location=(i * BAR_SPACING + EDGE_OFFSET + 10, graph_value + 40), color='white', font=myfont, angle=lableangle)
        graph.draw_text(text=str(lable_value),
            location=(i * BAR_SPACING + EDGE_OFFSET + 10, -90), color='white', font=myfont, angle=lableangle)

def editwindow(transactiondata, categorylist):

    sg.SetOptions(element_padding=(2, 2))

    layout = [[sg.T('Transaction ID', size=(15, 1)), sg.In(transactiondata[0], key='-EWKEY-', disabled=True)],
              [sg.T('Transaction', size=(15, 1)), sg.In(transactiondata[1], key='-EWTRANS-', disabled=True)],
              [sg.T('Date', size=(15, 1)), sg.In(transactiondata[2], key='-EWDATE-', disabled=True)],
              [sg.T('Amount', size=(15, 1)), sg.In(transactiondata[4], key='-EWAMOUNT-', disabled=True)],
              [sg.T('Category', size=(15, 1)), sg.Combo(categorylist,default_value=transactiondata[3],
                      key='-EWCATEGORY-', enable_events=True)],
              [sg.Exit(), sg.Button('Save', key='-EWSAVE-')],
              [sg.T("Exit doesn't save the changes")]]
    # print('categorylist ->', categorylist)
    editwindow = sg.Window('Edit Transaction', grab_anywhere=False, keep_on_top=True).Layout(layout)
    transactionkey = str(transactiondata[0])
    newcat = []

    while True:
        event, values = editwindow.Read()
        if event is None or event == "Exit":
            editwindow.Close()
            break

        if event == '-EWSAVE-':
            if len(values['-EWCATEGORY-']) == 2:
                # sg.Popup('Category3 ->', values['-MANCATEGORY-'])
                ewcategory = values['-EWCATEGORY-'][0]
            else:
                # sg.Popup('Category? ->', values['-MANCATEGORY-'])
                ewcategory = values['-EWCATEGORY-']

            newcat.append(ewcategory)
            newcat.append(transactionkey)
            # sg.Popup('-EWCATEGORY_ ->', newcat, keep_on_top=True)
            editwindow.Close()
            break

    return newcat

def summarywindow(transactiondata):
    # print('transactiondata  ->', transactiondata)
    sg.SetOptions(element_padding=(2, 2))
    cstransaction_headings = [['Posted_Date'], ['Description'], ['Amount'], ['Category']]
    layout = [[sg.Table(transactiondata,
                            headings=cstransaction_headings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='right',
                            display_row_numbers=True,
                            alternating_row_color=mediumblue2,
                            num_rows=20,
                            enable_events=True,
                            key='-CSTRANSTABLE-')],
                [sg.Exit()]]

    cswindow = sg.Window('Edit Transaction', grab_anywhere=False, keep_on_top=True).Layout(layout)
    transactionkey = str(transactiondata[0])

    while True:
        event, values = cswindow.Read()
        if event is None or event == "Exit":
            cswindow.Close()
            break


def runsql(conn, sqlstring, rowdata=None):
    """
    :param conn:
    :param sqlstring:
    :param rowdata:
    :return: True if successful  else False
    """

    try:
        curr = conn.cursor()
        # print('curr creation succeeded')
        # print('sqlstring / rowdata ->', sqlstring, '/', rowdata)
        if rowdata:
            curr.execute(sqlstring, rowdata)
        else:
            curr.execute(sqlstring)
        # commit the changes
        conn.commit()
        # print('commit succeeded')
        sqloutput = curr.fetchall()
        # print('sqloutput  ->', sqloutput)
        if len(sqloutput) == 0:
            return True
        else:
            return sqloutput
    except Error as e:
        print(e)
        sg.Popup('runsql FAILED(', rowdata, ')')
        return None


def tableexists(datafile, datatable):
    """
    :param: datafile
    :param: datatable
    :return: True if successful else False
    """
    if os.path.isfile(datafile):
        try:
            conn = sqlite3.connect(datafile)

            sql2 = "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%s' ;" % datatable

            # print('sql2 => ', sql2)
            curr = conn.cursor()
            curr.execute(sql2)

            thetablename = curr.fetchall()

            if len(thetablename)==0:
                return False
            else:
                return True
        except Error as e:
            print(e)
            sg.Popup('Could not connect to the database', keep_on_top=True)
            return False
    else:
        sg.Popup('Database file does not exist - it will be created')
        return False


def validatedatafile(datafile):
    if os.path.isfile(datafile):
        # sg.Popup('datafile exist')
        return True
    else:
        sg.Popup('Database file does not exist')
        return False


def setmessage(message, window):
    """
    :param window:
    :param message:
    :return:
    """
    # print('new message => ', message)
    window['-MESSAGEAREA-'](message)
    window.Refresh()


def db_connection(db_file):
    """

    :param db_file:
    :return: connection if successful else return None
    """
    try:
        conn = sqlite3.connect(db_file)
        print("sqlite3 version=", sqlite3.version)
        return conn
    except Error as e:
        print('Error: ', e)
        return None


def ewgetcategories(conn, tablename):
    sqlstring = 'SELECT Category, Notes FROM '
    sql = sqlstring + tablename + ' ORDER BY Category ; '
    # sg.Popup('sql ->', sql)
    thecategories = runsql(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def getcategories(conn, tablename):
    sqlstring = 'SELECT * FROM '
    sql = sqlstring + tablename + ' ORDER BY Category ; '
    # sg.Popup('sql ->', sql)
    thecategories = runsql(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def gettransactions(conn, tablename):
    sqlstring = 'SELECT Transaction_Id, Trans, Posted_Date, Category, Amount FROM '
    sql = sqlstring + tablename + ' ORDER BY Transaction_Id ; '
    # sg.Popup('sql ->', sql)
    thetransactions = runsql(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thetransactions:
        newtranslist = ['{:03.2f}'.format(x[4]) for x in thetransactions]

        thetransactions = [list(ele) for ele in thetransactions]
        # print('newtranslist', list(newtranslist))
        translist = [j[:4] for j in thetransactions]

        for tr in range(len(newtranslist)):
            translist[tr].append(newtranslist[tr])
        # print('translist ->', translist)
    else:
        translist = []

    return translist

'''
def getdbfilename(defaultfilename, window, thecsvfile=None):
    dbfilename = 'UNKNOWN'
    dbfilename = sg.PopupGetFile('Please enter a database file name',
                default_path=defaultfilename, keep_on_top=True, file_types=(("Sqlite Files", "*.db"),))
    if not os.path.isfile(dbfilename) and thecsvfile is not None:
        dbfilename = thecsvfile.replace('.csv', '.db')
        sg.Popup('No database File Found - a new file will be created', dbfilename, keep_on_top=True)

    return dbfilename
'''

def transupdatethecategory(conn, thenewcategory):
    # 'update TransactionList SET Category = "test category" where Transaction_Id = "20200926_237442"'
    if thenewcategory[0] != '':
        sqlstr = 'update TransactionList SET Category = ? where Transaction_Id = ?'
        runsql(conn, sqlstr, thenewcategory)


def catupdatethecategory(conn, catcategory):
    # catcategory = [ id, cat, note]
    if catcategory[0] != '':
        # sqlstr = 'update Categories SET Category = ? where Transaction_Id = ?'
        sqlstr = """
        UPDATE Categories SET 
        Category = ?,
        Notes = ?
        WHERE ID = ?
        """
        sqloutput = runsql(conn, sqlstr, catcategory)
        print('sqloutput ->', sqloutput)


def mantransupdate(conn, transid, trans, date, amount, type, category):
    # catcategory = [ id, cat, note]
    if transid != '':
        sqlstr = """
        UPDATE ManualTransactionList SET 
        Trans = ?, 
        Amount = ?, 
        Posted_Date = ?, 
        Type = ?,
        Category = ?
        WHERE Transaction_Id = ?
        """

        datalst = [trans, amount, date, type, category, transid]
        # print('sqlstr ->', sqlstr)
        # print('datalst ->', datalst)
        sqloutput = runsql(conn, sqlstr, datalst)
        # print('sqloutput ->', sqloutput)


def mantransinsert(conn, transid, trans, date, amount, type, category):
    # catcategory = [ id, cat, note]
    # INSERT INTO ManualTransactionList
    #
    # (Transaction_Id, Trans, Amount, Posted_Date, type, Category)
    #
    # VALUES ("20201109-999999", "transation name", "0.00", "2020-11-09", "DEBIT", "cash") ;

    sqlstr = """
    INSERT INTO ManualTransactionList (  
    Transaction_Id,
    Trans, 
    Amount, 
    Posted_Date, 
    Type,
    Category)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    datalst = [transid, trans, amount, date, type, category]
    # print('sqlstr ->', sqlstr)
    # print('datalst ->', datalst)
    sqloutput = runsql(conn, sqlstr, datalst)
    # print('sqloutput ->', sqloutput)



def mantransdelete(conn, transid):
    #
    # DELETE FROM ManualTransactionList	WHERE Transaction_Id = "20201109-999999" ;

    sqlstr = " DELETE FROM ManualTransactionList	WHERE Transaction_Id = ? ; "

    datalst = [transid]
    # print('sqlstr ->', sqlstr)
    # print('datalst ->', datalst)
    sqloutput = runsql(conn, sqlstr, datalst)
    # print('sqloutput ->', sqloutput)


def appendnewtransactions(conn, tablename):
    sqlstr = 'INSERT INTO TransactionList  SELECT * FROM ' + tablename + ' ;'
    # print(sqlstr)
    if runsql(conn, sqlstr):
        # print ('appendnewtransactions worked')
        sqloutput = runsql(conn, 'SELECT count(*) FROM TransactionList;')
    # sg.Popup('sqloutput=>', sqloutput)
    return sqloutput


def fillcstransactions(conn, cscategory, start, end):
    '''
    :param conn:
    :param cscategory:
    :return:
    '''
    sqlstr = ' SELECT Posted_Date, CombinedTransactionList.Trans, CombinedTransactionList.Amount, CombinedTransactionList.Category '
    sqlstr = sqlstr + ' from CombinedTransactionList '
    sqlstr = sqlstr + 'WHERE (Category = \'' + cscategory + '\') AND (Posted_Date >= \'' + start + '\') AND (Posted_Date <= \'' + end + '\')'
    sqlstr = sqlstr + ' ORDER BY Posted_Date ;'

    # print('sqlstr  ->', sqlstr)

    sqloutput = runsql(conn, sqlstr)
    # sg.Popup('sqloutput ->', sqloutput)

    if sqloutput is not None:
        sqloutput = [list(ele) for ele in sqloutput]
    return sqloutput


def filldstransactions(conn, dsdate):
    sqlstr = ''' SELECT Posted_Date, CombinedTransactionList.Trans, CombinedTransactionList.Amount, 
    CombinedTransactionList.Category from CombinedTransactionList WHERE Posted_Date = '''
    sqlstr = sqlstr + ' \'' + dsdate + '\' ORDER BY Posted_Date ; '

    sqloutput = runsql(conn, sqlstr)

    if len(sqloutput) > 0:
        # sg.Popup('sqloutput ->', sqloutput)
        sqloutput = [list(ele) for ele in sqloutput]

    return sqloutput


def gettablenames(conn):
    sqlstr = """SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"""
    sqloutput = runsql(conn, sqlstr)
    sqloutput = [list(ele) for ele in sqloutput]
    # sg.Popup('sqloutput=>', sqloutput)
    return sqloutput


def catcreaterow(conn, catcategory):
    if catcategory[0] != '':
        sqlstr = 'INSERT INTO Categories ( Category, Notes ) VALUES(?, ?)'
        sqloutput = runsql(conn, sqlstr, catcategory)
        print('sqlout ->', sqloutput)


def fillsummarylist(conn, summarystart=None, summaryend=None):

    # print('summarystartdate, summaryenddate ->', summarystart, summaryend )

    if summarystart is None:
        sqlstr = 'SELECT CombinedTransactionList.Category, sum(CombinedTransactionList.Amount) FROM CombinedTransactionList '
        sqlstr = sqlstr + ' GROUP By Category ORDER by sum(Amount);'
        sqloutput = runsql(conn, sqlstr)

    elif summaryend is None:
        sqlstr = 'SELECT CombinedTransactionList.Category, sum(CombinedTransactionList.Amount) FROM CombinedTransactionList '
        sqlstr = sqlstr + 'WHERE CombinedTransactionList.Posted_Date >= \'' + summarystart + \
                 '\'   GROUP By Category ORDER by sum(Amount);'
        # print('sql string and data ->', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    else:
        sqlstr = 'SELECT CombinedTransactionList.Category, sum(CombinedTransactionList.Amount) FROM CombinedTransactionList '
        sqlstr = sqlstr + 'WHERE CombinedTransactionList.Posted_Date >= \'' + summarystart + \
                 '\' AND  CombinedTransactionList.Posted_Date <= \'' + summaryend + '\''
        sqlstr = sqlstr + ' GROUP By Category ORDER by sum(Amount);'
        # print('sql string and data ->', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    # sqloutput = runsql(conn, sqlstr, summarystart)
    sqloutput = [list(ele) for ele in sqloutput]

    newsummarylist = ['{:03.2f}'.format(x[1]) for x in sqloutput]
    summarylist = [j.pop(0) for j in sqloutput]
    zipsummarylist = list(zip(summarylist, newsummarylist))
    # print('zipsummarylist', list(zipsummarylist))
    # summarylist = list(zipsummarylist)
    summarylist = [list(ele) for ele in zipsummarylist]
    # print('summarylist-final', summarylist)

    # print('sqlout ->', sqloutput)
    return summarylist

def filldailysummarylist(conn, summarystart=None, summaryend=None):

    # print('summarystartdate, summaryenddate ->', summarystart, summaryend )

    if summarystart is None:
        sqlstr = 'SELECT CombinedTransactionList.Posted_Date, sum(CombinedTransactionList.Amount) FROM CombinedTransactionList '
        sqlstr = sqlstr + 'WHERE CombinedTransactionList.Amount <= 0 GROUP By Posted_Date ORDER by Posted_Date;'
        sqloutput = runsql(conn, sqlstr)

    elif summaryend is None:
        sqlstr = 'SELECT CombinedTransactionList.Posted_Date, sum(CombinedTransactionList.Amount) FROM CombinedTransactionList '
        sqlstr = sqlstr + 'WHERE CombinedTransactionList.Posted_Date >= \'' + summarystart + \
                 '\'   GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data ->', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    else:
        sqlstr = 'SELECT CombinedTransactionList.Posted_Date, sum(CombinedTransactionList.Amount) FROM CombinedTransactionList '
        sqlstr = sqlstr + 'WHERE CombinedTransactionList.Posted_Date >= \'' + summarystart + \
                 '\' AND  CombinedTransactionList.Posted_Date <= \'' + summaryend + '\''
        sqlstr = sqlstr + ' GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data ->', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    # sqloutput = runsql(conn, sqlstr, summarystart)
    sqloutput = [list(ele) for ele in sqloutput]

    newsummarylist = ['{:03.2f}'.format(x[1]) for x in sqloutput]
    summarylist = [j.pop(0) for j in sqloutput]
    zipsummarylist = list(zip(summarylist, newsummarylist))
    # print('zipsummarylist', list(zipsummarylist))
    # summarylist = list(zipsummarylist)
    summarylist = [list(ele) for ele in zipsummarylist]
    # print('summarylist-final', summarylist)

    # print('sqlout ->', sqloutput)
    return summarylist


def filldailybalancelist(conn, summarystart=None, summaryend=None):

    if summarystart is None:
        sqlstr = 'SELECT TransactionList.Posted_Date, min(TransactionList.Balance) FROM TransactionList '
        sqlstr = sqlstr + ' GROUP By Posted_Date ORDER by Posted_Date;'
        sqloutput = runsql(conn, sqlstr)

    elif summaryend is None:
        sqlstr = 'SELECT TransactionList.Posted_Date, min(TransactionList.Balance) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date >= \'' + summarystart + \
                 '\'   GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data ->', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    else:
        sqlstr = 'SELECT TransactionList.Posted_Date, min(TransactionList.Balance) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date >= \'' + summarystart + \
                 '\' AND  TransactionList.Posted_Date <= \'' + summaryend + '\''
        sqlstr = sqlstr + ' GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data ->', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    # sqloutput = runsql(conn, sqlstr, summarystart)
    sqloutput = [list(ele) for ele in sqloutput]

    newsummarylist = ['{:03.2f}'.format(x[1]) for x in sqloutput]
    summarylist = [j.pop(0) for j in sqloutput]
    zipsummarylist = list(zip(summarylist, newsummarylist))
    # print('zipsummarylist', list(zipsummarylist))
    # summarylist = list(zipsummarylist)
    summarylist = [list(ele) for ele in zipsummarylist]
    # print('summarylist-final', summarylist)

    # print('sqlout ->', sqloutput)
    return summarylist

def truncateinputtable(conn, tablename):
    sqlstr = 'DELETE FROM ' + tablename + ' ;'
    if runsql(conn, sqlstr):
        return True
    else:
        return False


def open_csv_file(filepath_or_fileobj):
    # sg.Popup('open_csv_file')
    if isinstance(filepath_or_fileobj, string_types):
        fo = open(filepath_or_fileobj, mode='rt')
    return fo


# convert the CSV file to a sqlite3 table
def loadcsvfiletodb(conn, filepath_or_fileobj, table):
    global headersandtypes
    global dialect

    fo = open_csv_file(filepath_or_fileobj)
    try:
        dialect = csv.Sniffer().sniff(fo.readline())
    except TypeError:
        dialect = csv.Sniffer().sniff(str(fo.readline()))
    fo.seek(0)
    reader = csv.reader(fo, dialect)
    # Skip the header
    next(reader)

    conn.text_factory = str
    c = conn.cursor()

    sqlstr = 'INSERT INTO  %s  VALUES (%s) ' % (table, ','.join(['?'] * 13))

    for row in reader:
        runsql(conn, sqlstr, row)

    # commit the changes
    conn.commit()
    c.close()

    # the data was converted successfully
    return True


def fillmanualtransactionform(thewindow, manualtransaction):
    # window['-DAILYBALANCELISTTABLE-'](dailybalancelist)
    '''

    :param window:
    :param manualtransaction:
    :return:
    '''
    thewindow['-MANKEY-']('')
    thewindow['-MANTRANS-']('')
    thewindow['-MANDATE-']('')
    thewindow['-MANCATEGORY-']('')
    thewindow['-MANTYPE-']('')
    thewindow['-MANAMOUNT-']('')

    thewindow['-MANKEY-'](manualtransaction[0])
    thewindow['-MANTRANS-'](manualtransaction[1])
    thewindow['-MANDATE-'](manualtransaction[2])
    thewindow['-MANCATEGORY-'](manualtransaction[3])
    thewindow['-MANAMOUNT-'](manualtransaction[4])

    thewindow.refresh
    return True

def clearmanualtransactionform(thewindow):

    thewindow['-MANKEY-']('')
    thewindow['-MANTRANS-']('')
    thewindow['-MANDATE-']('')
    thewindow['-MANCATEGORY-']('')
    thewindow['-MANAMOUNT-']('')
    thewindow['-MANTYPE-']('')

    thewindow.refresh

def mangeneratetransid(window, adate):
    manualkey = adate[:4] + adate[5:7] + adate[8:10]
    manualkey = manualkey + '-' + str(random.randint(100000, 999999))
    # window['-MANKEY-'](manualkey)
    # window.refresh
    # sg.Popup('thedate ->', thedate)
    # sg.Popup('manualkey ->', manualkey)
    return manualkey


def reloadcombtransactionlist(conn):
    sqlstr1 = ' DELETE FROM CombinedTransactionList ; '

    sqlstr2 = '''
    INSERT INTO CombinedTransactionList 
    SELECT 
    TransactionList.Transaction_Id, 
    TransactionList.Trans, 
    TransactionList.Amount, 
    TransactionList.Posted_Date, 
    TransactionList.type, 
    TransactionList.Category
    From TransactionList ; '''

    sqlstr3 = '''
    INSERT INTO CombinedTransactionList 
    SELECT 
    ManualTransactionList.Transaction_Id, 
    ManualTransactionList.Trans, 
    ManualTransactionList.Amount, 
    ManualTransactionList.Posted_Date, 
    ManualTransactionList.type, 
    ManualTransactionList.Category
    From ManualTransactionList ; '''

    if runsql(conn, sqlstr1):
        if runsql(conn, sqlstr2):
            if runsql(conn, sqlstr3):
                return True
            else:
                sg.Popup('sqlstr3 FAILED')
                return False
        else:
            sg.Popup('sqlstr2 FAILED')
            return False
    else:
        sg.Popup('sqlstr1 FAILED')
        return False


def main():

    if validatedatafile(my_db_file):
        conn = db_connection(my_db_file)
    else:
        conn = None
        sg.Popup('db file %s does not exist', my_db_file)

    if conn is not None:
        try:
            if tableexists(my_db_file,'TransactionList'):
                pass
        except:
            sg.Popup('FAILED to find the tables')
            sys.exit(1)
    # read in current transactions

    transactionlist = gettransactions(conn,'Transactionlist')
    mantransactionlist = gettransactions(conn, 'ManualTransactionList')

    if reloadcombtransactionlist(conn):
        combtransactionlist = gettransactions(conn, 'CombinedTransactionList')
    else:
        sg.Popup('reloadcombtransactionlist FAILED')

    summarylist = fillsummarylist(conn)
    summaryheadings = ['Category', 'Amount']

    summarystartdate = date.today() - datetime.timedelta(days=14)
    summaryenddate = date.today()

    dailysummaryheadings = ['Day', 'Amount']
    dailysummarylist = filldailysummarylist(conn)
    dailybalancelist = filldailybalancelist(conn)

    categorylist = getcategories(conn, 'Categories')
    ewcategorylist = ewgetcategories(conn, 'Categories')
    catid = '0'
    cat = ''
    catnotes = ''

    myheadings = ['Trans_ID', 'Transaction', 'Posted', 'Category', 'Amount']
    categoryheadings = ['ID', 'Category', 'Notes']

    # PySimpleGUI screen layout
    # ------ Menu Definition ------ #
    menu_def = [['&File', ['E&xit'] , ]]

    summarytab_layout = [[sg.T('Category Summary', size=(30, 1), justification='center'),
                          sg.T('Daily Spend Summary', size=(26, 1), justification='center'),
                          sg.T('Daily Balance Summary', size=(25, 1), justification='center')],
                          [sg.Table(summarylist,
                            headings=summaryheadings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='right',
                            display_row_numbers=True,
                            alternating_row_color=mediumblue2,
                            num_rows=20,
                            enable_events=True,
                            tooltip='click on a category to drill-down',
                            key='-SUMMARYLISTTABLE-'),
                          sg.Table(dailysummarylist,
                                  headings=dailysummaryheadings,
                                  max_col_width=40,
                                  auto_size_columns=True,
                                  justification='right',
                                  display_row_numbers=True,
                                  alternating_row_color=mediumblue2,
                                  num_rows=20,
                                  enable_events=True,
                                  tooltip='click on a date to drill-down',
                                  key='-DAILYSUMMARYLISTTABLE-'),
                          sg.Table(dailybalancelist,
                                  headings=dailysummaryheadings,
                                  max_col_width=40,
                                  auto_size_columns=True,
                                  justification='right',
                                  display_row_numbers=True,
                                  alternating_row_color=mediumblue2,
                                  num_rows=20,
                                  enable_events=True,
                                  key='-DAILYBALANCELISTTABLE-')
                          ],
                         [sg.T('Start Date', size=(15, 1)), sg.T('End Date', size=(15, 1))],
                         [sg.In(str(summarystartdate), size=(17, 1),key='-SUMMARYSTARTDATE-'),
                          sg.In(str(summaryenddate), size=(17, 1), key='-SUMMARYENDDATE-'),
                          sg.Button('Run Category Report', key=('-RUNCATEGORYREPORT-')),
                          sg.Button('Run Daily Report', key=('-RUNDAILYREPORT-')),
                          sg.Button('Run Daily Balance', key=('-RUNDAILYBALANCEREPORT-'))],
                         [sg.CalendarButton('Calendar', target=(3, 0), size=(15, 1)),
                          sg.CalendarButton('Calendar', target=(3, 1), size=(15, 1)),
                          sg.T('use the calendar buttons to adjust the dates in the summary boxes and for the graphs.')]]

    graph = sg.Graph((900, 500), (0, -150), (900, 500))
    spendgraph = sg.Graph((900, 500), (0, -150), (900, 500))
    categorygraph = sg.Graph((900, 500), (0, -700), (900, 500))

    dailybalance_layout = [[sg.Button('Show balance graph', key=('-RUNGRAPH-'))],
                           [graph]]
    transactiontab_layout= [[sg.Button('Show transactions', key=('-SHOWTRANSACTIONS-'))],
                            [sg.T('Transaction List - click on a row to change the category', \
                                    size=(45, 1), justification='center')],
                            [sg.Table(transactionlist,
                                    headings=myheadings,
                                    max_col_width=40,
                                    auto_size_columns=True,
                                    justification='right',
                                    display_row_numbers=True,
                                    alternating_row_color=mediumblue2,
                                    num_rows=20,
                                    enable_events=True,
                                    tooltip='Transactions from bank',
                                    key='-TRANSACTIONLISTBOX-')],
                            [sg.Text('Filename', justification='center', size=(25, 1))],
                             [sg.Text('CSV File Name', justification='right', size=(15, 1)),
                              sg.InputText(key='-CSVFILENAME-', size=(80, 1), enable_events=True),
                              sg.FileBrowse(file_types=(('CSV Files', '*.csv'),))],
                             [sg.Button('Load CSV file and add new transactions', key='-LOADCSVFILE-', disabled=False)]
                            ]

    dailyspend_layout = [[sg.Button('Show spending graph', key=('-RUNSPENDGRAPH-'))],
                           [spendgraph]]

    categoryspend_layout = [[sg.Button('Show category graph', key=('-RUNCATEGORYGRAPH-'))],
                           [categorygraph]]

    forecasttranstab_layout = [[sg.T('Forecast Transaction List',
                                    size=(45, 1), justification='center')],
                            [sg.Table(combtransactionlist,
                                    headings=myheadings,
                                    max_col_width=40,
                                    auto_size_columns=True,
                                    justification='right',
                                    display_row_numbers=True,
                                    alternating_row_color=mediumblue2,
                                    num_rows=25,
                                    enable_events=True,
                                    tooltip='Manual Transactions',
                                    key='-COMBTRANSACTIONLISTBOX-')]
                            ]

    categorytabcol1_layout = [[sg.Table(categorylist,
                          headings=categoryheadings,
                          max_col_width=40,
                          auto_size_columns=True,
                          alternating_row_color=mediumblue2,
                          justification='left',
                          display_row_numbers=False,
                          num_rows=10,
                          enable_events=True,
                          key='-CATEGORYLISTBOX-')]]

    categorytabcol2_layout = [[sg.T('Primary Key', size=(12, 1)),
                               sg.In(catid, size=(20, 1), key='-CATID-', disabled=True)],
                              [sg.T('Category', size=(12, 1)), sg.In(cat, size=(20, 1), key='-CAT-')],
                              [sg.T('Notes', size=(12, 1)), sg.Multiline(catnotes, size=(20, 10), key='-CATNOTES-')],
                              [sg.Button('Save Changes', key='-CATSAVECHANGES-'), sg.Button('New', key='-CATNEW-')]]

    categorytabcol_layout = [[sg.Column(categorytabcol1_layout), sg.Column(categorytabcol2_layout)]]

    mantranstabcol1_layout = [[sg.T('Manual Transaction List',
                                    size=(45, 1), justification='center')],
                            [sg.Table(mantransactionlist,
                                    headings=myheadings,
                                    max_col_width=40,
                                    auto_size_columns=True,
                                    justification='right',
                                    display_row_numbers=True,
                                    alternating_row_color=mediumblue2,
                                    num_rows=25,
                                    enable_events=True,
                                    tooltip='Manual Transactions',
                                    key='-MANTRANSACTIONLISTBOX-')]
                            ]

    mantranstabcol2_layout = [[sg.T('Transaction ID', size=(15, 1)), sg.In(key='-MANKEY-', disabled=True, size=(40, 1))],
              [sg.T('Transaction', size=(15, 1)), sg.In(key='-MANTRANS-', disabled=False, size=(40, 1))],
              [sg.T('Date', size=(15, 1)), sg.In(key='-MANDATE-', disabled=True, size=(40, 1)),
               sg.CalendarButton('Calendar', target=(2, 1), size=(10, 1),format='%Y-%m-%d')],
              [sg.T('Amount', size=(15, 1)), sg.In(key='-MANAMOUNT-', disabled=False, size=(40, 1))],
              [sg.T('Type', size=(15, 1)),
               sg.Radio('Debit', '-MANRTYPE-', default=True, key='-MANRTYPED-', enable_events=True),
               sg.Radio('Credit', '-MANRTYPE-', key='-MANRTYPEC-', enable_events=True),
               sg.In('Debit', key='-MANTYPE-', disabled=True)],
              [sg.T('Category', size=(15, 1)), sg.Combo(categorylist, default_value='',
                      key='-MANCATEGORY-', enable_events=True, size=(40, 1))],
              [sg.Button('Update', key='-MANUPDATE-'), sg.Button('New', key='-MANNEW-'),
               sg.Button('Save New', key='-MANSAVENEW-'), sg.Button('Delete', key='-MANTRANSDELETE-')],
              [sg.T("Save the changes")]]

    manualtranstab_layout = [[sg.Column(mantranstabcol1_layout), sg.Column(mantranstabcol2_layout)]]

    mainscreenlayout = [
                        [sg.Menu(menu_def, )],
                        [sg.TabGroup([
                                [sg.Tab('Transaction List', transactiontab_layout, background_color=charcoal)],
                                [sg.Tab('Summary', summarytab_layout, background_color=charcoal)],
                                [sg.Tab('Daily Balance Graph', dailybalance_layout, background_color=charcoal)],
                                [sg.Tab('Daily Spending Graph', dailyspend_layout, background_color=charcoal)],
                                [sg.Tab('Category Spending Graph', categoryspend_layout, background_color=charcoal)],
                                [sg.Tab('Category', categorytabcol_layout, background_color=charcoal)],
                                [sg.Tab('Forecast Transactions', forecasttranstab_layout, background_color=charcoal)],
                                [sg.Tab('Manual Transactions', manualtranstab_layout, background_color=charcoal)]
                                ])
                        ],
                         [sg.InputText('Message Area', size=(110, 1), key='-MESSAGEAREA-', background_color='white')],
                        [sg.Exit()]]
    # sg.Popup('after Mainscreen')

    sg.SetOptions(element_padding=(2, 2))
    window = sg.Window('myFinances App', default_element_size=(15, 1), background_color=mediumgreen2).Layout(
    mainscreenlayout)
    window.Finalize()
    window.Refresh()

    # filltransactionlistbox(transactionlist, window)
    while True:  # Event Loop
        event, values = window.Read()
        if event is None or event == "Exit":
            window.Close()
            sys.exit(0)

        elif event == '-CATEGORYLISTBOX-':
            # sg.Popup('category table ->', event)
            # sg.Popup('value ->', values['-CATEGORYLISTBOX-'])
            rowid = int(values['-CATEGORYLISTBOX-'][0])
            # sg.Popup('category ->', categorylist[rowid][1])
            window['-CATID-'](categorylist[rowid][0])
            window['-CAT-'](categorylist[rowid][1])
            window['-CATNOTES-'](categorylist[rowid][2])
            window.Refresh()

        elif event == '-TRANSACTIONLISTBOX-':
            try:
                rowid = int(values['-TRANSACTIONLISTBOX-'][0])
                # sg.Popup('transaction ->', transactionlist[rowid][0])
                thenewcategory = editwindow(transactionlist[rowid], ewcategorylist)
                # sg.Popup('thenewcategory ->', thenewcategory)
                if len(thenewcategory) > 1:
                    # sg.Popup('thenewcategory is ->', thenewcategory[0])
                    transupdatethecategory(conn, thenewcategory)
                    ewcategorylist = ewgetcategories(conn, 'Categories')
                    transactionlist = gettransactions(conn, 'Transactionlist')
                    if reloadcombtransactionlist(conn):
                        combtransactionlist = gettransactions(conn, 'CombinedTransactionList')
                    else:
                        sg.Popup('reloadcombtransactionlist FAILED')

                    window['-TRANSACTIONLISTBOX-'](transactionlist)
                    window.Refresh()
            except:
                continue

        elif event == '-NEWTRANSACTIONLISTBOX-':
            rowid = int(values['-NEWTRANSACTIONLISTBOX-'][0])
            # sg.Popup('transaction ->', newtransactionlist[rowid][0])
            
        elif event == '-CATSAVECHANGES-':
            catcategory = list()
            catcategory.append(values['-CAT-'])
            catcategory.append(values['-CATNOTES-'])
            catcategory.append(values['-CATID-'])
            # print('catcategory ->', catcategory)
            catupdatethecategory(conn,catcategory)
            categorylist = getcategories(conn, 'Categories')
            window['-CATEGORYLISTBOX-'](categorylist)
            window.refresh
        
        elif event == '-CATNEW-':
            catcategory = list()
            catcategory.append(values['-CAT-'])
            catcategory.append(values['-CATNOTES-'])
            # print('catcategory ->', catcategory)
            catcreaterow(conn, catcategory)
            categorylist = getcategories(conn, 'Categories')
            window['-CATEGORYLISTBOX-'](categorylist)
            window.refresh

        elif event == '-NEWTABLELIST-':
            tablenamelist = gettablenames(conn)
            window['-TABLENAMELIST-'](tablenamelist)
            # print('tablelist ->', tablenamelist)
            window.Refresh()

        elif event == '-TABLENAMELIST-':
            # tablerowid = int(values['-TABLENAMELIST-'][0])
            csvtablename = values['-TABLENAMELIST-'][0]
            window['-CSVTABLENAME-'](csvtablename)
            window.Refresh()

        elif event == '-RUNCATEGORYREPORT-':
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            # sg.Popup('summarystartdate ->', summarystartdate)
            summarylist = fillsummarylist(conn, summarystartdate, summaryenddate)
            window['-SUMMARYLISTTABLE-'](summarylist)
            window.Refresh()

        elif event == '-RUNDAILYREPORT-':
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            # sg.Popup('summarystartdate ->', summarystartdate)
            dailysummarylist = filldailysummarylist(conn, summarystartdate, summaryenddate)
            window['-DAILYSUMMARYLISTTABLE-'](dailysummarylist)
            window.Refresh()

        elif event == '-RUNDAILYBALANCEREPORT-':
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            # sg.Popup('summarystartdate ->', summarystartdate)
            dailybalancelist = filldailybalancelist(conn, summarystartdate, summaryenddate)
            window['-DAILYBALANCELISTTABLE-'](dailybalancelist)
            window.Refresh()

        elif event == '-RUNGRAPH-':
            drawgraph(dailybalancelist, graph, scalefactor=40, lableangle=90)

        elif event == '-RUNSPENDGRAPH-':
            drawgraph(dailysummarylist, spendgraph, scalefactor=12, lableangle=90, flipgraph=True)

        elif event == '-RUNCATEGORYGRAPH-':
            drawgraph(summarylist, categorygraph, scalefactor=15, lableangle=90, flipgraph=True)

        elif event == '-SUMMARYLISTTABLE-':
            rowid = int(values['-SUMMARYLISTTABLE-'][0])
            # sg.Popup('summary category ->', summarylist[rowid][0])
            cscategory = summarylist[rowid][0]
            # print('cscategory ->', cscategory)
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            catsummarytransactions = fillcstransactions(conn, cscategory, summarystartdate, summaryenddate)
            summarywindow(catsummarytransactions)

        elif event == '-DAILYSUMMARYLISTTABLE-':
            rowid = int(values['-DAILYSUMMARYLISTTABLE-'][0])
            # sg.Popup('summary category ->', summarylist[rowid][0])
            dsdate = dailysummarylist[rowid][0]
            # sg.Popup('dsdate ->', dsdate)
            datesummarytransactions = filldstransactions(conn, dsdate)
            summarywindow(datesummarytransactions)

        elif event == '-MANTRANSACTIONLISTBOX-':
            rowid = int(values['-MANTRANSACTIONLISTBOX-'][0])
            if fillmanualtransactionform(window, mantransactionlist[rowid]):
                pass

        elif event == '-MANSAVENEW-':
            mankey = mangeneratetransid(window, values['-MANDATE-'])
            # event, values = window.Read()
            if values['-MANRTYPEC-']:
                manamount = float(values['-MANAMOUNT-'])
                if manamount < 0:
                    manamount = manamount * -1
            else:
                manamount = float(values['-MANAMOUNT-'])
                if manamount > 0:
                    manamount = manamount * -1

            mantransinsert(conn, mankey, values['-MANTRANS-'], values['-MANDATE-'],
                manamount, values['-MANTYPE-'], values['-MANCATEGORY-'][1])
            reloadcombtransactionlist(conn)
            mantransactionlist = gettransactions(conn, 'ManualTransactionList')
            window['-COMBTRANSACTIONLISTBOX-'](combtransactionlist)
            window['-MANTRANSACTIONLISTBOX-'](mantransactionlist)
            window.refresh

        elif event == '-MANRTYPEC-':
            window['-MANTYPE-']('Credit')
            window.refresh

        elif event == '-MANRTYPED-':
            window['-MANTYPE-']('Debit')
            window.refresh

        elif event == '-MANUPDATE-':
            if values['-MANRTYPEC-']:
                manrtype = 'Credit'
                manamount = float(values['-MANAMOUNT-'])
                if manamount < 0:
                    manamount = manamount * -1
            else:
                manrtype = 'Debit'
                manamount = float(values['-MANAMOUNT-'])
                if manamount > 0:
                    manamount = manamount * -1
            if len(values['-MANCATEGORY-']) == 3:
                # sg.Popup('Category3 ->', values['-MANCATEGORY-'])
                mancategory = values['-MANCATEGORY-'][1]
            else:
                # sg.Popup('Category? ->', values['-MANCATEGORY-'])
                mancategory = values['-MANCATEGORY-']
            mantransupdate(conn,values['-MANKEY-'],values['-MANTRANS-'],values['-MANDATE-'],manamount,
                    manrtype, mancategory)
            reloadcombtransactionlist(conn)
            mantransactionlist = gettransactions(conn, 'ManualTransactionList')
            window['-COMBTRANSACTIONLISTBOX-'](combtransactionlist)
            window['-MANTRANSACTIONLISTBOX-'](mantransactionlist)
            window.refresh

        elif event == '-MANTRANSDELETE-':
            mantransdelete(conn,values['-MANKEY-'])
            clearmanualtransactionform(window)
            reloadcombtransactionlist(conn)
            mantransactionlist = gettransactions(conn, 'ManualTransactionList')
            window['-COMBTRANSACTIONLISTBOX-'](combtransactionlist)
            window['-MANTRANSACTIONLISTBOX-'](mantransactionlist)
            window.refresh

        elif event == '-MANNEW-':
            clearmanualtransactionform(window)
            # window['-MANTRANSACTIONLISTBOX-'](mantransactionlist)
            # window.refresh

        elif event == '-LOADCSVFILE-':
            # sg.Popup('this button is not yet implemented')
            if truncateinputtable(conn, 'history_download'):
                # print('truncate success')
                if len(values['-CSVFILENAME-']) > 0:
                    if loadcsvfiletodb(conn, values['-CSVFILENAME-'], 'history_download'):
                        # print('loadcsvfiletodb success')
                        if (appendnewtransactions(conn, 'history_download')):
                            transactionlist = gettransactions(conn, 'Transactionlist')
                            window['-TRANSACTIONLISTBOX-'](transactionlist)
                            window.Refresh()
                            # print('appendnewtransactions success')
                        else:
                            print('appendnewtransactions failed')
                    else:
                        print('loadcsvfiletodb failed')
                else:
                    print('filename is empty')
                    sg.Popup('Please select a filename.')
            else:
                print('truncateinputtable failed')


# ##########################################
# execute the main function
if __name__ == "__main__":
    # execute only if run as a script
    main()