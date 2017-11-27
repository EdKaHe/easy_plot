# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 16:01:02 2017

@author: Ediz
"""

from bokeh.layouts import layout
from bokeh.models import PanTool, ResetTool, WheelZoomTool, SaveTool, TapTool, ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, Button, Panel, Tabs, Dropdown, CheckboxGroup, Slider
from bokeh.plotting import figure
from bokeh.io import curdoc
import pandas as pd

####################################
#import data from csv as dataframe#
##################################
data=pd.read_csv('test.csv', sep=';')
#extraxt the columns as list
columns=list(data.columns.values)
#convert pandas dataframe to bokeh columndatasource
source=ColumnDataSource(dict(x=data[columns[0]], 
                             y=data[columns[1]]))

########################################
#read and set initial values from json#
######################################
#read the saved settings
settings=pd.read_json(r'./settings.JSON', typ='series')[0]
#set all initial values
__marker=settings['marker']
__linevis_bool=settings['linevis_bool']
if __linevis_bool=='True':
    __linevis=[0]
elif __linevis_bool=='False':
    __linevis=[]
__linealpha=float(settings['linealpha'])
__linecolor=settings['linecolor']
__linewidth=int(settings['linewidth'])
__fillalpha=float(settings['fillalpha'])
__fillcolor=settings['fillcolor']
__size=int(settings['size'])

#######################################################
#this function creates labels of marker dropdown menu#
#####################################################           
def label_fn(item):
    item_str=str(item).capitalize()
    label_str='Marker ({})'.format(item_str)
    return label_str

#########################
#change data as desired#
#######################
def update_plot(attr, old, new):
    #change x and y data
    fig.xaxis.axis_label=dropdown_xdata.value
    fig.yaxis.axis_label=dropdown_ydata.value
    source.data=dict(x=data[dropdown_xdata.value],
                     y=data[dropdown_ydata.value])
    
    #change marker type and properties
    dropdown_marker.label = label_fn(dropdown_marker.value)
    for renderer_name, renderer in renderers.items():
        renderer.visible=(renderer_name == dropdown_marker.value)
        renderer.glyph.line_alpha=slider_linealpha.value
        renderer.glyph.line_color=dropdown_linecolor.value
        renderer.glyph.line_width=slider_linewidth.value
        if renderer_name!='line':
            renderer.glyph.fill_alpha=slider_fillalpha.value
            renderer.glyph.fill_color=dropdown_fillcolor.value
            renderer.glyph.size=slider_size.value
        
    #add or hide line
    if checkbox_addline.active:
        renderers['line'].visible=True        
    else:
        renderers['line'].visible=False
       
############################
#save the current settings#
##########################
def save_settings():
    if checkbox_addline.active:
        linevis_bool='True'
    else:
        linevis_bool='False'
    settings=dict(marker=[dropdown_marker.value],
                  linevis_bool=[linevis_bool],
                  linecolor=[dropdown_linecolor.value],
                  linealpha=[slider_linealpha.value],
                  linewidth=[slider_linewidth.value],
                  fillcolor=[dropdown_fillcolor.value],
                  fillalpha=[slider_fillalpha.value],
                  size=[slider_size.value]
            )
    df_settings=pd.DataFrame(settings)
    df_settings.to_json(r'./settings.JSON',orient='records')
      
#############################################################
#reset the settings to the initial settings of this session#
###########################################################
def reset_settings():
    #reset glyph properties
    for renderer_name, renderer in renderers.items():
        renderer.visible=False
        renderer.glyph.line_alpha=__linealpha
        renderer.glyph.line_width=__linewidth
        renderer.glyph.line_color=__linecolor
        if renderer_name!='line':
            renderer.glyph.fill_alpha=__fillalpha
            renderer.glyph.size=__size
            renderer.glyph.fill_color=__fillcolor
    renderers[__marker].visible=True
    if __linevis:
        renderers['line'].visible=True        
    else:
        renderers['line'].visible=False
        
    #reset widget properies
    slider_fillalpha.value=__fillalpha
    slider_linealpha.value=__linealpha
    slider_linewidth.value=__linewidth
    slider_size.value=__size
    dropdown_fillcolor.value=__fillcolor
    dropdown_linecolor.value=__linecolor
    dropdown_marker.value=__marker
    if __linevis:
        checkbox_addline.active=[0]        
    else:
        checkbox_addline.active=[]
        
################
#create figure#
##############
fig = figure(tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool(), TapTool()],output_backend='webgl')
fig.plot_width = 900
fig.plot_height = 600
fig.toolbar.logo = None

############################################################################
#create all selectable renderers and set the circle and line renderer true#
##########################################################################
renderers = {rn: getattr(fig, rn)(x='x', y='y', source=source,
                                   **extra, visible=False)
             for rn, extra in [('circle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha)),
                               ('diamond', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha)),
                               ('cross', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha)),
                               ('square', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha)),
                               ('triangle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha)),
                               ('line', dict(line_width=__linewidth, line_color=__linecolor, line_alpha=__linealpha)),]}
renderers[__marker].visible=True
if __linevis:
    renderers['line'].visible=True
else:
    renderers['line'].visible=False

#############
#style axis#
###########
fig.axis.minor_tick_line_color='black'
fig.axis.minor_tick_in=-6
fig.xaxis.axis_label=columns[0]
fig.yaxis.axis_label=columns[1]
fig.axis.axis_label_text_color=(0.7,0.7,0.7)
fig.axis.major_label_text_color=(0.7,0.7,0.7)
fig.axis.axis_label_text_font = 'helvetica'
fig.xaxis.axis_label_text_font_size = '16pt'
fig.yaxis.axis_label_text_font_size = '16pt'
fig.axis.axis_label_text_font_style = 'normal'
fig.axis.major_label_text_font = 'helvetica'
fig.axis.major_label_text_font_size = '10pt'
fig.axis.major_label_text_font_style = 'normal'

#####################
#create all widgets#
###################
#create data dropdown
menu=[(column, column) for column in columns]
dropdown_xdata = Dropdown(label="x-data", menu=menu, value=columns[0])
dropdown_ydata = Dropdown(label="y-data", menu=menu, value=columns[1])
dropdown_xdata.on_change('value', update_plot)
dropdown_ydata.on_change('value', update_plot)
#create marker dropdown
menu = [('No renderer', None)]
menu.extend((rn.capitalize(), rn) for rn in renderers if rn!='line')
dropdown_marker = Dropdown(label=label_fn(__marker), menu=menu, value=__marker)
dropdown_marker.on_change('value', update_plot)
#checkbox to hide and add line
checkbox_addline = CheckboxGroup(labels=['Add line'], active=__linevis)
checkbox_addline.on_change('active',update_plot)
#slide to adjust line_alpha
slider_linealpha = Slider(start=0, end=1, value=0.6, step=0.1, title='Line transparency')
slider_linealpha.on_change('value', update_plot)
#slide to adjust line_alpha
slider_fillalpha = Slider(start=0, end=1, value=0.2, step=0.1, title='Marker transparency')
slider_fillalpha.on_change('value', update_plot)
#create linecolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_linecolor = Dropdown(label='Line color', menu=menu, value=__linecolor)
dropdown_linecolor.on_change('value', update_plot)
#create fillcolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_fillcolor = Dropdown(label='Marker color', menu=menu, value=__fillcolor)
dropdown_fillcolor.on_change('value', update_plot)
#slide to adjust marker size
slider_size=Slider(start=0, end=30, value=__size, step=1, title='Marker size')
slider_size.on_change('value', update_plot)
#slide to adjust line width
slider_linewidth=Slider(start=0, end=10, value=__linewidth, step=1, title='Line width')
slider_linewidth.on_change('value', update_plot)
#create save button
button_save = Button(label="Save settings", button_type="success")
button_save.on_click(save_settings)
#create reset button
button_reset = Button(label="Reset settings", button_type="danger")
button_reset.on_click(reset_settings)
#create editable table widget
columns = [TableColumn(field=column, title=column) for column in columns]
table = DataTable(source=ColumnDataSource(data), columns=columns, editable=True, width=1200, height=800)
#create tab layouts
layout_plot=layout([[fig, [checkbox_addline, dropdown_marker, [slider_linealpha, slider_fillalpha], [dropdown_linecolor, dropdown_fillcolor], [slider_linewidth, slider_size], [button_reset, button_save]]],[dropdown_xdata, dropdown_ydata]])
layout_table=layout([table])
#create panels
tab_plot=Panel(child=layout_plot, title='Plot')
tab_table=Panel(child=layout_table, title='Table')
#create the tabs from panels
tabs=Tabs(tabs=[tab_plot, tab_table])

############################################
#create the layout with figure and widgets#
##########################################
layout=layout(tabs)

##############
#stream data#
############
curdoc().title='Easy Plot'
curdoc().add_root(layout)