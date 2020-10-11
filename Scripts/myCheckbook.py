import sqlite3
from sqlite3 import Error
import PySimpleGUI as sg
import os
import sys
from datetime import datetime

my_db_file = 'C:/Users/imlay/Downloads/myFinances_appdata.db'
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

    layout = [[sg.T('Transaction ID', size=(15, 1)), sg.In(transactiondata[0], key='_EWKEY_', disabled=True)],
              [sg.T('Transaction', size=(15, 1)), sg.In(transactiondata[1], key='_EWTRANS_')],
              [sg.T('Amount', size=(15, 1)), sg.In(transactiondata[2], key='_EWAMOUNT_')],
              [sg.T('Date', size=(15, 1)), sg.In(transactiondata[3], key='_EWDATE_')],
              [sg.T('Category', size=(15, 1)), sg.Combo(categorylist,default_value=transactiondata[4],
                      key='_EWCATEGORY_', enable_events=True)],
              [sg.Exit()]
              ]


    editwindow = sg.Window('Edit Transaction', grab_anywhere=False, keep_on_top=True).Layout(layout)
    newcategory = [transactiondata[0]]

    while True:
        event, values = editwindow.Read()
        if event is None or event == "Exit":
            editwindow.Close()
            break
        if event == '_EWCATEGORY_':
            newcategory.append(values['_EWCATEGORY_'])
            # sg.Popup('_EWCATEGORY_ =>', values['_EWCATEGORY_'], keep_on_top=True)

    return newcategory


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
        curr.execute(sqlstring, rowdata)
        # commit the changes
        self.conn.commit()
        # print('curr.execute succeeded')
        return True
    except Error as e:
        print(e)
        print('update entry FAILED(', rowdata, ')')
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
    window.FindElement('_MESSAGEAREA_').Update(message)
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


def getcategories(conn, tablename):
    sqlstring = 'SELECT Category FROM '
    sql = sqlstring + tablename + ' ; '
    # sg.Popup('sql =>', sql)
    thecategories = readrows(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def gettransactions(conn, tablename):
    sqlstring = 'SELECT Transaction_Id, Trans, Amount, Posted_Date, Category FROM '
    sql = sqlstring + tablename + ' ; '
    # sg.Popup('sql =>', sql)
    thetransactions = readrows(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thetransactions:
        thetransactions = [list(ele) for ele in thetransactions]

    return thetransactions


def updatethecategory(conn, thenewcategory, tablename):
    # 'update TransactionList SET Category = "test category" where Transaction_Id = "20200926_237442"'
    sqlstr = 'update TransactionList SET Category = ? where Transaction_Id = ?'
    rowdata =
    updaterow(conn, sqlstr, rowdata)




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
    newtransactionlist = gettransactions(conn,'NewTransactions')

    categorylist = getcategories(conn, 'Categories')
    # print('Categories', categorylist)

    myheadings = [['Trans_ID'], ['Transaction'], ['Amount'], ['Posted'], ['Category']]
    categoryheadings = [['Category']]
    # print('headings =>', myheadings)
    # PySimpleGUI screen layout
    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open', '&Save', '&Properties', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Toolbar', ['---', 'Command &1', 'Command &2', '---', 'Command &3', 'Command &4']],
                ['&Help', '&About...'] , ]

    newtransactionstab_layout = [[sg.Table(newtransactionlist,
                            headings=myheadings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='left',
                            display_row_numbers=True,
                            num_rows=10,
                            enable_events=True,
                            tooltip='New Transactions',
                            key='_NEWTRANSACTIONLISTBOX_')],
                            [sg.Button('Edit Transaction', key='_EDITNEWTRANSACTION_')]]

    forecasttab_layout = [[sg.T('forecast tab')]]

    categorytab_layout = [[sg.Table(categorylist,
                          headings=categoryheadings,
                          max_col_width=40,
                          auto_size_columns=True,
                          alternating_row_color=lightblue,
                          justification='left',
                          display_row_numbers=True,
                          num_rows=10,
                          enable_events=True,
                          change_submits=True,
                          bind_return_key=True,
                          key='_CATEGORYLISTBOX_')]]

    sparetab_layout = [[sg.T('new spare tab')]]

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
                            key='_OLDTRANSACTIONLISTBOX_')],
                            [sg.Button('Edit Transaction', key='_EDITOLDTRANSACTION_')]]

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
                                 key='_TRANSACTIONLISTBOX_')],
                         [sg.Button('Edit Transaction', key='_EDITOLDTRANSACTION_')],
                        [sg.TabGroup([
                                [sg.Tab('New Transactions', newtransactionstab_layout, background_color=charcoal)],
                                [sg.Tab('Forecast', forecasttab_layout, background_color=charcoal)],
                                [sg.Tab('Category', categorytab_layout, background_color=charcoal)],
                                [sg.Tab('Spare', sparetab_layout, background_color=charcoal)]
                                ])
                        ],
                         [sg.InputText('Message Area', size=(110, 1), key='_MESSAGEAREA_', background_color='white')],
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
        if event == '_CATEGORYLISTBOX_':
            # sg.Popup('category table =>', event)
            # sg.Popup('value =>', values['_CATEGORYLISTBOX_'])
            rowid = int(values['_CATEGORYLISTBOX_'][0])
            sg.Popup('category =>', categorylist[rowid][0])

        if event == '_TRANSACTIONLISTBOX_':
            rowid = int(values['_TRANSACTIONLISTBOX_'][0])
            # sg.Popup('transaction =>', transactionlist[rowid][0])
            thenewcategory = editwindow(transactionlist[rowid], categorylist)
            # sg.Popup('thenewcategory =>', thenewcategory)
            if len(thenewcategory) > 1:
                sg.Popup('thenewcategory is =>', thenewcategory[1])
                updatethecategory(thenewcategory, 'Transactions')

        if event == '_NEWTRANSACTIONLISTBOX_':
            rowid = int(values['_NEWTRANSACTIONLISTBOX_'][0])
            sg.Popup('transaction =>', newtransactionlist[rowid][0])

# ##########################################
# execute the main function
if __name__=="__main__":
    # execute only if run as a script
    main()
