'''
module to quickly plot 3D data in 2D slices.
'''
import sys
pyver = sys.version[0]
if pyver is "2":
    import Tkinter as Tk
    import FileDialog
elif pyver is "3":
    import tkinter as Tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.colors import LogNorm
from matplotlib.pyplot import colormaps
import numpy as np
import numpy.ma as ma

class POPUP(Tk.Menu):
    '''
    class representing the color map menu
    '''
    def __init__(self, ms, iscalling):
        Tk.Menu.__init__(self, ms, tearoff=0)
        slist=colormaps()[::4]
        self.iscalling = iscalling
        for ii, mmap in enumerate(slist):
            self.add_command(label=mmap,
                             command=lambda mmap=mmap: self.setself(mmap))

    def setself(self, mymap):
        '''
        function to set the colormap specfied by the string mymap as the
        colormap of the figure associated to the calling frame.
        '''
        self.iscalling.mycmap = mymap
        self.iscalling.updatefig()


class Fieldframe(Tk.Frame):
    '''
    class for the frame containing the field information (upper part of figure)
    '''
    def __init__(self, ms, mst):
        Tk.Frame.__init__(self, ms)
        self.mst = mst
        self.currentnr = Tk.Label(self, text="current field number: %.3d"
                                  % self.mst.fieldnr)
        self.currentnr.pack(side="left")
        button0 = Tk.Button(self, text="previous", command=self.mst.mone)
        button0.pack(side="left")
        button2 = Tk.Button(self, text="next", command=self.mst.pone)
        button2.pack(side="left")
        fieldtxt = Tk.Label(self, text="set field nr to: ")
        fieldtxt.pack(side="left")
        self.fldrn = Tk.Entry(self, width=5)
        self.fldrn.pack(side="left")
        self.fldrn.focus_set()
        button1 = Tk.Button(self, text="map field", command=self.mst.button1)
        button1.pack(side="left")


class DATA2D(object):
    '''
    class to hold a 2D sub-data array of the supplied data and link it with
    the appropriate figure frame
    '''
    def __init__(self, mindata, pfr):
        self.pfr = pfr  # this is the plot frame
        self.data = mindata
        self.frozen = False
        self.mycmap = "jet"
        self.getdata()
        pfr.canvas.mpl_connect('button_press_event', self.pick)

    def getdata(self):
        if not self.frozen:
            self.xmin = 0
            self.ymin = 0
            self.xmax = np.shape(self.data)[0]
            self.ymax = np.shape(self.data)[1]
            if isinstance(self.data, ma.core.MaskedArray):
                self.datamax = np.nanmax(np.array(self.data[~self.data.mask]))
                self.datamin = np.nanmin(np.array(self.data[~self.data.mask]))
            else:
                self.datamax = np.nanmax(np.array(self.data))
                self.datamin = np.nanmin(np.array(self.data))
            #print (type(self.data), self.data[~self.data.mask].min())
            #print (self.data.mask.sum())

    def makefig(self):
        self.im = self.pfr.a.imshow(
            self.data[self.xmin:self.xmax, self.ymin:self.ymax],
            cmap=self.mycmap, interpolation='none', vmin=self.datamin,
            vmax=self.datamax)
        self.cbar = self.pfr.f.colorbar(self.im)
        self.pfr.canvas.show()
        self.pfr.toolbar.update()
#        self.updatefig()

    def updatefig(self, from_slicing=False, plotlog=False ):
        mymin = self.datamin
        mymax = self.datamax
        # works with set_array together
        #self.im.set_data(self.data[self.xmin:self.xmax, self.ymin:self.ymax])
        if from_slicing:
            self.im.set_extent(  # for some reason, this seems to create problems.
        # june 2017. I still use it, but y-dimension flipped. 
        # seems ok i.e. 3rd and 4th argument swaped.
            [-0.5, self.im.get_size()[1]-0.5, self.im.get_size()[0]-0.5,-0.5])
        #self.im.set_data(self.data[self.xmin:self.xmax, self.ymin:self.ymax]) # should not use this?
        self.im.set_data(self.data)
        if plotlog:
            self.im.set_norm(LogNorm(mymin, mymax))
            self.cbar.update_bruteforce(self.im)
        else:
            self.im.set_norm(None)
            self.cbar.update_bruteforce(self.im)
        self.pfr.canvas.draw()
        self.cbar.set_array(self.data[self.xmin:self.xmax, self.ymin:self.ymax])  # works with set_data in z
        self.im.set_cmap(self.mycmap)
        
        #print self.ymax, self.xmax, self.data[0,0]
        #print self.pfr.a.get_xbound(), self.pfr.a.get_ybound()
        #print self.pfr.a.get_xticks()
        #print self.pfr.a.get_yticks()
        #print self.pfr.a.get_xticklabels()[0].get_label()
        #print "here"
        self.pfr.a.set_xlim(xmin=self.ymin-0.5, xmax=self.ymax-0.5)
        self.pfr.a.set_ylim(top=self.xmin-0.5, bottom=self.xmax-0.5)
        self.im.set_clim(vmin=mymin, vmax=mymax)
        self.im.changed()
        self.cbar.changed()
        self.cbar.update_normal(self.im)
        self.pfr.toolbar.update()
        self.pfr.canvas.draw()
        # print("x:", self.ymin-0.5, self.ymax-0.5)
        # print("y:", self.xmin-0.5, self.xmax-0.5)


    def pick(self, event):
        try:
            self.xdata = int(round(event.xdata))
        except:
            pass
        try:
            self.ydata = int(round(event.ydata))
        except:
            pass
        try:
            print ("xpos: ", self.xdata, "ypos: ", self.ydata, "data: ",)
            print (self.data[self.ydata, self.xdata])
        except:
        	print ("data extraction not possible")


class Coordinateframe(Tk.Frame):
    '''
    class to hold the frame with the current 2D view settings (lower part of
    figure)
    '''
    def __init__(self, ms, iscalling):
        Tk.Frame.__init__(self, ms)
        self.ms = ms
        self.logison = False
        self.coordx = Tk.Label(self, height=1, text="x min")
        self.coordx.grid(row=0, column=0, sticky="nsew")
        self.ex = Tk.Entry(self, width=5)
        self.ex.grid(column=1, row=0, sticky="nsew")
        self.ex.focus_set()
        coordy = Tk.Label(self, height=1, text="y min")
        coordy.grid(row=0, column=2, sticky="nsew")
        self.ey = Tk.Entry(self, width=5)
        self.ey.grid(column=3, row=0, sticky="nsew")
        self.ey.focus_set()
        coordx2 = Tk.Label(self, height=1, text="x max")
        coordx2.grid(row=1, column=0, sticky="nsew")
        self.ex2 = Tk.Entry(self, width=5)
        self.ex2.grid(column=1, row=1, sticky="nsew")
        self.ex2.focus_set()
        coordy2 = Tk.Label(self, height=1, text="y max")
        coordy2.grid(row=1, column=2, sticky="nsew")
        self.ey2 = Tk.Entry(self, width=5)
        self.ey2.grid(column=3, row=1, sticky="nsew")
        self.ey2.focus_set()
        coordz = Tk.Label(self, height=1, text="z min")
        coordz.grid(row=0, column=4, sticky="nsew")
        self.ez = Tk.Entry(self, width=5)
        self.ez.grid(column=5, row=0, sticky="nsew")
        self.ez.focus_set()
        coordz2 = Tk.Label(self, height=1, text="z max")
        coordz2.grid(row=1, column=4)
        self.ez2 = Tk.Entry(self, width=5)
        self.ez2.grid(column=5, row=1, sticky="nsew")
        self.ez2.focus_set()
        freezebutton = Tk.Button(self, text="freeze", width=5,
                                 command=self.freeze)
        freezebutton.grid(column=7, row=0, sticky="nsew")
        cmapbutton = Tk.Button(self, text="cmap", width=5)
        cmapbutton.grid(column=7, row=1, sticky="nsew")
        cmapbutton.bind("<Button-1>", self.cmapchoose)
        b = Tk.Button(self, text="set", width=5, command=self.setit)
        b.grid(column=6, row=0, sticky="nsew")
        c = Tk.Button(self, text="reset", width=5, command=self.reset)
        c.grid(column=6, row=1, sticky="nsew")
        self.logbutton = Tk.Button(self, text="log",width=5,command=self.plotlog)
        self.logbutton.grid(column=8,row=1,sticky="nsew")
        self.popup = POPUP(ms, iscalling)
        self.iscalling = iscalling
        # self.bind("<Configure>", self.on_size) # not needed?
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqheight()
        self.slicebuttonframe = Tk.Frame(self)
        self.slicebuttonframe.grid(column=9, row=0, sticky="nsew", rowspan=2)
        if ms.datap is not None:
            self.fieldtxt = Tk.Label(
                self.slicebuttonframe, text="slice along dimension: ")
            self.fieldtxt.pack(side="top")
            self.sliceslider = Tk.Scale(
                self.slicebuttonframe, from_=0, to=2,
                orient="horizontal", command=self.update)
            self.sliceslider.pack()
        for ii in list(range(9)):
            Tk.Grid.columnconfigure(self, ii, weight=1)
        for jj in list(range(2)):
            Tk.Grid.rowconfigure(self, jj, weight=1)

    def plotlog(self):
        if self.logison:
            self.logbutton["text"] = "log"
            self.logison = False
            self.ms.indata.updatefig(plotlog=False)
        else:
            self.logison = True
            self.logbutton["text"] = "lin"
            self.ms.indata.updatefig(plotlog=True)

    def update(self, val):
        self.ms.slice_along = val
        self.ms.newdata()
        self.ms.indata.updatefig(from_slicing=True, plotlog=self.logison)

    def cmapchoose(self, event):
        try:
            self.popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup.grab_release()

    def setit(self):
        self.logbutton["text"] = "log"
        self.logison = False
        try:
            self.iscalling.xmin = int(self.ey.get())
        except:
            try:
                self.iscalling.xmin = float(self.ey.get())
            except:
                pass
        try:
            self.iscalling.xmax = int(self.ey2.get())
        except:
            try:
                self.iscalling.xmax = float(self.ey2.get())
            except:
                pass
        try:
            self.iscalling.ymin = int(self.ex.get())
        except:
            try:
                self.iscalling.ymin = float(self.ex.get())
            except:
                pass
        try:
            self.iscalling.ymax = int(self.ex2.get())
        except:
            try:
                self.iscalling.ymax = float(self.ex2.get())
            except:
                pass
        try:
            self.iscalling.datamin = float(self.ez.get())
        except:
            pass
        try:
            self.iscalling.datamax = float(self.ez2.get())
        except:
            pass
        try:
            self.iscalling.updatefig()
        except:
            pass

    def reset(self):
        self.logbutton["text"] = "log"
        self.logison = False
        self.iscalling.frozen = False
        self.iscalling.getdata()
        self.iscalling.updatefig()

    def freeze(self):
        self.iscalling.frozen = True
        self.iscalling.updatefig()

    def on_size(self, event):
        # not needed?
        self.width = event.width  # in pixel
        self.height = event.height
        oneinch = 0.0393701  # mm in inch
        width_in_percentscreen = (1.0*self.width)/self.winfo_screenwidth()
        height_in_percentscreen = (1.0*self.height)/self.winfo_screenheight()
        width_in_inch = (
            width_in_percentscreen*self.winfo_screenmmwidth()*oneinch)
        self.config(width=width_in_inch, height=self.height)


class Figureframe(Tk.Frame):
    '''
    class for the frame holding the plot (middle part of the figure)
    '''
    def __init__(self, ms, msize):
        Tk.Frame.__init__(self, ms)
        self.ms = ms
        self.f = Figure(figsize=msize)  # self.mst.constants.figsize)
        self.a = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().grid(
            column=0, row=0, sticky="nsew", columnspan=2)
        self.height = self.winfo_reqheight()  # try size
        self.width = self.winfo_reqheight()
        self.toolbarframe = Tk.Frame(self)
        self.toolbarframe.grid(column=0, row=1, sticky="nsew")
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbarframe)
        self.toolbar.pack(side="left", expand=True)
        Tk.Grid.columnconfigure(self, 0, weight=1)
        Tk.Grid.columnconfigure(self, 1, weight=1)
        Tk.Grid.rowconfigure(self, 0, weight=1)
        Tk.Grid.rowconfigure(self, 1, weight=0)


class DATA1D(object):
    def __init__(self, mdata, pfr):
        self.pfr = pfr  # this is the plot frame
        self.data = mdata
        self.frozen = False
        # pfr.canvas.mpl_connect('button_press_event', self.pick)

    def makefig(self):
        self.im = self.pfr.a.plot(self.data[0], self.data[1],'.-')
        self.pfr.canvas.show()
        self.pfr.toolbar.update()


class FASTPLOT(Tk.Tk):
    '''
    parameters:
    -----------
    data: 2D or 3D np.array or cube or CubeList of 2D cubes. Not all
            functionality given in case of cubelist.
    title: string to be put in the window frame title bar

    call as e.g.: FASTPLOT(mydata, datap="plotting my data")
    '''
    def __init__(self, data, title="FASTPLOT", sliceing=0, is1D=False):
        Tk.Tk.__init__(self)
        datap = None
        data = np.squeeze(data)
        self.onedim = is1D
        #print (type(data))
        #self.mydata=data
        if is1D:
            pass
        else:
            if (isinstance(data, list) and not (
                    data.__class__.__name__ == 'CubeList')):
                try:
                    data = np.array(data)
                except:
                    pass
            if isinstance(data, np.ndarray):
                if data.ndim == 1:
                    self.onedim = True
                if data.ndim == 3:
                    datap = data
                    data = data[0]
                    print ("dispaly 0 slice along 0 dimension")
                if data.ndim > 3:
                    raise ValueError("the dimension of the data is larger than"
                                     " three, please reduce dimension")
            if data.__class__.__name__ == 'Cube':
                if data.data.ndim == 3:
                    datap = data
                    data = data[0].data
                    print ("dispaly 0 slice along 0 dimension")
                if data.data.ndim > 3:
                    raise ValueError(
                            "the dimension of the data is"
                            "larger than three, please reduce dimension")
                else:
                    data = data.data
            if data.__class__.__name__ == 'CubeList':
                datap = data
                data = data[0].data
        #print (type(datap))
        self.wm_title(title)
        self.datap = datap
        self.datai = 0
        self.slice_along = sliceing
        self.grid_propagate(True)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqheight()
        self.figfr = Figureframe(self, (7, 7))
        self.leng = 0
        if self.onedim:
            if isinstance(data, list):
                self.indata = DATA1D(data, self.figfr)
            else:
                self.indata = DATA1D([list(range(data.shape[0])), data], self.figfr)
        else:
            self.indata = DATA2D(data, self.figfr)
            self.coorfr = Coordinateframe(self, self.indata)
            self.coorfr.grid(column=0, row=2, sticky="nsew")
        self.fieldnr = self.datai
        if self.datap is not None:
            self.fieldfr = Fieldframe(self, self)
            self.fieldfr.grid(column=0, row=0, sticky="nsew")
        self.figfr.grid(column=0, row=1, sticky="nsew")
        self.indata.makefig()
        if self.datap is not None:
            if self.datap.__class__.__name__ == "list":
                self.newdata()
        Tk.Grid.columnconfigure(self, 0, weight=1)
        Tk.Grid.rowconfigure(self, 0, weight=0)
        Tk.Grid.rowconfigure(self, 1, weight=1)
        Tk.Grid.rowconfigure(self, 2, weight=0)

    def button1(self):
        self.datai = int(self.fieldfr.fldrn.get())
        self.newdata()

    def pone(self):
        self.datai = self.datai+1
        if self.leng > 1:
            self.indata.vecdata = self.vecdata[self.datai]
        try:
            self.newdata()
        except:
            self.datai = 0
            self.newdata()

    def mone(self):
        self.datai = self.datai-1
        if self.leng > 1:
            self.indata.vecdata = self.vecdata[self.datai]
        try:
            self.newdata()
        except:
            self.datai = self.leng
            self.newdata()

    def newdata(self):
        if str(self.slice_along) == str(0):
            if self.datap.__class__.__name__ == "nimfile":
                self.indata.data = (self.datap.getField(self.datai).idata *
                                    self.datap.getField(
                                        self.datai).RHEADER[7])
            elif self.datap.__class__.__name__ == 'CubeList':
                self.indata.data = self.datap[self.datai].data
            elif self.datap.__class__.__name__ == 'Cube':
                self.indata.data = self.datap.data[self.datai, :, :]
            elif (self.datap.__class__.__name__ in ['ndarray',
                                                    'MaskedArray']):
                self.indata.data = self.datap[self.datai, :, :]
        if str(self.slice_along) == str(1):
            if self.datap.__class__.__name__ == "nimfile":
                print ("this is not supported for nimfile")
            elif self.datap.__class__.__name__ == 'CubeList':
                print ("this is not supported for CubeList")
            elif self.datap.__class__.__name__ == 'Cube':
                self.indata.data = self.datap.data[:, self.datai, :]
            elif self.datap.__class__.__name__ in ['ndarray',
                                                   'MaskedArray']:
                self.indata.data = self.datap[:, self.datai, :]
        if str(self.slice_along) == str(2):
            if self.datap.__class__.__name__ == "nimfile":
                print ("this is not supported for nimfile")
            elif self.datap.__class__.__name__ == 'CubeList':
                print ("this is not supported for CubeList")
            elif self.datap.__class__.__name__ == 'Cube':
                self.indata.data = self.datap.data[:, :, self.datai]
            elif self.datap.__class__.__name__ in ['ndarray',
                                                   'MaskedArray']:
                self.indata.data = self.datap[:, :, self.datai]
        try:
            self.fieldfr.currentnr.configure(text="current field number: %.3d"
                                             % self.datai)
        except:
            pass
        self.indata.getdata()
        self.indata.updatefig(plotlog=self.coorfr.logison)
