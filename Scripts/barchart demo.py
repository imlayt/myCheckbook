import sys
import random

import PySimpleGUI as sg

mysize = (12, 1)
BAR_WIDTH = 20
BAR_SPACING = 20
EDGE_OFFSET = 3
GRAPH_SIZE = (500, 200)
DATA_SIZE = (500, 200)

bcols = ['blue', 'red', 'green', 'yellow', 'green']
myfont = "Ariel 14"

mydata = [['one', 9663.90], ['two', 40], ['three', 30]]

graph = sg.Graph(GRAPH_SIZE, (0, 0), DATA_SIZE)

layout = [[sg.Text('Pi Sensor Values', font=myfont)],
          [graph],
          [sg.Text('PI Tag 1', text_color=bcols[0], font=myfont, size=(12, 1), key='-TAG1-'),
           sg.Text('PI Tag 2', text_color=bcols[1], font=myfont, size=(12, 1), key='-TAG2-'),
           sg.Text('PI Tag 2', text_color=bcols[1], font=myfont, size=(12, 1), key='-TAG3-'),
           sg.Text('PI Tag 2', text_color=bcols[1], font=myfont, size=(12, 1), key='-TAG4-'),
           sg.Text('PI Tag 3', text_color=bcols[2], font=myfont, size=(12, 1), key='-TAG5-')],
          [sg.Exit()]]

window = sg.Window('Real Time Charts', layout)
while True:
    event, values = window.read(timeout=2000)
    if event in (None, 'Exit'):
        break

    graph.erase()
    for i in (range(len(mydata))):
        # Random value are used. Add interface to Pi sensors here:
        # graph_value = random.randint(0, 400)
        graph_value = mydata[i][1]
        graph.draw_rectangle(top_left=(i * BAR_SPACING + EDGE_OFFSET, graph_value),
                bottom_right=(i * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color='blue')
        graph.draw_text(text=str(graph_value),
                location=(i * BAR_SPACING + EDGE_OFFSET + 15, graph_value + 10), color='red', font=myfont)

window.close()