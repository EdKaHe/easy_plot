# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 16:01:02 2017

@author: Ediz
"""

from bokeh.layouts import layout
from bokeh.models import PanTool, BoxZoomTool, BoxSelectTool, ResetTool, WheelZoomTool, SaveTool, TapTool, ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, Button, Panel, Tabs, Dropdown, Slider, Select, TextInput
from bokeh.plotting import figure
from bokeh.io import curdoc
import pandas as pd
import xlrd
from numpy import exp,log,log10,sin,sinc,sinh,cos,cosh,tan,tanh, nan
from scipy import optimize
from time import sleep

####################################
#import data from csv as dataframe#
##################################
filepath='test.xlsx'
try:
    data=pd.read_excel(filepath, sep=';')
except xlrd.XLRDError:
    data=pd.read_csv(filepath, sep=';')
#extraxt the columns as list
columns=list(data.columns.values)
#convert pandas dataframe to bokeh columndatasource
source_plot=ColumnDataSource(data=dict(x=data[columns[0]], 
                             y=data[columns[1]]))
source_table=ColumnDataSource(data=data)
source_fit=ColumnDataSource(data=dict(x=[0 for i in range(data.shape[0])], 
                             y=[0 for i in range(data.shape[0])]))

########################################
#read and set initial values from json#
######################################
#read the saved settings
settings=pd.read_json(r'./settings.JSON', typ='series')[0]
#set all initial values
dict_linedash=dict(none=[], solid=[1],dashed=[8,8],dotted=[2,6])#required to convert string to array
__marker=settings['marker']
__linedash=settings['linedash']
__linealpha=float(settings['linealpha'])
__linecolor=settings['linecolor']
__linewidth=int(settings['linewidth'])
__fillalpha=float(settings['fillalpha'])
__fillcolor=settings['fillcolor']
__size=int(settings['size'])

#######################################################
#this function creates labels of marker dropdown menu#
#####################################################           
def label_marker(item):
    item_str=str(item).capitalize()
    label_str='Marker ({})'.format(item_str)
    return label_str

def label_linedash(item):
    item_str=str(item).capitalize()
    label_str='Line ({})'.format(item_str)
    return label_str

def label_fillcolor(item):
    item_str=str(item).capitalize()
    label_str='Marker color ({})'.format(item_str)
    return label_str

def label_linecolor(item):
    item_str=str(item).capitalize()
    label_str='Line color ({})'.format(item_str)
    return label_str

#####################################################
#function to match plot and table data periodically#
###################################################
def update():
    source_plot.data=dict(x=source_table.data[select_xdata.value],
                          y=source_table.data[select_ydata.value])

#########################
#change data as desired#
#######################
def update_plot(attr, old, new):
    #change x and y data
    fig_one.xaxis.axis_label=select_xdata.value
    fig_one.yaxis.axis_label=select_ydata.value
    source_plot.data=dict(x=source_table.data[select_xdata.value],
                     y=source_table.data[select_ydata.value])
    
    #change marker type and properties
    dropdown_marker.label=label_marker(dropdown_marker.value)
    dropdown_fillcolor.label=label_fillcolor(dropdown_fillcolor.value)
    dropdown_linecolor.label=label_linecolor(dropdown_linecolor.value)
    dropdown_linedash.label=label_linedash(dropdown_linedash.value)
    for renderer_name, renderer in renderers.items():
        renderer.visible=(renderer_name == dropdown_marker.value)
        renderer.glyph.line_alpha=slider_linealpha.value
        renderer.glyph.line_color=dropdown_linecolor.value
        renderer.glyph.line_dash=dict_linedash[dropdown_linedash.value]
        renderer.glyph.line_width=slider_linewidth.value
        if renderer_name!='line':
            renderer.glyph.fill_alpha=slider_fillalpha.value
            renderer.glyph.fill_color=dropdown_fillcolor.value
            renderer.glyph.size=slider_size.value
            
    #add or hide line
    if dropdown_linedash.value=='none':
        renderers['line'].visible=False
    else:
        renderers['line'].visible=True
        
    #update fit figure
    for renderer_name, renderer in renderers_data_fit.items():
        renderer.visible=False
        renderer.glyph.line_alpha=slider_linealpha.value
        renderer.glyph.line_width=slider_linewidth.value
        renderer.glyph.line_color=dropdown_linecolor.value
        renderer.glyph.line_dash=dict_linedash[dropdown_linedash.value]
        if renderer_name!='line':
            renderer.glyph.fill_alpha=slider_fillalpha.value
            renderer.glyph.size=slider_size.value
            renderer.glyph.fill_color=dropdown_fillcolor.value
    renderers_data_fit[dropdown_marker.value].visible=True
    if dropdown_linedash.value=='none':
        renderers_data_fit['line'].visible=False        
    else:
        renderers_data_fit['line'].visible=True

########################
#change fit as desired#
#######################
def update_fit(attr, old, new):  
    #change marker type and properties
    dropdown_marker_fit.label=label_marker(dropdown_marker_fit.value)
    dropdown_fillcolor_fit.label=label_fillcolor(dropdown_fillcolor_fit.value)
    dropdown_linecolor_fit.label=label_linecolor(dropdown_linecolor_fit.value)
    dropdown_linedash_fit.label=label_linedash(dropdown_linedash_fit.value)
    for renderer_name, renderer in renderers_model_fit.items():
        renderer.visible=(renderer_name == dropdown_marker_fit.value)
        renderer.glyph.line_alpha=slider_linealpha_fit.value
        renderer.glyph.line_color=dropdown_linecolor_fit.value
        renderer.glyph.line_width=slider_linewidth_fit.value
        renderer.glyph.line_dash=dict_linedash[dropdown_linedash_fit.value]
        if renderer_name!='line':
            renderer.glyph.fill_alpha=slider_fillalpha_fit.value
            renderer.glyph.fill_color=dropdown_fillcolor_fit.value
            renderer.glyph.size=slider_size_fit.value
            
    #add or hide line
    if dropdown_linedash_fit.value=='none':
        renderers_model_fit['line'].visible=False
    else:
        renderers_model_fit['line'].visible=True
        
############################
#save the current settings#
##########################
def save_settings():
    settings=dict(marker=[dropdown_marker.value],
                  linedash=[dropdown_linedash.value],
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
        renderer.glyph.line_dash=dict_linedash[__linedash]
        if renderer_name!='line':
            renderer.glyph.fill_alpha=__fillalpha
            renderer.glyph.size=__size
            renderer.glyph.fill_color=__fillcolor
    renderers[__marker].visible=True
    if __linedash=='none':
        renderers['line'].visible=False        
    else:
        renderers['line'].visible=True
        
    #reset widget properies
    slider_fillalpha.value=__fillalpha
    slider_linealpha.value=__linealpha
    slider_linewidth.value=__linewidth
    slider_size.value=__size
    dropdown_fillcolor.value=__fillcolor
    dropdown_linecolor.value=__linecolor
    dropdown_marker.value=__marker
    dropdown_linedash.value=__linedash

#create function that adds data from left plot to the right permanently 
def add_plot():
    #add marker to plot
    new_data=source_plot.data
    renderer=getattr(fig_all, dropdown_marker.value)(x=new_data['x'], y=new_data['y'], legend=select_ydata.value, muted_color=dropdown_fillcolor.value, muted_alpha=slider_fillalpha.value*0.1)
    #change marker properties
    renderer.glyph.line_width=slider_linewidth.value
    renderer.glyph.line_color=dropdown_linecolor.value
    renderer.glyph.line_alpha=slider_linealpha.value
    renderer.glyph.size=slider_size.value
    renderer.glyph.fill_color=dropdown_fillcolor.value
    renderer.glyph.fill_alpha=slider_fillalpha.value
    
    #change line properties if line is visible
    if dropdown_linedash.value!='none':
        renderer=getattr(fig_all, 'line')(x=new_data['x'], y=new_data['y'], legend=select_ydata.value, muted_color=dropdown_linecolor.value, muted_alpha=slider_linealpha.value*0.1)
        renderer.glyph.line_width=slider_linewidth.value
        renderer.glyph.line_color=dropdown_linecolor.value
        renderer.glyph.line_alpha=slider_linealpha.value
    
    #change axis labels
    fig_all.xaxis.axis_label=select_xdata.value
    fig_all.yaxis.axis_label=select_ydata.value
    
    #update texboxes only if user didn't create labels
    if not user_labels:
        text_xlabel.value=select_xdata.value
        text_ylabel.value=select_ydata.value
        
    fig_all.legend.location = "top_left"
    fig_all.legend.click_policy="mute"

#create function that changes axis labels after user input
def change_label(attr, old, new):
    #set user input true so that it is not changed automatically anymore
    global user_labels
    user_labels=True
    
    #change the axis labels
    fig_all.xaxis.axis_label=text_xlabel.value
    fig_all.yaxis.axis_label=text_ylabel.value
    
#create function that fits data from function given as string
def fit_data(attr, old, new):
    global parameter
    func=lambda x,a,b,c,d,e: eval(text_fit.value)
    try:
        parameter,_=optimize.curve_fit(func, source_plot.data['x'],source_plot.data['y'])
    except RuntimeError:
        tmp_str=text_fit.title
        for i in range(5):
            text_fit.title='Parameter not found!'
            sleep(0.2)
            text_fit.title=''
            sleep(0.2)
        text_fit.title=tmp_str
        return
    
    x_data=source_plot.data['x']
    y_data=func(source_plot.data['x'], *parameter)
    source_fit.data=dict(x=x_data,y=y_data)    
    
###########################################################################################################################################
###########################################################plot tab########################################################################
###########################################################################################################################################

################
#create figure#
##############
fig_one = figure(toolbar_location='right', toolbar_sticky=False, tools=[PanTool(), BoxZoomTool(), WheelZoomTool(), BoxSelectTool(), TapTool(), ResetTool(), SaveTool()],output_backend='webgl')
fig_one.plot_width = 600
fig_one.plot_height = 300
fig_one.toolbar.logo = None

fig_all = figure(toolbar_location='right', toolbar_sticky=False, tools=[PanTool(), BoxZoomTool(), WheelZoomTool(), BoxSelectTool(), TapTool(), ResetTool(), SaveTool()],output_backend='webgl')
fig_all.plot_width = 800
fig_all.plot_height = 600
fig_all.toolbar.logo = None

############################################################################
#create all selectable renderers and set the circle and line renderer true#
##########################################################################
renderers = {rn: getattr(fig_one, rn)(x='x', y='y', source=source_plot,
                                   **extra, visible=False)
             for rn, extra in [('line', dict(line_width=__linewidth, line_color=__linecolor, line_alpha=__linealpha, line_dash=dict_linedash[__linedash])),
                               ('circle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('diamond', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('square', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('triangle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('asterisk', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('cross', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('x', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash]))]}
renderers[__marker].visible=True
if __linedash=='none':
    renderers['line'].visible=False
else:
    renderers['line'].visible=True

#############
#style axis#
###########
fig_one.axis.minor_tick_line_color='black'
fig_one.axis.minor_tick_in=-6
fig_one.xaxis.axis_label=columns[0]
fig_one.yaxis.axis_label=columns[1]
fig_one.axis.axis_label_text_color=(0.7,0.7,0.7)
fig_one.axis.major_label_text_color=(0.7,0.7,0.7)
fig_one.axis.axis_label_text_font = 'helvetica'
fig_one.xaxis.axis_label_text_font_size = '12pt'
fig_one.yaxis.axis_label_text_font_size = '12pt'
fig_one.axis.axis_label_text_font_style = 'normal'
fig_one.axis.major_label_text_font = 'helvetica'
fig_one.axis.major_label_text_font_size = '10pt'
fig_one.axis.major_label_text_font_style = 'normal'

fig_all.axis.minor_tick_line_color='black'
fig_all.axis.minor_tick_in=-6
fig_all.xaxis.axis_label=''
fig_all.yaxis.axis_label=''
fig_all.axis.axis_label_text_color=(0.7,0.7,0.7)
fig_all.axis.major_label_text_color=(0.7,0.7,0.7)
fig_all.axis.axis_label_text_font = 'helvetica'
fig_all.xaxis.axis_label_text_font_size = '16pt'
fig_all.yaxis.axis_label_text_font_size = '16pt'
fig_all.axis.axis_label_text_font_style = 'normal'
fig_all.axis.major_label_text_font = 'helvetica'
fig_all.axis.major_label_text_font_size = '10pt'
fig_all.axis.major_label_text_font_style = 'normal'

##################
#style the title#
################
fig_one.title.text='Preview Plot'
fig_one.title.text_color=(0.7,0.7,0.7)
fig_one.title.text_font='helvetica'
fig_one.title.text_font_size='14pt'
fig_one.title.align='right'

fig_all.title.text='Overview Plot'
fig_all.title.text_color=(0.7,0.7,0.7)
fig_all.title.text_font='helvetica'
fig_all.title.text_font_size='20pt'
fig_all.title.align='right'

##########################
#create all plot widgets#
########################
#create data dropdown
options=[column for column in columns]
select_xdata = Select(title='x-data: ', options=options, value=columns[0])
select_ydata = Select(title='y-data: ', options=options, value=columns[1])
select_xdata.on_change('value', update_plot)
select_ydata.on_change('value', update_plot)

#create marker dropdown
menu = [('None', 'none')]
menu.extend((rn.capitalize(), rn) for rn in renderers if rn!='line')
dropdown_marker = Dropdown(label=label_marker(__marker), menu=menu, value=__marker)
dropdown_marker.on_change('value', update_plot)

#create line dropdown
menu = [('None', 'none'), ('Solid', 'solid'),('Dashed', 'dashed'), ('Dotted', 'dotted')]
dropdown_linedash = Dropdown(label=label_linedash(__linedash), menu=menu, value=__linedash)
dropdown_linedash.on_change('value', update_plot)

#slide to adjust line_alpha
slider_linealpha = Slider(start=0, end=1, value=0.6, step=0.1, title='Line transparency')
slider_linealpha.on_change('value', update_plot)

#slide to adjust fill_alpha
slider_fillalpha = Slider(start=0, end=1, value=0.2, step=0.1, title='Marker transparency')
slider_fillalpha.on_change('value', update_plot)

#create linecolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_linecolor = Dropdown(label=label_linecolor(__linecolor), menu=menu, value=__linecolor)
dropdown_linecolor.on_change('value', update_plot)

#create fillcolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_fillcolor = Dropdown(label=label_fillcolor(__fillcolor), menu=menu, value=__fillcolor)
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

#create add plot button
button_add = Button(label="Add to overview", button_type='success')
button_add.on_click(add_plot)

user_labels=False
#create textinput for xlabel
text_xlabel=TextInput(value='', title='x-label: ')
text_xlabel.on_change('value',change_label)

#create textinput for ylabel
text_ylabel=TextInput(value='', title='y-label: ')
text_ylabel.on_change('value',change_label)

###########################################################################################################################################
###########################################################fit tab#########################################################################
###########################################################################################################################################
################
#create figure#
##############
fig_fit = figure(toolbar_location='right', toolbar_sticky=False, tools=[PanTool(), BoxZoomTool(), WheelZoomTool(), BoxSelectTool(), TapTool(), ResetTool(), SaveTool()],output_backend='webgl')
fig_fit.plot_width = 800
fig_fit.plot_height = 600
fig_fit.toolbar.logo = None

#############
#style axis#
###########
fig_fit.axis.minor_tick_line_color='black'
fig_fit.axis.minor_tick_in=-6
fig_fit.xaxis.axis_label=columns[0]
fig_fit.yaxis.axis_label=columns[1]
fig_fit.axis.axis_label_text_color=(0.7,0.7,0.7)
fig_fit.axis.major_label_text_color=(0.7,0.7,0.7)
fig_fit.axis.axis_label_text_font = 'helvetica'
fig_fit.xaxis.axis_label_text_font_size = '12pt'
fig_fit.yaxis.axis_label_text_font_size = '12pt'
fig_fit.axis.axis_label_text_font_style = 'normal'
fig_fit.axis.major_label_text_font = 'helvetica'
fig_fit.axis.major_label_text_font_size = '10pt'
fig_fit.axis.major_label_text_font_style = 'normal'

############################################################################
#create all selectable renderers and set the circle and line renderer true#
##########################################################################
#model data
renderers_model_fit = {rn: getattr(fig_fit, rn)(x='x', y='y', source=source_fit,
                                   **extra, visible=False)
             for rn, extra in [('line', dict(line_width=__linewidth, line_color=__linecolor, line_alpha=__linealpha, line_dash=dict_linedash[__linedash])),
                               ('circle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('diamond', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('square', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('triangle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('asterisk', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('cross', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('x', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash]))]}
renderers_model_fit[__marker].visible=True
if __linedash=='none':
    renderers_model_fit['line'].visible=False
else:
    renderers_model_fit['line'].visible=True

#real data
renderers_data_fit = {rn: getattr(fig_fit, rn)(x='x', y='y', source=source_plot,
                                   **extra, visible=False)
             for rn, extra in [('line', dict(line_width=__linewidth, line_color=__linecolor, line_alpha=__linealpha, line_dash=dict_linedash[__linedash])),
                               ('circle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('diamond', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('square', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('triangle', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('asterisk', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('cross', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash])),
                               ('x', dict(size=__size, line_width=__linewidth, line_color=__linecolor, fill_color=__fillcolor, line_alpha=__linealpha, fill_alpha=__fillalpha, line_dash=dict_linedash[__linedash]))]}
renderers_data_fit[__marker].visible=True
if __linedash=='none':
    renderers_data_fit['line'].visible=False
else:
    renderers_data_fit['line'].visible=True
    
#########################
#create all fit widgets#
#######################

#create line dropdown
menu = [('None', 'none'), ('Solid', 'solid'),('Dashed', 'dashed'), ('Dotted', 'dotted')]
dropdown_linedash_fit = Dropdown(label=label_linedash(__linedash), menu=menu, value=__linedash)
dropdown_linedash_fit.on_change('value', update_fit)

#slide to adjust line_alpha
slider_linealpha_fit = Slider(start=0, end=1, value=0.6, step=0.1, title='Line transparency')
slider_linealpha_fit.on_change('value', update_fit)

#create linecolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_linecolor_fit = Dropdown(label=label_linecolor(__linecolor), menu=menu, value=__linecolor)
dropdown_linecolor_fit.on_change('value', update_fit)

#slide to adjust line width
slider_linewidth_fit=Slider(start=0, end=10, value=__linewidth, step=1, title='Line width')
slider_linewidth_fit.on_change('value', update_fit)

#create marker dropdown
menu = [('None', 'none')]
menu.extend((rn.capitalize(), rn) for rn in renderers_model_fit if rn!='line')
dropdown_marker_fit = Dropdown(label=label_marker(__marker), menu=menu, value=__marker)
dropdown_marker_fit.on_change('value', update_fit)

#slide to adjust fill_alpha
slider_fillalpha_fit = Slider(start=0, end=1, value=0.2, step=0.1, title='Marker transparency')
slider_fillalpha_fit.on_change('value', update_fit)

#create fillcolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_fillcolor_fit = Dropdown(label=label_fillcolor(__fillcolor), menu=menu, value=__fillcolor)
dropdown_fillcolor_fit.on_change('value', update_fit)

#slide to adjust marker size
slider_size_fit=Slider(start=0, end=30, value=__size, step=1, title='Marker size')
slider_size_fit.on_change('value', update_fit)

##create save button
#button_save_fit = Button(label="Save settings", button_type="success")
#button_save_fit.on_click(save_fit_settings)
#
##create reset button
#button_reset_fit = Button(label="Reset settings", button_type="danger")
#button_reset_fit.on_click(reset_fit_settings)
    
#create textinput for fit function
text_fit=TextInput(value='a*x**4+b*x**3+c*x**2+d*x+e', title='Fit function (Parameter a-e): ')
text_fit.on_change('value',fit_data)

###########################################################################################################################################
###########################################################table tab#######################################################################
###########################################################################################################################################

#create editable table widget
table_columns = [TableColumn(field=column, title=column) for column in columns]
table = DataTable(source=source_table, columns=table_columns, editable=True, width=1200, height=800)

###########################################################################################################################################
###########################################################create layouts##################################################################
###########################################################################################################################################

#create tab layouts
layout_plot=layout([[[[button_reset, button_save], [dropdown_linedash, dropdown_marker], [slider_linealpha, slider_fillalpha], [dropdown_linecolor, dropdown_fillcolor], [slider_linewidth, slider_size], [select_xdata, select_ydata], fig_one, button_add], [fig_all, [text_xlabel, text_ylabel]]]])
layout_fit=layout([[[text_fit, [dropdown_linedash_fit, dropdown_marker_fit], [slider_linealpha_fit, slider_fillalpha_fit], [dropdown_linecolor_fit, dropdown_fillcolor_fit], [slider_linewidth_fit, slider_size_fit]], [fig_fit]]])
layout_table=layout([table])

#create panels
tab_plot=Panel(child=layout_plot, title='Plot')
tab_fit=Panel(child=layout_fit, title='Fit')
tab_table=Panel(child=layout_table, title='Table')

#create the tabs from panels
tabs=Tabs(tabs=[tab_plot, tab_fit, tab_table])

############################################
#create the layout with figure and widgets#
##########################################
layout=layout(tabs)

##############
#stream data#
############
curdoc().title='Easy Plot'
curdoc().add_root(layout)
curdoc().add_periodic_callback(update,1000)