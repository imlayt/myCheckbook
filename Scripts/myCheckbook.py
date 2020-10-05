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


def filltransactionlistbox(table, window=None):

    global transactionlistbox
    """

    :return: company number or None
    """
    sqlstr = 'select "Transaction_Id", "Transaction" from ? limit ;'
    print('sqlstr', sqlstr)
    try:
        print('transactionlistbox = table.readrows(sqlstr)')
        transactionlistbox = table.readrows(sqlstr)
        # companynumber = companyboxlist[0][1]
        # print('currentcompany =>', companynumber)
        print('transactionlistbox =>', transactionlistbox)
        window.FindElement('_TRANSACTIONLISTBOX_').Update(transactionlistbox)
        window.FindElement('_TABLE_').Update(transactionlistbox)
        window.Refresh()
        return None
    except:
        print('fillcompanylistbox FAILED')
        window.FindElement('_TRANSACTIONLISTBOX_').Update('')
        window.FindElement('_TABLE_').Update('')
        return None


def gettransactions(conn, tablename):
    sqlstring = 'SELECT Transaction_Id, Trans, Amount, Posted_Date, Balance FROM '
    sql = sqlstring + tablename + ' ; '
    # sg.Popup('sql =>', sql)
    thetransactions = readrows(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thetransactions:
        thetransactions = [list(ele) for ele in thetransactions]

    return thetransactions


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

    myheadings = [['Trans_ID'], ['Transaction'], ['Amount'], ['Posted'], ['Balance']]
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
                            key='_NEWTRANSACTIONLISTBOX_')]]

    forecasttab_layout =  [[sg.T('forecast tab')]]

    categorytab_layout = [[sg.T('new category tab')]]
    sparetab_layout = [[sg.T('new spare tab')]]

    transactionlistbox_layout = [[sg.T('Transaction List', size=(38, 1),justification='center' )],
                             [sg.Table(transactionlist,
                                     headings=myheadings,
                                     max_col_width=40,
                                     auto_size_columns=True,
                                     justification='left',
                                     display_row_numbers=True,
                                     num_rows=10,
                                     enable_events=True,
                                     key='_TRANSACTIONLISTBOX_')]]

    mainscreenlayout = [[sg.Menu(menu_def, )],
                        [sg.T('Transaction List', size=(38, 1), justification='center')],
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
                        [sg.TabGroup([[sg.Tab('New Transactions', newtransactionstab_layout,
                                background_color=mediumgreen)],
                                      [sg.Tab('Forecast', forecasttab_layout, background_color=charcoal)],
                                      [sg.Tab('Category', categorytab_layout, background_color='white')],
                                      [sg.Tab('Spare', sparetab_layout, background_color=mediumgreen2)]
                                      ],
                                )],
                         [sg.InputText('Message Area', size=(110, 1), key='_MESSAGEAREA_', background_color='white')],
                        [sg.Exit()]]

    # read in transactions
    transactionlist = gettransactions(conn, 'Transactionlist')
    newtransactionlist = gettransactions(conn, 'newtransactions')
    # print(transactionlist)


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


# fill list boxes
    #

# ##########################################
# execute the main function
if __name__=="__main__":
    # execute only if run as a script
    main()
