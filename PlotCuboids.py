# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 16:42:07 2018

@author: lud
"""
import matplotlib
#import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import tkinter as Tk
    
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
from argparse import ArgumentParser
import os


    
    
def cuboid_data2(o, size=(1,1,1)):
    X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
         [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
         [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
         [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
         [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
         [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
    X = np.array(X).astype(float)
    for i in range(3):
        X[:,:,i] *= size[i]
    X += np.array(o)
    return X

def plotCubeAt2(positions,sizes=None,colors=None, **kwargs):
    if not isinstance(colors,(list,np.ndarray)): colors=["C0"]*len(positions)
    if not isinstance(sizes,(list,np.ndarray)): sizes=[(1,1,1)]*len(positions)
    g = []
    for p,s,c in zip(positions,sizes,colors):
        g.append( cuboid_data2(p, size=s) )
    return Poly3DCollection(np.concatenate(g),  
                            facecolors=np.repeat(colors,6), **kwargs)

    
def main(path, width, depth, height):
    #get all data files
    source_files = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            source_files.append(os.path.join(path, file))
    
    #get data
    def getData(df):
        if len(df.columns < 7):
            df['6'] = 0
        sizes = [tuple(x) for x in df.iloc[:,[1,2,3]].values]
        positions = [tuple(x) for x in df.iloc[:,[4,5,6]].values]
        colors = ["limegreen"]*df.shape[0]
        pc = plotCubeAt2(positions,sizes,colors=colors, edgecolor="k", linewidth = 0.4)    
        return pc
    
    #create figure
    
    fig = Figure()
    root = Tk.Tk()
    root.wm_title("Plot boxes")
    canvas = FigureCanvasTkAgg(fig, master=root)
    ax = fig.add_subplot(111,projection='3d')
    ax.set_aspect('equal')
    ax.set_xlim([0,width])
    ax.set_ylim([0,depth])
    ax.set_zlim([0,height]) 
    
    if len(source_files) > 0:
        box_data = pd.read_csv(source_files[0], header = None)
    else:
        box_data = pd.DataFrame(np.full((1,6),0,dtype = int))
    ax.add_collection3d(getData(box_data))    
    

    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)    
    
    def refresh(df):
        ax.collections.clear()
        ax.add_collection(getData(df))
        canvas.draw()
    
    def ok():
        newfile = tkvar.get()        
        box_data = pd.read_csv(newfile, header = None)       
        refresh(box_data)
    
    def option_changed(*args):
        newfile = tkvar.get()
        box_data = pd.read_csv(newfile, header = None)
        refresh(box_data)
    
    # Create a Tkinter variable
    tkvar = Tk.StringVar(root)
    if len(source_files) > 0:
        tkvar.set(source_files[0])
    else:
        tkvar.set('No file')
    tkvar.trace("w", option_changed)
    
    popupMenu = Tk.OptionMenu(root, tkvar, '', *source_files)
    popupMenu.pack(side=Tk.TOP)
    
    
    
        
    def on_key_event(event):
        print('you pressed %s' % event.key)
        key_press_handler(event, canvas, toolbar)
    
    canvas.mpl_connect('key_press_event', on_key_event)
    
        
    def _quit():
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    
    button = Tk.Button(master=root, text='Quit', command=_quit)
    button.pack(side=Tk.BOTTOM)

    root.mainloop()

# main('E:\\Projects\\BinPacking\\test',800,1200,2055)
if __name__ == "__main__":    
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", dest="layer_data_path",
                        help="find data from path", metavar="PATH")
    parser.add_argument("-w", "--width", dest="width", type = int, default=800,
                        help="plane width, default 800")
    parser.add_argument("-d", "--depth", dest="depth", type = int, default=1200,
                        help="plane depth, default 1200")
    parser.add_argument("-hei", "--height", dest="height", type = int, default=2055,
                        help="bin height, default 2055")
    args = parser.parse_args()
    main(args.layer_data_path, args.width, args.depth, args.height)