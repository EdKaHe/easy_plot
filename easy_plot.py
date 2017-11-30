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
filepath='171124_Omicron_Luxx_75mW.csv'
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
settings_plot=pd.read_json(r'./settings_plot.JSON', typ='series')[0]
settings_fit=pd.read_json(r'./settings_fit.JSON', typ='series')[0]

#set all initial values
dict_linedash=dict(none=[], solid=[1],dashed=[8,8],dotted=[2,6])#required to convert string to array
__marker_plot=settings_plot['marker']
__linedash_plot=settings_plot['linedash']
__linealpha_plot=float(settings_plot['linealpha'])
__linecolor_plot=settings_plot['linecolor']
__linewidth_plot=int(settings_plot['linewidth'])
__fillalpha_plot=float(settings_plot['fillalpha'])
__fillcolor_plot=settings_plot['fillcolor']
__size_plot=int(settings_plot['size'])
__marker_fit=settings_fit['marker']
__linedash_fit=settings_fit['linedash']
__linealpha_fit=float(settings_fit['linealpha'])
__linecolor_fit=settings_fit['linecolor']
__linewidth_fit=int(settings_fit['linewidth'])
__fillalpha_fit=float(settings_fit['fillalpha'])
__fillcolor_fit=settings_fit['fillcolor']
__size_fit=int(settings_fit['size'])

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
    #make the unfixed fit invisible
    for renderer_name, renderer in renderers_plot_fit.items():
        renderer.visible=False
    
    #change x and y data
    fig_plot.xaxis.axis_label=select_xdata.value
    fig_plot.yaxis.axis_label=select_ydata.value
    source_plot.data=dict(x=source_table.data[select_xdata.value],
                     y=source_table.data[select_ydata.value])
    
    #change marker type and properties
    dropdown_marker.label=label_marker(dropdown_marker.value)
    dropdown_fillcolor.label=label_fillcolor(dropdown_fillcolor.value)
    dropdown_linecolor.label=label_linecolor(dropdown_linecolor.value)
    dropdown_linedash.label=label_linedash(dropdown_linedash.value)
    for renderer_name, renderer in renderers_plot.items():
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
        renderers_plot['line'].visible=False
    else:
        renderers_plot['line'].visible=True

########################
#change fit as desired#
#######################
def update_fit(attr, old, new):  
    #change marker type and properties
    dropdown_marker_fit.label=label_marker(dropdown_marker_fit.value)
    dropdown_fillcolor_fit.label=label_fillcolor(dropdown_fillcolor_fit.value)
    dropdown_linecolor_fit.label=label_linecolor(dropdown_linecolor_fit.value)
    dropdown_linedash_fit.label=label_linedash(dropdown_linedash_fit.value)
    for renderer_name, renderer in renderers_fit.items():
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
        renderers_fit['line'].visible=False
    else:
        renderers_fit['line'].visible=True
        
############################
#save the current settings#
##########################
def save_plot_settings():
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
    df_settings.to_json(r'./settings_plot.JSON',orient='records')
    
def save_fit_settings():
    settings=dict(marker=[dropdown_marker_fit.value],
                  linedash=[dropdown_linedash_fit.value],
                  linecolor=[dropdown_linecolor_fit.value],
                  linealpha=[slider_linealpha_fit.value],
                  linewidth=[slider_linewidth_fit.value],
                  fillcolor=[dropdown_fillcolor_fit.value],
                  fillalpha=[slider_fillalpha_fit.value],
                  size=[slider_size_fit.value]
            )
    df_settings=pd.DataFrame(settings)
    df_settings.to_json(r'./settings_fit.JSON',orient='records')
      
#############################################################
#reset the settings to the initial settings of this session#
###########################################################
def reset_plot_settings():
    #reset glyph properties
    for renderer_name, renderer in renderers_plot.items():
        renderer.visible=False
        renderer.glyph.line_alpha=__linealpha_plot
        renderer.glyph.line_width=__linewidth_plot
        renderer.glyph.line_color=__linecolor_plot
        renderer.glyph.line_dash=dict_linedash[__linedash_plot]
        if renderer_name!='line':
            renderer.glyph.fill_alpha=__fillalpha_plot
            renderer.glyph.size=__size_plot
            renderer.glyph.fill_color=__fillcolor_plot
            
    if __marker_plot!='none':
        renderers_plot[__marker_plot].visible=True
    if __linedash_plot=='none':
        renderers_plot['line'].visible=False        
    else:
        renderers_plot['line'].visible=True
        
    #reset widget properies
    slider_fillalpha.value=__fillalpha_plot
    slider_linealpha.value=__linealpha_plot
    slider_linewidth.value=__linewidth_plot
    slider_size.value=__size_plot
    dropdown_fillcolor.value=__fillcolor_plot
    dropdown_linecolor.value=__linecolor_plot
    dropdown_marker.value=__marker_plot
    dropdown_linedash.value=__linedash_plot
    
def reset_fit_settings():
    #reset glyph properties
    for renderer_name, renderer in renderers_fit.items():
        renderer.visible=False
        renderer.glyph.line_alpha=__linealpha_fit
        renderer.glyph.line_width=__linewidth_fit
        renderer.glyph.line_color=__linecolor_fit
        renderer.glyph.line_dash=dict_linedash[__linedash_fit]
        if renderer_name!='line':
            renderer.glyph.fill_alpha=__fillalpha_fit
            renderer.glyph.size=__size_fit
            renderer.glyph.fill_color=__fillcolor_fit
    if __marker_fit!='none':
        renderers_fit[__marker_fit].visible=True
    if __linedash_fit=='none':
        renderers_fit['line'].visible=False        
    else:
        renderers_fit['line'].visible=True
        
    #reset widget properies
    slider_fillalpha_fit.value=__fillalpha_fit
    slider_linealpha_fit.value=__linealpha_fit
    slider_linewidth_fit.value=__linewidth_fit
    slider_size_fit.value=__size_fit
    dropdown_fillcolor_fit.value=__fillcolor_fit
    dropdown_linecolor_fit.value=__linecolor_fit
    dropdown_marker_fit.value=__marker_fit
    dropdown_linedash_fit.value=__linedash_fit

#create function that adds data from left plot to the right permanently 

def fix_plot():
    #make the unfixed plot invisible
    for renderer_name, renderer in renderers_plot.items():
        renderer.visible=False
    
    #add marker to plot
    new_data_plot=source_plot.data
    global plot_count
    try:
        plot_count+=1
    except NameError:
        plot_count=0
    legend_plot='Plot {}'.format(plot_count)
    if dropdown_marker.value!='none':
        renderer_fixed=getattr(fig_plot, dropdown_marker.value)(x=new_data_plot['x'], y=new_data_plot['y'], legend=legend_plot, muted_color=dropdown_fillcolor.value, muted_alpha=slider_fillalpha.value*0.1)
        #change marker properties
        renderer_fixed.glyph.line_width=slider_linewidth.value
        renderer_fixed.glyph.line_color=dropdown_linecolor.value
        renderer_fixed.glyph.line_alpha=slider_linealpha.value
        renderer_fixed.glyph.size=slider_size.value
        renderer_fixed.glyph.fill_color=dropdown_fillcolor.value
        renderer_fixed.glyph.fill_alpha=slider_fillalpha.value
    #change line properties if line is visible
    if dropdown_linedash.value!='none':
        renderer_fixed=getattr(fig_plot, 'line')(x=new_data_plot['x'], y=new_data_plot['y'], legend=legend_plot, muted_color=dropdown_linecolor.value, muted_alpha=slider_linealpha.value*0.1)
        renderer_fixed.glyph.line_width=slider_linewidth.value
        renderer_fixed.glyph.line_color=dropdown_linecolor.value
        renderer_fixed.glyph.line_alpha=slider_linealpha.value
        renderer_fixed.glyph.line_dash=dict_linedash[dropdown_linedash.value]
    
    #change axis labels
    fig_plot.xaxis.axis_label=select_xdata.value
    fig_plot.yaxis.axis_label=select_ydata.value
    
    #update texboxes only if user didn't create labels
    if not user_labels:
        text_xlabel.value=select_xdata.value
        text_ylabel.value=select_ydata.value
        
    fig_plot.legend.location = "top_left"
    fig_plot.legend.click_policy="mute"
    
def fix_fit():       
    #make the unfixed plot invisible
    for renderer_name, renderer in renderers_plot_fit.items():
        renderer.visible=False
    
    #fix fit
    new_data_fit=source_fit.data
    if dropdown_marker_fit.value!='none':
        renderer_fixed=getattr(fig_plot, dropdown_marker_fit.value)(x=new_data_fit['x'], y=new_data_fit['y'], muted_color=dropdown_fillcolor_fit.value, muted_alpha=slider_fillalpha_fit.value*0.1)
        #change marker properties
        renderer_fixed.glyph.line_width=slider_linewidth_fit.value
        renderer_fixed.glyph.line_color=dropdown_linecolor_fit.value
        renderer_fixed.glyph.line_alpha=slider_linealpha_fit.value
        renderer_fixed.glyph.size=slider_size_fit.value
        renderer_fixed.glyph.fill_color=dropdown_fillcolor_fit.value
        renderer_fixed.glyph.fill_alpha=slider_fillalpha_fit.value
    #change line properties if line is visible
    if dropdown_linedash_fit.value!='none':
        renderer_fixed=getattr(fig_plot, 'line')(x=new_data_fit['x'], y=new_data_fit['y'], muted_color=dropdown_linecolor_fit.value, muted_alpha=slider_linealpha_fit.value*0.1)
        renderer_fixed.glyph.line_width=slider_linewidth_fit.value
        renderer_fixed.glyph.line_color=dropdown_linecolor_fit.value
        renderer_fixed.glyph.line_alpha=slider_linealpha_fit.value
        renderer_fixed.glyph.line_dash=dict_linedash[dropdown_linedash_fit.value]

#create function that changes axis labels after user input
def change_label(attr, old, new):
    #set user input true so that it is not changed automatically anymore
    global user_labels
    user_labels=True
    
    #change the axis labels
    fig_plot.xaxis.axis_label=text_xlabel.value
    fig_plot.yaxis.axis_label=text_ylabel.value
    
#create function that fits data from function given as string
def fit_data():
    global parameter
    func=lambda x,a,b,c,d,e: eval(text_fit.value)
    
    #get indices of selected points
    indices=source_plot.selected['1d']['indices']
    indices.sort()
    if indices:
        x=source_plot.data['x'][indices]
        y=source_plot.data['y'][indices]
    else:
        x=source_plot.data['x']
        y=source_plot.data['y']
        
    try:
        parameter,_=optimize.curve_fit(func, x, y)
    except RuntimeError:
        for i in range(5):
            button_fit.label='Parameter not found!'
            button_fit.button_type='danger'
            sleep(0.2)
            button_fit.button_type='default'
            sleep(0.2)
        button_fit.label='Fit data'
        return
    
    #print parameter to text output
    text_parameter.value=str(parameter)
    
    y=func(x, *parameter)
    source_fit.data=dict(x=x,y=y)    
    
    #update glyph properties
    dropdown_marker_fit.label=label_marker(dropdown_marker_fit.value)
    dropdown_fillcolor_fit.label=label_fillcolor(dropdown_fillcolor_fit.value)
    dropdown_linecolor_fit.label=label_linecolor(dropdown_linecolor_fit.value)
    dropdown_linedash_fit.label=label_linedash(dropdown_linedash_fit.value)
    for renderer_name, renderer in renderers_plot_fit.items():
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
        renderers_plot_fit['line'].visible=False
    else:
        renderers_plot_fit['line'].visible=True
    
    #make fit visible
    if dropdown_marker_fit.value!='none':
        renderers_plot_fit[dropdown_marker_fit.value].visible=True
    if dropdown_linedash_fit.value=='none':
        renderers_plot_fit['line'].visible=False
    else:
        renderers_plot_fit['line'].visible=True
    
###########################################################################################################################################
###########################################################plot tab########################################################################
###########################################################################################################################################

################
#create figure#
##############
fig_plot = figure(toolbar_location='right', toolbar_sticky=False, tools=[PanTool(), BoxZoomTool(), WheelZoomTool(), BoxSelectTool(), TapTool(), ResetTool(), SaveTool()],output_backend='webgl')
fig_plot.plot_width = 800
fig_plot.plot_height = 600
fig_plot.toolbar.logo = None

############################################################################
#create all selectable renderers and set the circle and line renderer true#
##########################################################################
renderers_plot = {rn: getattr(fig_plot, rn)(x='x', y='y', source=source_plot,
                                   **extra, visible=False)
             for rn, extra in [('line', dict(line_width=__linewidth_plot, line_color=__linecolor_plot, line_alpha=__linealpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('circle', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('diamond', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('square', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('triangle', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('asterisk', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('cross', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot])),
                               ('x', dict(size=__size_plot, line_width=__linewidth_plot, line_color=__linecolor_plot, fill_color=__fillcolor_plot, line_alpha=__linealpha_plot, fill_alpha=__fillalpha_plot, line_dash=dict_linedash[__linedash_plot]))]}
if __marker_plot!='none':
    renderers_plot[__marker_plot].visible=True
if __linedash_plot=='none':
    renderers_plot['line'].visible=False
else:
    renderers_plot['line'].visible=True
    
renderers_plot_fit = {rn: getattr(fig_plot, rn)(x='x', y='y', source=source_fit,
                                   **extra, visible=False)
             for rn, extra in [('line', dict(line_width=__linewidth_fit, line_color=__linecolor_fit, line_alpha=__linealpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('circle', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('diamond', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('square', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('triangle', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('asterisk', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('cross', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('x', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit]))]}

#############
#style axis#
###########
fig_plot.axis.minor_tick_line_color='black'
fig_plot.axis.minor_tick_in=-6
fig_plot.xaxis.axis_label=columns[0]
fig_plot.yaxis.axis_label=columns[1]
fig_plot.axis.axis_label_text_color=(0.7,0.7,0.7)
fig_plot.axis.major_label_text_color=(0.7,0.7,0.7)
fig_plot.axis.axis_label_text_font = 'helvetica'
fig_plot.xaxis.axis_label_text_font_size = '12pt'
fig_plot.yaxis.axis_label_text_font_size = '12pt'
fig_plot.axis.axis_label_text_font_style = 'normal'
fig_plot.axis.major_label_text_font = 'helvetica'
fig_plot.axis.major_label_text_font_size = '10pt'
fig_plot.axis.major_label_text_font_style = 'normal'

##################
#style the title#
################
fig_plot.title.text='Overview Plot'
fig_plot.title.text_color=(0.7,0.7,0.7)
fig_plot.title.text_font='helvetica'
fig_plot.title.text_font_size='14pt'
fig_plot.title.align='right'

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
menu.extend((rn.capitalize(), rn) for rn in renderers_plot if rn!='line')
dropdown_marker = Dropdown(label=label_marker(__marker_plot), menu=menu, value=__marker_plot)
dropdown_marker.on_change('value', update_plot)

#create line dropdown
menu = [('None', 'none'), ('Solid', 'solid'),('Dashed', 'dashed'), ('Dotted', 'dotted')]
dropdown_linedash = Dropdown(label=label_linedash(__linedash_plot), menu=menu, value=__linedash_plot)
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
dropdown_linecolor = Dropdown(label=label_linecolor(__linecolor_plot), menu=menu, value=__linecolor_plot)
dropdown_linecolor.on_change('value', update_plot)

#create fillcolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_fillcolor = Dropdown(label=label_fillcolor(__fillcolor_plot), menu=menu, value=__fillcolor_plot)
dropdown_fillcolor.on_change('value', update_plot)

#slide to adjust marker size
slider_size=Slider(start=0, end=30, value=__size_plot, step=1, title='Marker size')
slider_size.on_change('value', update_plot)

#slide to adjust line width
slider_linewidth=Slider(start=0, end=10, value=__linewidth_plot, step=1, title='Line width')
slider_linewidth.on_change('value', update_plot)

#create save button
button_save_plot = Button(label="Save plot settings", button_type="success")
button_save_plot.on_click(save_plot_settings)

#create reset button
button_reset_plot = Button(label="Reset plot settings", button_type="danger")
button_reset_plot.on_click(reset_plot_settings)

#create fix plot button
button_fix_plot = Button(label="Fix plot")
button_fix_plot.on_click(fix_plot)

#create fix fit button
button_fix_fit = Button(label="Fix fit")
button_fix_fit.on_click(fix_fit)

#create fix plot button
button_fit = Button(label="Fit data")
button_fit.on_click(fit_data)

user_labels=False
#create textinput for xlabel
text_xlabel=TextInput(value=select_xdata.value, title='x-label: ')
text_xlabel.on_change('value',change_label)

#create textinput for ylabel
text_ylabel=TextInput(value=select_ydata.value, title='y-label: ')
text_ylabel.on_change('value',change_label)

###########################################################################################################################################
###########################################################fit tab#########################################################################
###########################################################################################################################################
################
#create figure#
##############
fig_fit = figure(toolbar_location='right', toolbar_sticky=False, tools=[PanTool(), BoxZoomTool(), WheelZoomTool(), ResetTool()],output_backend='webgl')
fig_fit.plot_width = 800
fig_fit.plot_height = 600
fig_fit.toolbar.logo = None

#############
#style title#
###########
fig_fit.title.text='Style Preview'
fig_fit.title.text_color=(0.7,0.7,0.7)
fig_fit.title.text_font='helvetica'
fig_fit.title.text_font_size='14pt'
fig_fit.title.align='right'

#############
#style axis#
###########
fig_fit.axis.visible=False

############################################################################
#create all selectable renderers and set the circle and line renderer true#
##########################################################################
renderers_fit = {rn: getattr(fig_fit, rn)(x=[0, 1], y=[1, 1],
                                   **extra, visible=False)
             for rn, extra in [('line', dict(line_width=__linewidth_fit, line_color=__linecolor_fit, line_alpha=__linealpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('circle', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('diamond', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('square', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('triangle', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('asterisk', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('cross', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit])),
                               ('x', dict(size=__size_fit, line_width=__linewidth_fit, line_color=__linecolor_fit, fill_color=__fillcolor_fit, line_alpha=__linealpha_fit, fill_alpha=__fillalpha_fit, line_dash=dict_linedash[__linedash_fit]))]}
if __marker_fit!='none':
    renderers_fit[__marker_fit].visible=True
if __linedash_fit=='none':
    renderers_fit['line'].visible=False
else:
    renderers_fit['line'].visible=True
    
#########################
#create all fit widgets#
#######################

#create line dropdown
menu = [('None', 'none'), ('Solid', 'solid'),('Dashed', 'dashed'), ('Dotted', 'dotted')]
dropdown_linedash_fit = Dropdown(label=label_linedash(__linedash_fit), menu=menu, value=__linedash_fit)
dropdown_linedash_fit.on_change('value', update_fit)

#slide to adjust line_alpha
slider_linealpha_fit = Slider(start=0, end=1, value=0.6, step=0.1, title='Line transparency')
slider_linealpha_fit.on_change('value', update_fit)

#create linecolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_linecolor_fit = Dropdown(label=label_linecolor(__linecolor_fit), menu=menu, value=__linecolor_fit)
dropdown_linecolor_fit.on_change('value', update_fit)

#slide to adjust line width
slider_linewidth_fit=Slider(start=0, end=10, value=__linewidth_fit, step=1, title='Line width')
slider_linewidth_fit.on_change('value', update_fit)

#create marker dropdown
menu = [('None', 'none')]
menu.extend((rn.capitalize(), rn) for rn in renderers_fit if rn!='line')
dropdown_marker_fit = Dropdown(label=label_marker(__marker_fit), menu=menu, value=__marker_fit)
dropdown_marker_fit.on_change('value', update_fit)

#slide to adjust fill_alpha
slider_fillalpha_fit = Slider(start=0, end=1, value=0.2, step=0.1, title='Marker transparency')
slider_fillalpha_fit.on_change('value', update_fit)

#create fillcolor dropdown
colors=['black', 'white', 'gray', 'whitesmoke', 'red', 'firebrick', 'pink', 'orange', 'yellow', 'green', 'olive', 'blue', 'navy']
menu=[(color.capitalize(), color) for color in colors]
dropdown_fillcolor_fit = Dropdown(label=label_fillcolor(__fillcolor_fit), menu=menu, value=__fillcolor_fit)
dropdown_fillcolor_fit.on_change('value', update_fit)

#slide to adjust marker size
slider_size_fit=Slider(start=0, end=30, value=__size_fit, step=1, title='Marker size')
slider_size_fit.on_change('value', update_fit)

#create save button
button_save_fit = Button(label="Save settings", button_type="success")
button_save_fit.on_click(save_fit_settings)

#create reset button
button_reset_fit = Button(label="Reset settings", button_type="danger")
button_reset_fit.on_click(reset_fit_settings)
    
#create text box for fit function
text_fit=TextInput(value='a*x**4+b*x**3+c*x**2+d*x+e', title='Fit function (Parameter a-e): ')

#create text box for parameter
text_parameter=TextInput(value='', title='Parameter output (a-e)')

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
layout_plot=layout([[[[select_xdata, select_ydata], [dropdown_linedash, dropdown_marker], [dropdown_linecolor, dropdown_fillcolor], [slider_linewidth, slider_size], [slider_linealpha, slider_fillalpha], [text_xlabel, text_ylabel], button_fix_plot, [button_reset_plot, button_save_plot]], [fig_plot, [button_fit, button_fix_fit]]]])
layout_fit=layout([[[[text_fit, text_parameter], [dropdown_linedash_fit, dropdown_marker_fit], [dropdown_linecolor_fit, dropdown_fillcolor_fit], [slider_linewidth_fit, slider_size_fit], [slider_linealpha_fit, slider_fillalpha_fit], [button_reset_fit, button_save_fit]], [fig_fit]]])
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