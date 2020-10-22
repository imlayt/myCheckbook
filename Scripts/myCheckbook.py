import os
import sqlite3
import sys
from datetime import date
from sqlite3 import Error
import PySimpleGUI as sg

my_db_file = 'C:/Users/imlay/Downloads/myCheckbook_appdata.db'
# my_db_file = 'myFinances-AppData.db'

lightblue = '#b9def4'  # color used by PySimpleGUIdef __init__(self, logfile, table='LogEntries'):
mediumblue = '#d2d2df'  # color used by PySimpleGUI
mediumblue2 = '#534aea'  # color used by PySimpleGUI
mediumgreen = '#66b3b3'  # color used by PySimpleGUI
mediumgreen2 = '#00aaaa'  # color used by PySimpleGUIs
charcoal = '#6a6a6a'


def drawgraph(datalist, graph, scalefactor=None, lableangle=None, flipgraph=None):

    BAR_WIDTH = 17
    BAR_SPACING = 17
    EDGE_OFFSET = 3
    mediumgreen2 = '#00aaaa'  # color used by PySimpleGUIs

    myfont = "Ariel 10"
    if scalefactor is None:
        scalefactor = 1

    if lableangle is None:
        lableangle = 60

    graph.erase()
    for i in (range(len(datalist))):
        display_value = (float(datalist[i][1])).__round__(0)
        graph_value = (float(datalist[i][1])/scalefactor).__round__(0)    # divide by scalefactor to make the bars fit on the chart
        # print('graph_value', graph_value)
        if flipgraph:
            graph_value = graph_value * -1

        graph.draw_rectangle(top_left=(i * BAR_SPACING + EDGE_OFFSET, graph_value),
                bottom_right=(i * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=mediumgreen2)
        graph.draw_text(text=str(display_value),
            location=(i * BAR_SPACING + EDGE_OFFSET + 17, graph_value + 40), color='white', font=myfont, angle=lableangle)


def editwindow(transactiondata, categorylist):

    sg.SetOptions(element_padding=(2, 2))

    layout = [[sg.T('Transaction ID', size=(15, 1)), sg.In(transactiondata[0], key='-EWKEY-', disabled=True)],
              [sg.T('Transaction', size=(15, 1)), sg.In(transactiondata[1], key='-EWTRANS-', disabled=True)],
              [sg.T('Amount', size=(15, 1)), sg.In(transactiondata[2], key='-EWAMOUNT-', disabled=True)],
              [sg.T('Date', size=(15, 1)), sg.In(transactiondata[3], key='-EWDATE-', disabled=True)],
              [sg.T('Category', size=(15, 1)), sg.Combo(categorylist,default_value=transactiondata[4],
                      key='-EWCATEGORY-', enable_events=True)],
              [sg.Exit(), sg.Button('Save', key='-EWSAVE-')],
              [sg.T("Exit doesn't save the changes")]]
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
    thecategories = runsql(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def getcategories(conn, tablename):
    sqlstring = 'SELECT * FROM '
    sql = sqlstring + tablename + ' ; '
    # sg.Popup('sql =>', sql)
    thecategories = runsql(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thecategories:
        thecategories = [list(ele) for ele in thecategories]

    return thecategories

def gettransactions(conn, tablename):
    sqlstring = 'SELECT Transaction_Id, Trans, Amount, Posted_Date, Category FROM '
    sql = sqlstring + tablename + ' ORDER BY Transaction_Id ; '
    # sg.Popup('sql =>', sql)
    thetransactions = runsql(conn, sql)

    # res = [list(ele) for ele in test_list]
    if thetransactions:
        thetransactions = [list(ele) for ele in thetransactions]

    return thetransactions


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
        print('sqloutput =>', sqloutput)

def getnewtransactions(conn, tablename):
    # print('tablename =>', tablename[1:len(tablename)-2])
    # tablename = [list(ele) for ele in tablename]
    # print('tablename =>', tablename[1:len(tablename)-2])
    sqlstr = 'INSERT INTO TransactionList  SELECT * FROM ' + tablename[1:len(tablename)-2] + ' ;'
    # print(sqlstr)
    if runsql(conn, sqlstr):
        print ('getnewtransactions worked')
    sqloutput = runsql(conn, 'SELECT count(*) FROM TransactionList;')
    # sg.Popup('sqloutput=>', sqloutput)
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
        print('sqlout =>', sqloutput)


def fillsummarylist(conn, summarystart=None, summaryend=None):

    # print('summarystartdate, summaryenddate =>', summarystart, summaryend )

    if summarystart is None:
        sqlstr = 'SELECT TransactionList.Category, sum(TransactionList.Amount) FROM TransactionList '
        sqlstr = sqlstr + ' GROUP By Category ORDER by Category;'
        sqloutput = runsql(conn, sqlstr)

    elif summaryend is None:
        sqlstr = 'SELECT TransactionList.Category, sum(TransactionList.Amount) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date > \'' + summarystart + \
                 '\'   GROUP By Category ORDER by Category;'
        # print('sql string and data =>', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    else:
        sqlstr = 'SELECT TransactionList.Category, sum(TransactionList.Amount) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date > \'' + summarystart + \
                 '\' AND  TransactionList.Posted_Date < \'' + summaryend + '\''
        sqlstr = sqlstr + ' GROUP By Category ORDER by Category;'
        # print('sql string and data =>', sqlstr)
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

    # print('sqlout =>', sqloutput)
    return summarylist

def filldailysummarylist(conn, summarystart=None, summaryend=None):

    # print('summarystartdate, summaryenddate =>', summarystart, summaryend )

    if summarystart is None:
        sqlstr = 'SELECT TransactionList.Posted_Date, sum(TransactionList.Amount) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Amount < 0 GROUP By Posted_Date ORDER by Posted_Date;'
        sqloutput = runsql(conn, sqlstr)

    elif summaryend is None:
        sqlstr = 'SELECT TransactionList.Posted_Date, sum(TransactionList.Amount) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date => \'' + summarystart + \
                 '\'   GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data =>', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    else:
        sqlstr = 'SELECT TransactionList.Posted_Date, sum(TransactionList.Amount) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date > \'' + summarystart + \
                 '\' AND  TransactionList.Posted_Date < \'' + summaryend + '\''
        sqlstr = sqlstr + ' GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data =>', sqlstr)
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

    # print('sqlout =>', sqloutput)
    return summarylist


def filldailybalancelist(conn, summarystart=None, summaryend=None):

    if summarystart is None:
        sqlstr = 'SELECT TransactionList.Posted_Date, min(TransactionList.Balance) FROM TransactionList '
        sqlstr = sqlstr + ' GROUP By Posted_Date ORDER by Posted_Date;'
        sqloutput = runsql(conn, sqlstr)

    elif summaryend is None:
        sqlstr = 'SELECT TransactionList.Posted_Date, min(TransactionList.Balance) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date > \'' + summarystart + \
                 '\'   GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data =>', sqlstr)
        sqloutput = runsql(conn, sqlstr)

    else:
        sqlstr = 'SELECT TransactionList.Posted_Date, min(TransactionList.Balance) FROM TransactionList '
        sqlstr = sqlstr + 'WHERE TransactionList.Posted_Date > \'' + summarystart + \
                 '\' AND  TransactionList.Posted_Date < \'' + summaryend + '\''
        sqlstr = sqlstr + ' GROUP By Posted_Date ORDER by Posted_Date;'
        # print('sql string and data =>', sqlstr)
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

    # print('sqlout =>', sqloutput)
    return summarylist


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

    tablenamelist = gettablenames(conn)
    csvtablename = []

    summarylist = fillsummarylist(conn)

    summaryheadings = ['Category', 'Amount']
    summarystartdate = date.today()
    summaryenddate = date.today()

    dailysummarylist = filldailysummarylist(conn)
    dailysummaryheadings = ['Day', 'Amount']
    # print('dailysummarylist =>', dailysummarylist)

    dailybalancelist = filldailybalancelist(conn)
    dailysummaryheadings = ['Day', 'Amount']

    categorylist = getcategories(conn, 'Categories')
    ewcategorylist = ewgetcategories(conn, 'Categories')
    catid = '0'
    cat = ''
    catnotes = ''
    # print('Categories', categorylist)

    myheadings = ['Trans_ID', 'Transaction', 'Amount', 'Posted', 'Category']
    categoryheadings = ['ID', 'Category', 'Notes']

    # PySimpleGUI screen layout
    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open', '&Save', '&Properties', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Toolbar', ['---', 'Command &1', 'Command &2', '---', 'Command &3', 'Command &4']],
                ['&Help', '&About...'] , ]

    summarytab_layout = [[sg.T('Summary by Category', size=(30, 1)),
                          sg.T('Daily Spend Summary', size=(26, 1)),
                          sg.T('Daily Balance Summary', size=(30, 1))],
                          [sg.Table(summarylist,
                            headings=summaryheadings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='right',
                            display_row_numbers=True,
                            alternating_row_color=mediumblue2,
                            num_rows=10,
                            enable_events=True,
                            key='-SUMMARYLISTTABLE-'),
                          sg.Table(dailysummarylist,
                                  headings=dailysummaryheadings,
                                  max_col_width=40,
                                  auto_size_columns=True,
                                  justification='right',
                                  display_row_numbers=True,
                                  alternating_row_color=mediumblue2,
                                  num_rows=10,
                                  enable_events=True,
                                  key='-DAILYSUMMARYLISTTABLE-'),
                          sg.Table(dailybalancelist,
                                  headings=dailysummaryheadings,
                                  max_col_width=40,
                                  auto_size_columns=True,
                                  justification='right',
                                  display_row_numbers=True,
                                  alternating_row_color=mediumblue2,
                                  num_rows=10,
                                  enable_events=True,
                                  key='-DAILYBALANCELISTTABLE-')
                          ],
                         [sg.T('Start Date', size=(15, 1)), sg.T('End Date', size=(15, 1))],
                         [sg.In(str(summarystartdate), size=(17, 1),key='-SUMMARYSTARTDATE-'),
                          sg.In(str(summaryenddate), size=(17, 1), key='-SUMMARYENDDATE-'),
                          sg.Button('Run CategoryReport', key=('-RUNREPORT-')),
                          sg.Button('Run Daily Report', key=('-RUNDAILYREPORT-')),
                          sg.Button('Run Daily Balance', key=('-RUNDAILYBALANCEREPORT-'))],
                         [sg.CalendarButton('Calendar', target=(3, 0), size=(15, 1)),
                          sg.CalendarButton('Calendar', target=(3, 1), size=(15, 1)),
                          sg.T('use the calendar buttons to adjust the dates in the summary boxes and for the graphs.')]]

    graph = sg.Graph((750, 250), (0, -100), (750, 250))
    spendgraph = sg.Graph((750, 250), (0, -20), (750, 250))

    dailybalance_layout = [[sg.Button('Show balance graph', key=('-RUNGRAPH-'))],
                           [graph]]

    dailyspend_layout = [[sg.Button('Show spending graph', key=('-RUNSPENDGRAPH-'))],
                           [spendgraph]]

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

    newtranstab_layout = [[sg.T('new newtrans tab')],
                          [sg.Listbox(tablenamelist, size=(30, 10) , enable_events=True, key='-TABLENAMELIST-')],
                          [sg.In(csvtablename, size=(30, 1), key='-CSVTABLENAME-')],
                          [ sg.B('List Tables', key='-NEWTABLELIST-'), sg.B('Add New Transactions', key='-NEWT-')]]

    transactionlistbox_layout = [[sg.Menu(menu_def, )],
                           [sg.Table(transactionlist,
                            headings=myheadings,
                            max_col_width=40,
                            auto_size_columns=True,
                            justification='left',
                            display_row_numbers=True,
                            alternating_row_color=mediumblue2,
                            num_rows=10,
                            enable_events=True,
                            tooltip='Old Transactions',
                            key='-OLDTRANSACTIONLISTBOX-')],
                            [sg.Button('Edit Transaction', key='-EDITOLDTRANSACTION-')]]

    mainscreenlayout = [[sg.T('Transaction List - click on a row to change the category', \
                        size=(45, 1), justification='center')],
                        [sg.Menu(menu_def, )],
                         [sg.Table(transactionlist,
                                 headings=myheadings,
                                 max_col_width=40,
                                 auto_size_columns=True,
                                 justification='left',
                                 display_row_numbers=True,
                                 alternating_row_color=mediumblue2,
                                 num_rows=10,
                                 enable_events=True,
                                 tooltip='Old Transactions',
                                 key='-TRANSACTIONLISTBOX-')],
                        [sg.TabGroup([
                                [sg.Tab('Summary', summarytab_layout, background_color=charcoal)],
                                [sg.Tab('Daily Balance Graph', dailybalance_layout, background_color=charcoal)],
                                [sg.Tab('Daily Spending Graph', dailyspend_layout, background_color=charcoal)],
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
            window['-CATID-'](categorylist[rowid][0])
            window['-CAT-'](categorylist[rowid][1])
            window['-CATNOTES-'](categorylist[rowid][2])
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
                window['-TRANSACTIONLISTBOX-'](transactionlist)
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
            categorylist = getcategories(conn, 'Categories')
            window['-CATEGORYLISTBOX-'](categorylist)
            window.refresh
        
        elif event == '-CATNEW-':
            catcategory = list()
            catcategory.append(values['-CAT-'])
            catcategory.append(values['-CATNOTES-'])
            # print('catcategory =>', catcategory)
            catcreaterow(conn, catcategory)
            categorylist = getcategories(conn, 'Categories')
            window['-CATEGORYLISTBOX-'](categorylist)
            window.refresh
        
        elif event == '-NEWT-':
            inputtable = values['-CSVTABLENAME-']
            # print('inputtable =>', inputtable)
            if len(inputtable) > 0:
                newrecordcount = getnewtransactions(conn, inputtable)
                messagetxt = []
                messagetxt.append ('new rec count => ')
                messagetxt.append( newrecordcount)
                setmessage(messagetxt, window )
                transactionlist = gettransactions(conn, 'Transactionlist')
                window['-TRANSACTIONLISTBOX-'](transactionlist)
            else:
                sg.Popup('inputtable is empty')

        elif event == '-NEWTABLELIST-':
            tablenamelist = gettablenames(conn)
            window['-TABLENAMELIST-'](tablenamelist)
            # print('tablelist =>', tablenamelist)
            window.Refresh()

        elif event == '-TABLENAMELIST-':
            # tablerowid = int(values['-TABLENAMELIST-'][0])
            csvtablename = values['-TABLENAMELIST-'][0]
            window['-CSVTABLENAME-'](csvtablename)
            window.Refresh()

        elif event == '-RUNREPORT-':
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            # sg.Popup('summarystartdate =>', summarystartdate)
            summarylist = fillsummarylist(conn, summarystartdate, summaryenddate)
            window['-SUMMARYLISTTABLE-'](summarylist)
            window.Refresh()

        elif event == '-RUNDAILYREPORT-':
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            # sg.Popup('summarystartdate =>', summarystartdate)
            dailysummarylist = filldailysummarylist(conn, summarystartdate, summaryenddate)
            window['-DAILYSUMMARYLISTTABLE-'](dailysummarylist)
            window.Refresh()

        elif event == '-RUNDAILYBALANCEREPORT-':
            summarystartdate = values['-SUMMARYSTARTDATE-'][0:10]
            summaryenddate = values['-SUMMARYENDDATE-'][0:10]
            # sg.Popup('summarystartdate =>', summarystartdate)
            dailybalancelist = filldailybalancelist(conn, summarystartdate, summaryenddate)
            window['-DAILYBALANCELISTTABLE-'](dailybalancelist)
            window.Refresh()

        elif event == '-RUNGRAPH-':
            drawgraph(dailybalancelist, graph, scalefactor=40, lableangle=90)

        elif event == '-RUNSPENDGRAPH-':

            drawgraph(dailysummarylist, spendgraph, scalefactor=12, lableangle=90, flipgraph=True)


# ##########################################
# execute the main function
if __name__ == "__main__":
    # execute only if run as a script
    main()
