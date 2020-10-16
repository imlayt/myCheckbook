import sqlite3
from sqlite3 import Error
import PySimpleGUI as sg
import os
import sys
from datetime import datetime

my_db_file = 'C:/Users/imlay/Downloads/myCheckbook_appdata.db'
# my_db_file = 'myFinances-AppData.db'
# my_db_file = ''

lightblue = '#b9def4'  # color used by PySimpleGUIdef __init__(self, logfile, table='LogEntries'):
mediumblue = '#d2d2df'  # color used by PySimpleGUI
mediumblue2 = '#534aea'  # color used by PySimpleGUI
mediumgreen = '#66b3b3'  # color used by PySimpleGUI
mediumgreen2 = '#00aaaa'  # color used by PySimpleGUIs
charcoal = '#6a6a6a'

def editwindow(transactiondata, categorylist):

    sg.SetOptions(element_padding=(2, 2))

    layout = [[sg.T('Transaction ID', size=(15, 1)), sg.In(transactiondata[0], key='-EWKEY-', disabled=True)],
              [sg.T('Transaction', size=(15, 1)), sg.In(transactiondata[1], key='-EWTRANS-', disabled=True)],
              [sg.T('Amount', size=(15, 1)), sg.In(transactiondata[2], key='-EWAMOUNT-', disabled=True)],
              [sg.T('Date', size=(15, 1)), sg.In(transactiondata[3], key='-EWDATE-', disabled=True)],
              [sg.T('Category', size=(15, 1)), sg.Combo(categorylist,default_value=transactiondata[4],
                      key='-EWCATEGORY-', enable_events=True)],
              [sg.Exit(), sg.Button('Save', key='-EWSAVE-')]]
    # print('categorylist =>', categorylist)
    editwindow = sg.Window('Edit Transaction', grab_anywhere=False, keep_on_top=True).Layout(layout)
    transactionkey = str(transactiondata[0])
    newcat = []

    while True:
        event, values = editwindow.Read()
        if event is None or event == "Exit":
            editwindow.Close()
            break

        if event == '-EWSAVE-':
            newcat.append(values['-EWCATEGORY-'][0])
            newcat.append(transactionkey)
            # sg.Popup('-EWCATEGORY_ =>', newcat, keep_on_top=True)
            editwindow.Close()
            break

    return newcat


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
        # print('sqlstring =>', sqlstring)
        if rowdata:
            curr.execute(sqlstring, rowdata)
        else:
            curr.execute(sqlstring)
        # commit the changes
        conn.commit()
        # print('commit succeeded')
        sqloutput = curr.fetchall()
        return sqloutput
    except Error as e:
        print(e)
        print('runsql FAILED(', rowdata, ')')
        return False


def createrow(conn, sqlstring, rowdata):
    """

    :param conn:
    :param sqlstring:
    :param rowdata:
    :return: True if successful  else False
    """

    try:
        curr = conn.cursor()
        # print('curr creation succeeded')
        # print('sqlstring =>', sqlstring)
        curr.execute(sqlstring, rowdata)
        # commit the changes
        conn.commit()
        # print('commit succeeded')
        return True
    except Error as e:
        print(e)
        print('createrow FAILED(', rowdata, ')')
        return False


def readrows(conn, sqlstring, sqlvaluelist=None):
    """

    :param sqlstring:
    :param sqlvaluelist: values to be inserted into the sqlstring when the cursor is executed
    :return: list containing 1 or more rows or None
    """

    try:
        curr = conn.cursor()
        # print('readrows curr creation succeeded')
        if sqlvaluelist is None:
            # sg.Popup('readrows sqlvaluelist is None, sqlstring =>', sqlstring)
            # print('readrows sqlvaluelist is None, sqlstring =>', sqlstring)
            # print('sqlstring =>', sqlstring)
            curr.execute(sqlstring)
        else:
            # sg.Popup('readrows sqlvaluelist is NOT None',sqlstring, sqlvaluelist )
            # print('readrows cur.execute =>', sqlstring, ((sqlvaluelist),))
            curr.execute(sqlstring, (sqlvaluelist,))

        # print('readrows curr.execute succeeded')
        therecords = curr.fetchall()
        # print('readrows therecords => ', therecords)
        return therecords
    except Error as e:
        print('readrows error =>', e)
        return None


def updaterow(conn, sqlstring, rowdata):
    """

    :param sqlstring:
    :param rowdata:
    :return: True if successful else False
    """

    try:
        curr = conn.cursor()
        # print('curr creation succeeded')
        # print('sqlstring =>', sqlstring)
        # print('rowdata =>', rowdata)
        curr.execute(sqlstring, rowdata)
        # commit the changes
        conn.commit()
        # print('curr.execute succeeded')
        return True
    except Error as e:
        print(e)
        print('update entry FAILED(', rowdata, ')')
        print('sqlstring =>', sqlstring)
        return False


def deleterow(conn, sqlstring):
    """

    :param sqlstring:
    :return: True if successful else False
    """
    pass


def tableexists(datafile, datatable):
    """

    :param: datafile
    :param: datatable
    :return: True if successful else False
    """
    if os.path.isfile(datafile):
        try:
            conn = sqlite3.connect(datafile)

            sql2 = "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%s' ;" % tablename

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
    print('new message => ', message)
    window.FindElement('-MESSAGEAREA-').Update(message)
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
    sql = sqlstring + tablename + ' ; '
    # sg.Popup('sql =>', sql)
    thecategories = readrows(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def getcategories(conn, tablename):
    sqlstring = 'SELECT * FROM '
    sql = sqlstring + tablename + ' ; '
    # sg.Popup('sql =>', sql)
    thecategories = readrows(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def gettransactions(conn, tablename):
    sqlstring = 'SELECT Transaction_Id, Trans, Amount, Posted_Date, Category FROM '
    sql = sqlstring + tablename + ' ORDER BY Transaction_Id ; '
    # sg.Popup('sql =>', sql)
    thetransactions = readrows(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thetransactions:
        thetransactions = [list(ele) for ele in thetransactions]

    return thetransactions


def transupdatethecategory(conn, thenewcategory):
    # 'update TransactionList SET Category = "test category" where Transaction_Id = "20200926_237442"'
    if thenewcategory[0] != '':
        sqlstr = 'update TransactionList SET Category = ? where Transaction_Id = ?'
        updaterow(conn, sqlstr, thenewcategory)
        gettransactions(conn, 'Transactionlist')


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
        updaterow(conn, sqlstr, catcategory)


def getnewtransactions(conn, tablename):
    sqlstr = 'INSERT INTO TransactionList  SELECT * FROM history_download;'
    if runsql(conn, sqlstr):
        print ('getnewtransactions worked')
    sqloutput = runsql(conn, 'SELECT count(*) FROM TransactionList;')
    # sg.Popup('sqloutput=>', sqloutput)
    return sqloutput


def gettablenames(conn):
    sqlstr = """SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"""
    sqloutput = runsql(conn, sqlstr)
    # sg.Popup('sqloutput=>', sqloutput)
    return sqloutput


def catcreaterow(conn, catcategory):
    if catcategory[0] != '':
        sqlstr = 'INSERT INTO Categories ( Category, Notes ) VALUES(?, ?)'
        createrow(conn, sqlstr, catcategory)


def main():

    if validatedatafile(my_db_file):
        conn = db_connection(my_db_file)
        # fileinfo = my_db_file
    else:
        conn = None
        sg.Popup('db file %s does not exist', my_db_file)

    if conn is not None:
        try:
            # transactions = DataTable(conn, 'Transactions')
            # print('transactionlist', transactionlist)
            # sg.popup('loaded transactions')
            pass
        except:
            sg.Popup('FAILED to instantiate the tables')
            sys.exit(1)
    # read in current transactions

    transactionlist = gettransactions(conn,'Transactionlist')
    # newtransactionlist = gettransactions(conn,'NewTransactions')

    categorylist = getcategories(conn, 'Categories')
    ewcategorylist = ewgetcategories(conn, 'Categories')
    catid = '0'
    cat = ''
    catnotes = ''
    # print('Categories', categorylist)

    myheadings = [['Trans_ID'], ['Transaction'], ['Amount'], ['Posted'], ['Category']]
    categoryheadings = [['ID'], ['Category'], ['Notes']]
    # print('headings =>', myheadings)
    # PySimpleGUI screen layout
    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open', '&Save', '&Properties', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Toolbar', ['---', 'Command &1', 'Command &2', '---', 'Command &3', 'Command &4']],
                ['&Help', '&About...'] , ]

    newtransactionstab_layout = [[sg.T('old new transactions tab')]]

    '''newtransactionstab_layout = [[sg.Table(newtransactionlist,
                            headings=myheadings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='left',
                            display_row_numbers=True,
                            num_rows=10,
                            enable_events=True,
                            tooltip='New Transactions',
                            key='-NEWTRANSACTIONLISTBOX-')],
                            [sg.Button('Edit Transaction', key='-EDITNEWTRANSACTION-')]]'''

    forecasttab_layout = [[sg.T('forecast tab')]]

    categorytabcol1_layout = [[sg.Table(categorylist,
                          headings=categoryheadings,
                          max_col_width=40,
                          auto_size_columns=True,
                          alternating_row_color=lightblue,
                          justification='left',
                          display_row_numbers=False,
                          num_rows=10,
                          enable_events=True,
                          change_submits=True,
                          bind_return_key=True,
                          key='-CATEGORYLISTBOX-')]]

    categorytabcol2_layout = [[sg.T('Primary Key', size=(15, 1)), sg.In(catid, size=(20, 1), key='-CATID-', disabled=True)],
                              [sg.T('Category', size=(15, 1)), sg.In(cat, size=(20, 1), key='-CAT-')],
                              [sg.T('Notes', size=(15, 1)), sg.Multiline(catnotes, size=(35, 10), key='-CATNOTES-')],
                              [sg.Button('Save Changes', key='-CATSAVECHANGES-'), sg.Button('New', key='-CATNEW-')]]

    categorytabcol_layout = [[sg.Column(categorytabcol1_layout), sg.Column(categorytabcol2_layout)]]

    newtranstab_layout = [[sg.T('new newtrans tab')],
                          [sg.B('Add New Transactions', key='-NEWT-'), sg.B('List Tables', key='-NEWTABLELIST-')]]

    transactionlistbox_layout = [[sg.Menu(menu_def, )],
                           [sg.Table(transactionlist,
                            headings=myheadings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='left',
                            display_row_numbers=True,
                            num_rows=10,
                            enable_events=True,
                            tooltip='Old Transactions',
                            key='-OLDTRANSACTIONLISTBOX-')],
                            [sg.Button('Edit Transaction', key='-EDITOLDTRANSACTION-')]]

    mainscreenlayout = [[sg.T('Transaction List', size=(38, 1), justification='center')],
                        [sg.Menu(menu_def, )],
                         [sg.Table(transactionlist,
                                 headings=myheadings,
                                 max_col_width=40,
                                 auto_size_columns=True,
                                 justification='left',
                                 display_row_numbers=True,
                                 num_rows=10,
                                 enable_events=True,
                                 tooltip='Old Transactions',
                                 key='-TRANSACTIONLISTBOX-')],
                        [sg.TabGroup([
                                [sg.Tab('New Transactions', newtransactionstab_layout, background_color=charcoal)],
                                [sg.Tab('Forecast', forecasttab_layout, background_color=charcoal)],
                                [sg.Tab('Category', categorytabcol_layout, background_color=charcoal)],
                                [sg.Tab('Get New Transactions', newtranstab_layout, background_color=charcoal)]
                                ])
                        ],
                         [sg.InputText('Message Area', size=(110, 1), key='-MESSAGEAREA-', background_color='white')],
                        [sg.Exit()]]
    # sg.Popup('after Mainscreen')

    sg.SetOptions(element_padding=(2, 2))
    window = sg.Window('myFinances App', default_element_size=(15, 1), background_color=mediumgreen2).Layout(
    mainscreenlayout)
    window.Finalize()
    # sg.popup('after window Finalize')
    window.Refresh()

    # filltransactionlistbox(transactionlist, window)
    while True:  # Event Loop
        event, values = window.Read()
        if event is None or event == "Exit":
            window.Close()
            sys.exit(0)

        elif event == '-CATEGORYLISTBOX-':
            # sg.Popup('category table =>', event)
            # sg.Popup('value =>', values['-CATEGORYLISTBOX-'])
            rowid = int(values['-CATEGORYLISTBOX-'][0])
            # sg.Popup('category =>', categorylist[rowid][1])
            window.find_element('-CATID-').update(categorylist[rowid][0])
            window.find_element('-CAT-').update(categorylist[rowid][1])
            window.find_element('-CATNOTES-').update(categorylist[rowid][2])
            window.Refresh()

        elif event == '-TRANSACTIONLISTBOX-':
            rowid = int(values['-TRANSACTIONLISTBOX-'][0])
            # sg.Popup('transaction =>', transactionlist[rowid][0])
            thenewcategory = editwindow(transactionlist[rowid], ewcategorylist)
            # sg.Popup('thenewcategory =>', thenewcategory)
            if len(thenewcategory) > 1:
                # sg.Popup('thenewcategory is =>', thenewcategory[0])
                transupdatethecategory(conn, thenewcategory)
                ewcategorylist = ewgetcategories(conn, 'Categories')
                transactionlist = gettransactions(conn, 'Transactionlist')
                window.FindElement('-TRANSACTIONLISTBOX-').Update(transactionlist)
                window.Refresh()

        elif event == '-NEWTRANSACTIONLISTBOX-':
            rowid = int(values['-NEWTRANSACTIONLISTBOX-'][0])
            # sg.Popup('transaction =>', newtransactionlist[rowid][0])
            
        elif event == '-CATSAVECHANGES-':
            catcategory = list()
            catcategory.append(values['-CAT-'])
            catcategory.append(values['-CATNOTES-'])
            catcategory.append(values['-CATID-'])
            # print('catcategory =>', catcategory)
            catupdatethecategory(conn,catcategory)
        
        elif event == '-CATNEW-':
            catcategory = list()
            catcategory.append(values['-CAT-'])
            catcategory.append(values['-CATNOTES-'])
            # print('catcategory =>', catcategory)
            catcreaterow(conn, catcategory)
        
        elif event == '-NEWT-':
            print('NEWT')
            newrecordcount = getnewtransactions(conn, 'Transactionlist')
            messagetxt = []
            messagetxt.append ('new rec count => ')
            messagetxt.append( newrecordcount)
            setmessage(messagetxt, window )
            transactionlist = gettransactions(conn, 'Transactionlist')
            window.FindElement('-TRANSACTIONLISTBOX-').Update(transactionlist)

        elif event == '-NEWTABLELIST-':
            tablelist = gettablenames(conn)
            print('tablelist =>', tablelist)


# ##########################################
# execute the main function
if __name__=="__main__":
    # execute only if run as a script
    main()
