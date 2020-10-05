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

transactionlistbox = []

class DataTable:
    def __init__(self, connection, datatable):
        """

        :param connection:
        :param datatable:
        """
        self.conn = connection
        self.datatable = datatable
    pass

    def createrow(self, sqlstring, rowdata):
        """

        :param sqlstring:
        :param rowdata:
        :return: True if successful  else False
        """

        try:
            curr = self.conn.cursor()
            # print('curr creation succeeded')
            # print('sqlstring =>', sqlstring)
            curr.execute(sqlstring, rowdata)
            # commit the changes
            self.conn.commit()
            # print('commit succeeded')
            return True
        except Error as e:
            print(e)
            print('createrow FAILED(', rowdata, ')')
            return False

    def readrows(self, sqlstring, sqlvaluelist=None):
        """

        :param sqlstring:
        :param sqlvaluelist: values to be inserted into the sqlstring when the cursor is executed
        :return: list containing 1 or more rows or None
        """

        try:
            curr = self.conn.cursor()
            # sg.Popup('readrows curr creation succeeded')
            if sqlvaluelist is None:
                # sg.Popup('readrows sqlvaluelist is None, sqlstring =>', sqlstring)
                # print('readrows sqlvaluelist is None, sqlstring =>', sqlstring)
                curr.execute(sqlstring)
            else:
                # sg.Popup('readrows sqlvaluelist is NOT None',sqlstring, sqlvaluelist )
                # print('readrows cur.execute =>', sqlstring, ((sqlvaluelist),))
                curr.execute(sqlstring, (sqlvaluelist,))

            # print('readrows curr.execute succeeded')
            therecords = curr.fetchall()
            print('readrows therecords => ', therecords)
            return therecords
        except Error as e:
            print('readrows error =>', e)
            return None

    def updaterow(self, sqlstring, rowdata):
        """

        :param sqlstring:
        :param rowdata:
        :return: True if successful else False
        """

        try:
            curr = self.conn.cursor()
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

    def deleterow(self,sqlstring):
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


def filltransactionlistbox(table, window):

    global transactionlistbox
    """

    :return: company number or None
    """
    sqlstr = 'select "Transaction_Id", "Transaction" from Transactions limit 50;'
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


def main():
    """

    :return:
    """
    # global fileinfo, thecontactlog, theactionitemlist, thecontact, thecompany
    global transactionlistbox

    if validatedatafile(my_db_file):
        conn = db_connection(my_db_file)
        # fileinfo = my_db_file
    else:
        conn = None
        sg.Popup('db file %s does not exist', my_db_file)

    if conn is not None:
        try:
            transactions = DataTable(conn, 'Transactions')
            print('transactionlistbox', transactionlistbox)
            # sg.popup('loaded transactions')
        except:
            sg.Popup('FAILED to instantiate the tables')
            sys.exit(1)

    # PySimpleGUI screen layout
    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open', '&Save', '&Properties', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Toolbar', ['---', 'Command &1', 'Command &2', '---', 'Command &3', 'Command &4']],
                ['&Help', '&About...'] , ]

    contacttabcol1_layout = []

    contacttabcol2_layout = []

    actionitemlisttabcol1_layout = []

    actionitemlisttabcol2_layout = []

    contactlogtabcol1_layout = []

    contactlogtabcol2_layout = []

    myheadings = ['One', 'Two', 'Three']
    print(myheadings)
    print(transactionlistbox)

    companytabcol1_layout = [[sg.T('Transaction List', size=(38, 1),justification='center' )],
                             [sg.Table(transactionlistbox,
                                     headings=myheadings,
                                     max_col_width=100,
                                     auto_size_columns=True,
                                     justification='left',
                                     display_row_numbers=True,
                                     num_rows=10,
                                     enable_events=True,
                                     key='_TABLE_')]
                             ]
    print('transactionlistbox', transactionlistbox)
    svcompanytabcol1_layout = [sg.Table(values=transactionlistbox,
                                    headings=myheadings,
                                    max_col_width=min(round(250 / len(myheadings)),10),
                                    auto_size_columns=True,
                                    justification='left',
                                    display_row_numbers='true',
                                    alternating_row_color='lightblue',
                                    num_rows=min(len(transactionlistbox), 10), enable_events=True, key='_TABLE_')]

    companytabcol2_layout = []

    newtransactionstab_layout = [sg.Column(companytabcol2_layout, background_color=mediumgreen)]

    forecasttab_layout = [[sg.Column(contacttabcol1_layout, background_color=mediumgreen),
                          sg.Column(contacttabcol2_layout, background_color=mediumgreen)]
                         ]
    categorytab_layout = [[sg.Column(actionitemlisttabcol1_layout, background_color=mediumgreen),
                             sg.Column(actionitemlisttabcol2_layout, background_color=mediumgreen)]]

    sparetab_layout = [[sg.Column(contactlogtabcol1_layout, background_color=mediumgreen),
                             sg.Column(contactlogtabcol2_layout, background_color=mediumgreen)]]

    svmainscreenlayout = [[sg.Menu(menu_def, )],
                         [sg.Column(companytabcol1_layout, background_color='lightblue'),
                         sg.TabGroup([sg.Tab('New Transactions', newtransactionstab_layout, tooltip='tip', background_color=mediumgreen),
                                      sg.Tab('Forecast', forecasttab_layout, background_color=mediumgreen),
                                      sg.Tab('Category List', categorytab_layout, background_color=mediumgreen),
                                      sg.Tab('SPARE', sparetab_layout, background_color=mediumgreen)],
                                 tooltip='Tab Group')],
                        [sg.InputText('Message Area', size=(110, 1), key='_MESSAGEAREA_', background_color='white')],
                        sg.Exit()]

    mainscreenlayout = [
                         [sg.Column(companytabcol1_layout, background_color='lightblue'),
                        [sg.InputText('Message Area', size=(110, 1), key='_MESSAGEAREA_', background_color='white')],
                        sg.Exit()]]

    # ########################################
    # initialize main screen window
    sg.SetOptions(element_padding=(2, 2))
    window = sg.Window('myFinances App', default_element_size=(15, 1), background_color=mediumgreen2).Layout(
            mainscreenlayout)
    print(transactionlistbox)
    window.Finalize()
    sg.popup('after window Finalize')
    window.Refresh()


    # fillscreen(window,0,0)  # fill all the fields based on the first company and the first contact in that company
    #  = fillcompanylistbox(thecompany, window)
    # currentcontact = fillcontactlistbox(thecontact, window, currentcompany)
    # currentactionitem = fillactionitemlistbox(theactionitemlist, window, currentcompany)
    # currentcontactlogitem = fillcontactloglistbox(thecontactlog, window, currentcompany)
    filltransactionlistbox(Transactions, window)
    print('transactionlistbox', transactionlistbox)

    # fillcompanyrow(thecompany, currentcompany, window)
    # fillcontactrow(thecontact, currentcontact, window)
    # fillactionitemrow(theactionitemlist, currentactionitem, window)
    # fillcontactlogrow(thecontactlog, currentcontactlogitem, window)

    while True:  # Event Loop
        event, values = window.Read()
        if event is None or event=="Exit":
            window.Close()
            break

# ##########################################
# execute the main function
if __name__=="__main__":
    # execute only if run as a script
    main()
