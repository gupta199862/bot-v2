import json
import math
import numpy as np
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
import numpy as np
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, Slider, Select
from bokeh.plotting import curdoc, figure
from bokeh.driving import count


BUFSIZE = 200

source = ColumnDataSource(dict(
    time=[], cp0=[] ,cp1=[] ,cp2=[] , p2m0=[] , p2m1=[] , p2m2=[]
))



def get_plot_data():
    json_data = []
    with open("USDT-BTC_Market_predictions.txt") as file :
    	for line in file:
        	json_data=json.loads(line)
        
    EVAL_mat_array=np.array(json_data)        
        
    curnt_price  = EVAL_mat_array[:,0:3]
    predict2min  = EVAL_mat_array[:,3:6]
    #predict10min = EVAL_mat_array[:,6:9]
    #predict30min = EVAL_mat_array[:,9:12]

    # set up some data
    cp0 = curnt_price[:,0]
    cp1 = curnt_price[:,1]
    cp2 = curnt_price[:,2]
    #cp2 =  cp2[5:]

    p2m0 = predict2min[:,0]
    p2m1 = predict2min[:,1]
    p2m2 = predict2min[:,2]
    #p2m0 = p2m0[1:]
    #p2m1 = p2m1[1:]
    #p2m2 = p2m2[1:]

    #p10m0 = predict10min[:,0]
    #p10m1 = predict10min[:,1]
    #p10m2 = predict10min[:,2]
    #p10m0 = p10m0[5:]
    #p10m1 = p10m1[5:]
    #p10m2 = p10m2[5:]

    #p30m0 = predict30min[:,0]
    #p30m1 = predict30min[:,1]
    #p30m2 = predict30min[:,2]
    #p30m0 = p30m0[15:]
    #p30m1 = p30m1[15:]
    #p30m2 = p30m2[15:]


    #yc = range(200)
    #yp = range(0,200,1)
    return cp0,p2m0,cp1,p2m1,cp2,p2m2

     
#create a new plot with figure

p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_axis_type=None, y_axis_location="right")
p.x_range.follow = "end"
p.x_range.follow_interval = 100
p.x_range.range_padding = 0#add both a line and circles on the same plot
#p.line(y4, x4, line_width=2,line_color="firebrick")
p.line(y='time' ,x= 'cp2', line_width=1 ,source=source)
p.line(y='time' ,x= 'p10m2', line_width=1 , line_color="red" , source=source)
#p.circle(y,cp2, size=2, line_color="red", fill_color="orange", fill_alpha=0.5)
#p.circle(y2,p2m2, size=2, line_color="navy", fill_color="orange", fill_alpha=0.5)
#p.line(y4, x4, line_width=2,line_color="orange")
#p.circle(y3,x3, size=10, line_color="navy", fill_color="orange", fill_alpha=0.5)
#p.circle(x, z, fill_color="white", size=8)
#show(p) # show the results





@count()
def update(t):
    cp0,p2m0,cp1,p2m1,cp2,p2m2= get_plot_data()

    new_data = dict(
        time=[t],
        cp0=[cp0],
        p2m0=[p2m0],
        cp1=[cp1],
        p2m1=[p2m1],
        cp2=[cp2],
        p2m2=[p2m2]
    )
    source.stream(new_data, 300)

curdoc().add_periodic_callback(update, 1000*120)
curdoc().title = "prediction"




