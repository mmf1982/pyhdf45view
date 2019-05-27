#!/usr/bin/python3
'''
module to view hdf4/ hdf5/ netCDF files

developed by: Martina M. Friedrich
2017 -- 2018


    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''



import matplotlib
import sys
pyver = sys.version[0]
if pyver is "2":
    import Tkinter as Tk
    import ttk
    import tkFont
    from tkFileDialog import askopenfilename
    class dummy(object):
        def __init__(self):
            self.Dataset=dummy2
    class dummy2(object):
        def __init__(self):
            pass
        def close(self):
            pass
    netCDF4 = dummy()
elif pyver is "3":
    import tkinter as Tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
    try:
        import netCDF4v132 as netCDF4
    except:
	    import netCDF4
    from tkinter.filedialog import askopenfilename
import h5py
import Fastplot as Fp
import numpy as np
import os
import copy
import glob

# if pyver is "2":
#sys.path.append(
# "/home/martinaf/python/lib/python2.7/site-packages/python_hdf4-0.9-py2.7-linux-x86_64.egg") 
# try using the pyhdf version installed on the system for py26.
# the fix they have does not work.
import pyhdf.SD  # due to bug when variable lengths long, need this version:
import pyhdf.HDF
import pyhdf.V
import pyhdf.VS
import pyhdf.SD
# https://github.com/fhs/python-hdf4/commit/1ad85ef17a194b62bbe5c6c3eeda12b55b6666ae
# careful, I changed something in there, so I could compile it with pyinstaller
# If this is not desired, no extra fix needed.
#sys.path.append("/home/martinaf/.local/lib/python2.7/site-packages")

#print ("h5py version ", h5py.__version__)
#print ("numpy version ", np.__version__)
#print ("matplotlib version", matplotlib.__version__)
#print ("ttk version", ttk.__version__)

HDFFILEENDINGLIST=["*.hdf",
                   "*.he5",
                   "*.h5",
                   "*.h4",
                   "*.hdf5",
                   "*.hdf4",
                   "*.nc",
                   "*.he4",
                   "*.hdfeos",
                   "*.HDFEOS",
                   "*.HDF",
                   "*.NC",
                   "*.HE4",
                   "*.HE5",
                   "*.H5",
                   "*.H4",
                   "*.HDF5",
                   "*.HDF4",
                   ]

def center(toplevel, size= None):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    if size is None:
        size = tuple(2*int(_) for _
                     in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))
    return

class HELPWIN:
    def __init__(self, mtitle, mco="red"):
        self.helpw = Tk.Toplevel(background=mco)
        self.helpw.wm_title(mtitle)
        self.txt = Tk.Label(self.helpw, bg=mco,justify="left")
        self.txt.pack(side="left")

    def configtext(self, mtext):
        self.txt.configure(text=mtext)
        center(self.helpw)
        return


class handlegroup(object):
    reflist = []
    def __init__(self, tree, parent, mobject, hdfflag, pname=None, reftr=None):
        if hdfflag is 5:
            keylist = list(mobject.keys())
        elif hdfflag is "eos":
            keylist = mobject.mstruct[reftr]
        else:
            try:
                keylist = list(mobject.groups.keys())
                try:
                    keylist = keylist + list(mobject.variables.keys())
                except:
                    pass
            except:
                try:
                    keylist = list(mobject.variables.keys())
                except:
                    keylist = []
        #idxlist = np.argsort(np.array(keylist))
        #print (idxlist)
        keylist.sort()
        for key in keylist:
            #key = keylist[idx]
            if hdfflag is "eos":
                #print (key)
                kn = key[0]
                typ = key[1]
                if typ == pyhdf.V.HC.DFTAG_VG:
                    typ = "vgroup"
                elif typ == pyhdf.V.HC.DFTAG_VH:
                    typ = "vdata"
                elif typ == pyhdf.V.HC.DFTAG_NDG:
                    typ = "dataset"
                key, dims, rank, stype = mobject.get_name(key[1], key[0])
                if "fakeDim" in key or "YDim:" in key or "XDim:" in key or "ZDim:" in key:
                    continue
                if kn in self.reflist:
                    continue
                else:
                    self.reflist.append(kn)
                #print (key)
                # need to extract key from here
            if hdfflag is 5:
                mname  = mobject[key].parent.name[1:]
            else:
                try:
                    if pname is not None:
                        mname = pname
                    else:
                        mname = mobject[key].parent.name[:]
                except:
                    try:
                        mname = parent.name
                    except:
                        if pname is not None:
                            mname = pname
                        else:
                            mname = ""
            if len(mname) > 0:
                newname = mname + "/" + key
            else:
                newname  = key
            if hdfflag is 5:
                if isinstance(mobject[key], h5py.Group):
                        if parent is "1":
                            tree.insert(parent, "end", newname, text=key,
                                        values =
                                        ("","","",
                                         list(mobject[key].attrs.keys())))
                        else:
                            tree.insert(mname, "end", newname, text=key,
                                        values =
                                        ("","","",
                                         list(mobject[key].attrs.keys())))
                else:
                        try:
                            dty = mobject[key].dtype
                        except:
                            try:
                                dty = type(mobject[key])
                            except:
                                pass  # need eos impl.
                        try:
                            ndim = mobject[key].value.ndim
                        except:
                            try: 
                                f=g #need eos impl.
                            except:
                                ndim = 0
                        try:
                            dims = mobject[key].maxshape
                        except:
                            dims = []  # need eos impl.
                        if parent is "1":
                            try:
                                tree.insert(
                                    parent, "end", newname, text=key, values=
                                    (ndim, dims , dty,
                                    list(mobject[key].attrs.keys())))
                            except:
                                pass  # need eos impl.
                        else:
                            try:
                                tree.insert(
                                    mname, "end", newname, text=key, values=
                                    (ndim, dims , dty,
                                    list(mobject[key].attrs.keys())))
                            except:
                                pass
                try:
                    d=handlegroup(tree, mname, mobject[key], hdfflag)
                except Exception as e:
                        pass
            elif hdfflag is "eos":
                if parent is "1":
                        try:
                            tree.insert(parent, "end", newname, text=key,
                                        values=
                                        (rank, dims , stype, list(mobject.get_info(kn)[0].keys()), kn, typ))
                        except Exception as e:
                            print ("l246: ", e)
                else:
                            try:
                                tree.insert(mname, "end", newname, text=key,
                                            values=
                                            (rank, dims , stype, list(mobject.get_info(kn)[0].keys()),kn, typ))
                            except Exception as E:
                                tree.insert(mname.split("/")[-1], newname,
                                            text=key,values=
                                            (rank, dims , stype, [], kn,typ))
                try:
                    d=handlegroup(tree, mname, mobject,hdfflag, newname, kn)
                except:
                    pass
            else:
                try:
                    atlist = list(mobject[key].ncattrs())
                except AttributeError as act:
                    atlist = []
                if isinstance(mobject[key], netCDF4._netCDF4.Group):
                    if parent is "1":
                            tree.insert(parent, "end", newname, text=key,
                                        values= ("", "" , "",atlist))
                    else:
                            try:
                                tree.insert(mname, "end", newname, text=key,
                                            values= ("", "" , "", atlist))
                            except Exception as E:
                                tree.insert(mname.split("/")[-1], newname, text=key,
                                            values= ("", "" , "", atlist))
                else:
                        try:
                            dty = mobject[key].dtype
                        except:
                            dty = type(mobject[key])
                        try:
                            ndim = mobject[key].ndim
                        except:
                            ndim = 0
                        try:
                            dims = mobject[key].shape
                        except:
                            dims = []
                        if parent is "1":
                            try:
                                tree.insert(
                                    parent, "end", newname, text=key, values=
                                    (ndim, dims , dty, atlist))
                            except:
                                tree.insert(
                                    parent, "end", newname, text=key, values=
                                    (ndim, dims , dty,[]))
                        else:
                            try:
                                tree.insert(
                                    mname, "end", newname, text=key, values=
                                    (ndim, dims , dty, atlist))
                            except:
                                tree.insert(
                                    mname, "end", newname, text=key, values=
                                    (ndim, dims , dty,[]))
                d=handlegroup(tree, newname, mobject[key], hdfflag, newname)


class App(object):
    def __init__(self, ms, mfilename=None):
        self.hdfflag = None
        self.mfile = None
        self.mlist = []
        self.ms = ms
        self.mfilename = mfilename
        try:
            self.loadnewfile(mfilename)
        except:
            pass
        table = ttk.Frame(ms)
        filemenu = Tk.Menu(ms)
        filemenu.add_command(label="Open", command=self.newfile)
        filemenu.add_command(label="Next", command=self.nextfile)
        filemenu.add_command(label="Previous", command=self.previousfile)
        ms.config(menu=filemenu)  # menubar)
        table.pack(fill='both', expand=True)
        self.xdata = dataobj(None, "")
        self.ydata = dataobj(None, "")
        self.xerr = dataobj(None, "")
        self.yerr = dataobj(None, "")
        self.hold = False
        self.tree = ttk.Treeview(columns=["dimension", "shape", "type",
                                          "attributes", "ref","typ"])
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=table)
        vsb.grid(column=1, row=0, sticky='ns', in_=table)
        hsb.grid(column=0, row=1, sticky='ew', in_=table)
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(0, weight=1)
        self.tree.heading("dimension", text="dim")
        self.tree.heading("shape", text="shape")
        self.tree.heading("type", text="dtype/ col name")
        self.tree.heading("attributes", text="attributes")
        self.tree.heading("ref", text="refnr")
        self.tree.heading("typ", text="typ")
        self.tree.bind("<Double-1>", self.OnClick)
        self.tree.bind("<Button-3>", self.OnClick2)
        self.tree.bind("<ButtonRelease-3>", self.OffClick2)
        self.tree.bind("<Button-2>", self.make_fastplot)
        self.connectnewfile()
        buttonframe = ttk.Frame()
        buttonframe.grid(column=0, row=2, in_=table)
        self.textx = Tk.Label(buttonframe,
                              text="x data: {}".format(self.xdata.title))
        self.texty = Tk.Label(buttonframe,
                              text="y data: {}".format(self.ydata.title))
        self.button_x = Tk.Button(buttonframe,
                                  text="caputure x", command=self.getx)
        self.button_y = Tk.Button(buttonframe,
                                  text="caputre y", command=self.gety)
        self.button_error_y = Tk.Button(
            buttonframe, text="capture error y", command=self.geterrory)
        self.button_error_x = Tk.Button(
            buttonframe, text="capture error x", command=self.geterrorx)
        self.button_plot = Tk.Button(buttonframe,
                                     text="plot x-y", command=self.makeplot)
        self.button_hold = Tk.Button(buttonframe,
                                     text="hold off", command=self.holdfunc)
        self.button_clear = Tk.Button(buttonframe,
                                     text="clear", command=self.clearall)
        self.textx.pack(side="left")
        self.button_x.pack(side="left")
        self.button_error_x.pack(side="left")
        self.button_plot.pack(side="left")
        self.button_hold.pack(side="left")
        self.button_clear.pack(side="left")
        self.button_y.pack(side="left")
        self.button_error_y.pack(side="left")
        self.texty.pack(side="left")
        self.focus = "off"

    def loadnewfile(self, thisfilename):
        # print (type(thisfilename))
        # print (len(thisfilename))
        # reset the reflist handlegroup class.
        handlegroup.reflist = []
        self.ms.wm_title(thisfilename)
        self.ms.wm_iconname(thisfilename.split("/")[-1])
        print ("this file: ", thisfilename)
        ending = thisfilename.split("/")[-1].split(".")[-1]
        if isinstance(self.mfile, h5py.File):
            self.mfile.close()
        elif isinstance(self.mfile, pyhdf.SD.SD):
            self.mfile.end()
        else:
            try:
                self.mfile.close()
            except AttributeError:
                pass
        try:
            if "hdf_dd" in ending:
                try:
                    self.mfile = pyhdf.SD.SD(thisfilename, pyhdf.SD.SDC.READ)
                    self.hdfflag = 4
                except:
                    self.mfile = h5py.File(thisfilename)
                    self.hdfflag = 5
            elif "nc" in ending and pyver is "3":
                self.mfile = netCDF4.Dataset(thisfilename)
                self.hdfflag = "netcdf"
            elif "5" in ending:
                self.mfile = h5py.File(thisfilename)
                self.hdfflag = 5
            elif "he4" in ending or "hdfeos" in ending or "HDFEOS" in ending or "hdf" in ending:
                self.mfile = hdf4_object(thisfilename)
                self.hdfflag = "eos"
        except Exception as eee:
            print (eee)
            try:
                self.mfile = netCDF4.Dataset(thisfilename)
                self.hdfflag = "netcdf"
            except:
                self.mfile = pyhdf.SD.SD(thisfilename, pyhdf.SD.SDC.READ)
                self.hdfflag = 4
        self.mfilename = thisfilename
        self.mlist = self.makefilelist()
        return

    def makefilelist(self):
        mlist = []
        #print self.mfilename
        try:
            currentpath = "/".join(self.mfilename.split("/")[:-1])+"/"
        except:
            currentpath = ""
        if currentpath is "/":
            currentpath = os.getcwd() + "/"
        for ending in HDFFILEENDINGLIST:
            mlist=mlist+(glob.glob(currentpath+ending))
        mlist.sort()
        self.mfilename = currentpath + self.mfilename.split("/")[-1]
        #print mlist
        return mlist

    def previousfile(self):
        now = self.mlist.index(self.mfilename)
        self.mfilename = self.mlist[now-1]
        self.loadnewfile(self.mfilename)
        self.connectnewfile()
        return

    def nextfile(self):
        now = self.mlist.index(self.mfilename)
        try:
            self.mfilename = self.mlist[now+1]
        except IndexError as Exc:
            #warning=HELPWIN("load error")
            #warning.configtext(Exc.message)
            self.mfilename = self.mlist[0]
        self.loadnewfile(self.mfilename)
        self.connectnewfile()
        return

    def connectnewfile(self):
        zero = "1"
        print("file opened as (hdf version)", self.hdfflag)
        for entry in self.tree.get_children():
            self.tree.delete(entry)
        try:
            mtext = self.mfilename.split("/")[-1]
        except:
            mtext = ""
        if self.hdfflag == 5:
            self.tree.insert("", 0, zero, text=mtext,
                             values=( "", "", "", list(
                             		 self.mfile.attrs.keys())))
            mparent = self.mfile
            mname = zero
            d = handlegroup(self.tree, mname, mparent, self.hdfflag)
        elif self.hdfflag == 4:
            self.tree.insert("", 0, zero, text=mtext, values=
                             ( "", "", "", list(self.mfile.attributes().keys())))
            #idxlist = np.argsort(np.array(self.mfile.datasets().keys()))
            keys = (self.mfile.datasets().keys())
            #print (idxlist)
            for key in keys:  #, self.mfile.datasets().keys()):
                #key = list(self.mfile.datasets().keys())[idx]
                # print "key", key
                ndim = self.mfile.select(key).info()[1]
                dims = self.mfile.select(key).info()[2]
                if isinstance(dims, list):
                    dims = " x ".join([str(entr) for entr in dims])
                else:
                    dims = str(dims)
                mtype = self.mfile.select(key).get().dtype
                matts = (", ".join(list(self.mfile.select(key).attributes().keys())))
                self.tree.insert(zero, "end", key, text=key, values=
                                (str(ndim), dims, mtype, matts))
        elif self.hdfflag == "netcdf":
            self.tree.insert("", 0, zero, text=mtext,
                             values=( "", "", "", list(
                                    self.mfile.ncattrs())))
            mparent = self.mfile
            mname = zero
            d = handlegroup(self.tree, mname, mparent, self.hdfflag)
        elif self.hdfflag == "eos":
            self.tree.insert("",0,zero,text=mtext,
                             values=("","","", list(self.mfile.sd.attributes().keys())))
            d = handlegroup(self.tree, zero, self.mfile, self.hdfflag,reftr=-1)
        try:
            self.tree.item(zero, open=True)
        except:
            print("no file loaded")
        return

    def newfile(self):
        name = askopenfilename()
        self.loadnewfile(name)
        self.connectnewfile()
        self.mlist = self.makefilelist()
        # self.ms.title = name  # not working
        return

    def clearall(self):
        self.xdata = dataobj(None, "")
        self.ydata = dataobj(None, "")
        self.xerr = dataobj(None, "")
        self.yerr = dataobj(None, "")
        self.textx.configure(text="x data:")
        self.texty.configure(text="y data:")
        return

    def holdfunc(self):
        if self.hold:
            self.hold = False
            self.button_hold["text"] = "hold off"
            self.button_hold.configure(bg = "lightgray")
        else:
            self.hold = True
            self.button_hold["text"] = "hold on"
            self.button_hold.configure(bg = "red")
        return

    def makeplot(self):
        try:
            if not self.hold:
                self.mplot = FASTPLOT1D()
            self.mplot.addplot(self.xdata, self.ydata, self.yerr, self.xerr)
        except Exception as exceps:
            errorwindow = HELPWIN(self.xdata.title + " vs " + self.ydata.title)
            errorwindow.configtext(exceps)
        return

    def getx(self):
        if not self.focus is "on_x":
            self.button_x["text"] = "focus is on x"
            self.button_x.configure(bg = "red")
            self.button_y["text"] = "capture y"
            self.button_y.configure(bg = "lightgray")
            self.button_error_x["text"] = "capture err x"
            self.button_error_x.configure(bg = "lightgray")
            self.button_error_y["text"] = "capture err y"
            self.button_error_y.configure(bg = "lightgray")
            self.focus = "on_x"
        else:
            self.focus = "off"
            self.button_x["text"] = "capture x"
            self.button_x.configure(bg = "lightgray")
        return

    def gety(self):
        if not self.focus is "on_y":
            self.button_y["text"] = "focus is on y"
            self.button_y.configure(bg = "red")
            self.button_x["text"] = "caputre x"
            self.button_x.configure(bg = "lightgray")
            self.button_error_x["text"] = "capture err x"
            self.button_error_x.configure(bg = "lightgray")
            self.button_error_y["text"] = "capture err y"
            self.button_error_y.configure(bg = "lightgray")
            self.focus = "on_y"
        else:
            self.focus = "off"
            self.button_y["text"] = "caputre y"
            self.button_y.configure(bg = "lightgray")
        return

    def geterrory(self):
        if self.focus is not "on_errory":
            self.button_error_y["text"] = "focus on err y"
            self.button_error_y.configure(bg="red")
            self.button_x["text"] = "capture x"
            self.button_x.configure(bg="lightgray")
            self.button_y["text"] = "capture y"
            self.button_y.configure(bg="lightgray")
            self.button_error_x["text"] = "capture err x"
            self.button_error_x.configure(bg="lightgray")
            self.focus = "on_errory"
        else:
            self.focus = "off"
            self.button_error_y["text"] = "capture err y"
            self.button_error_y.configure(bg="lightgray")
        return

    def geterrorx(self):
        if self.focus is not "on_errorx":
            self.button_error_x["text"] = "focus on err x"
            self.button_error_x.configure(bg="red")
            self.button_x["text"] = "capture x"
            self.button_x.configure(bg="lightgray")
            self.button_y["text"] = "capture y"
            self.button_y.configure(bg="lightgray")
            self.button_error_y["text"] = "capture err y"
            self.button_error_y.configure(bg="lightgray")
            self.focus = "on_errorx"
        else:
            self.focus = "off"
            self.button_error_x["text"] = "capture err x"
            self.button_error_x.configure(bg="lightgray")
        return

    def OnClick(self, event):
        if self.hdfflag == "eos":
            item = self.tree.selection()
            refnumber = self.tree.item(item[0])["values"][-2]
            mdata = self.mfile.get_data(refnumber)
            key = item[0].split("/")[-1]
            table = MTable(self, key, mdata)
        else:
            item = self.tree.selection()[0]
            keys = item.split("/")
            mdata = self.mfile
            for key in keys[:-1]:
                mdata = mdata[key]
            key = keys[-1]
            table = MTable(self, key, mdata)
        return

    def make_fastplot(self, event):
        if self.hdfflag == "eos":
            item = self.tree.selection()
            refnumber = self.tree.item(item[0])["values"][-2]
            data = np.array(self.mfile.get_data(refnumber)[:])
            key = item[0].split("/")[-1]
        else:
            item = self.tree.selection()[0]
            keys = item.split("/")
            mdata = self.mfile
            for key in keys[:-1]:
                mdata = mdata[key]
            key = keys[-1]
            if self.hdfflag == 5 :
                data = mdata[key].value
            if self.hdfflag == "netcdf":
                data = mdata.variables[key][:]
            elif self.hdfflag == 4:
                data = self.mfile.select(key)[:]
        #if data.ndim >= 2:
        mfig = Fp.FASTPLOT(data, title=key)
        return

    def OnClick2(self, event):
        if self.hdfflag == "eos":
            item = self.tree.selection()
            refnumber = self.tree.item(item[0])["values"][-2]
            mdata = self.mfile.get_info(refnumber)
            key = item[0].split("/")[-1]
        else:
            item = self.tree.selection()[0]
            keys = item.split("/")
            mdata = self.mfile
            mdat = mdata
            if keys != ['1']:
                try:
                    for key in keys:
                        mdat = mdat[key]
                except Exception as E:
                    pass
            else:
                key = None
        if self.hdfflag == 5:
            print ("\n")
            print ("info on: ", key)
            print ("----------" )
            print ("atrs:", list(mdat.attrs))
            print ("   -------")
            for keys in mdat.attrs.keys():
                try:
                    print (keys, ": ", mdat.attrs[keys])
                except:
                    print (keys, " string, due to incompatibility not displayable")
            print (mdat)
            #self.attr_frame = Attributewindow(mdat.attrs, key)
        elif self.hdfflag == "netcdf":
            try:
                print ("\n")
                print ("info on: ", mdat.name)
            except:
                try:
                    print ("info on: ", mdat.title)
                except:
                    print ("info on: ", mdat.filepath())
            print ("---------")
            print (mdat)
            print ("---------\n")
        elif self.hdfflag == 4:
            if key is None:
                print ("\ninfo on main ")
                print ("attribute  name:  value")
                mdict = self.mfile.attributes()
            else:
                print ("\ninfo on: ", key)
                print ("attribute  name:  value")
                mdict = self.mfile.select(key).attributes()
            try:
                    keylist = list(mdict.keys())
                    idxlist = np.argsort(np.array(keylist))
                    #print (keylist, mdict)
                    for idx in idxlist:
                        key = keylist[idx]
                        try:
                            print (key, ":\t", mdict[key])
                        except Exception as E:
                            print (E)
                    #self.attr_frame = Attributewindow(
                    #    self.mfile.select(key).attributes(), key)
            except:
                    pass
                    #self.attr_frame = Attributewindow(self.mfile.attributes(), key)
            print ("---------\n")
        elif self.hdfflag == "eos":
            print ("info on: ", key)
            print ("---------")
            for xkey in mdata[0].keys():
                print (xkey, ": ", mdata[0][xkey])
            print (mdata[1])
            print ("")
        return

    def OffClick2(self, event):
        pass
        #self.attr_frame.destroy()
        #return


class hdf4_object(object):
    def __init__(self, filename):
        self.sd = pyhdf.SD.SD(filename)
        self.hdf = pyhdf.HDF.HDF(filename)
        self.vs = self.hdf.vstart()
        self.v = self.hdf.vgstart()
        self.mstruct = self.get_structure()

    def get_structure(self):
        mref = -1
        reflist = {}
        reflist[-1] =[]
        reflist_done = []
        while True:
            try: 
                mref = self.v.getid(mref)
                if mref in reflist_done:
                    continue
                reflist[-1].append((mref, pyhdf.HDF.HC.DFTAG_VG))
            except pyhdf.HDF.HDF4Error:
                break
            reflist[mref], rl = self.get_structure2(mref, reflist)
            reflist_done.extend(rl)
        return reflist

    def get_structure2(self, refs, reflist):
        gr = self.v.attach(refs)
        allmem = gr.tagrefs()
        arglist = []
        refsdone = []
        for tag, ref in allmem:
            if tag == pyhdf.HDF.HC.DFTAG_VH:
                #arglist.append(self.vs.attach(ref).inquire()[-1])
                arglist.append((ref, tag))
            if tag == pyhdf.HDF.HC.DFTAG_NDG:
                arglist.append((ref, tag))
            #        self.sd.select(self.sd.reftoindex(ref)).info()[0])
            if tag == pyhdf.HDF.HC.DFTAG_VG:
                in_there, refm = self.get_structure2(ref, reflist)
                refsdone.append(refm)
                reflist[ref] = in_there
                arglist.append((ref, tag))
            refsdone.append(ref)
        return arglist, refsdone

    def get_data(self, ref):
        if isinstance(ref, tuple):
            ref = ref[0]
        try:
            a = self.vs.attach(ref)
        except:
            a = self.sd.select(self.sd.reftoindex(ref))
        return a

    def get_info(self, ref):
        if ref == "":
            attributes = self.sd.attributes()
            otherinfo = None
        else:
            try:
                a = self.vs.attach(ref)
                attributes = a.attrinfo()
                otherinfo = a.inquire()  
                # number records, interlace mode, lisf of field names, size in bytes, name of vdata
            except:
                try:
                    a = self.sd.select(self.sd.reftoindex(ref))
                    attributes = a.attributes()
                    otherinfo = a.info()
                    # name, rank, shape, dimension, type, attributes
                except:
                    try:
                        a = self.v.attach(ref)
                        attributes = a.attrinfo()
                        otherinfo = None
                    except:
                        attributes = {}
                        otherinfo = None
        return attributes, otherinfo

    def get_name(self, tag, ref):
        dims = rank = name = stype = None
        if tag == pyhdf.HDF.HC.DFTAG_VH:
            dims, rank, stype, trash, name =  (self.vs.attach(ref).inquire())
        elif tag == pyhdf.HDF.HC.DFTAG_NDG:
            name, rank, dims, stype, nattrs =  (self.sd.select(self.sd.reftoindex(ref)).info())
        elif tag == pyhdf.HDF.HC.DFTAG_VG:
            name =  (self.v.attach(ref)._name)
        return name, dims, rank, stype

class Attributewindow(object):
    def __init__(self, mdict, title,master=None, hdfv=None):
        self.root = Tk.Toplevel()
        try:
            center(self.root, (350, 32*(1+len(list(mdict.keys())))))
        except:
            center(self.root, (350, 32*(1+len(mdict))))
        self.root.title(title)
        pframe = ttk.Frame(self.root)
        pframe.pack(fill='both', expand=True)
        try:
            tree = ttk.Treeview(pframe, columns=["name", "content"],
                            show="headings", height = 16 * len(list(mdict.keys())))
        except:
            tree = ttk.Treeview(pframe, columns=["name", "content"],
                            show="headings", height = 16 * len(mdict))
        tree.pack(expand=True)
        maxwidth1 = tkFont.Font().measure("attribute name")
        maxwidth2 = tkFont.Font().measure("attribute value")
        try:
            maxwidth1 = max(
                max([tkFont.Font().measure(jj) for jj in list(mdict.keys())]),
                maxwidth1)
        except:
            try:
                maxwidth1 = max(
                max([tkFont.Font().measure(jj) for jj in mdict]),
                maxwidth1)
            except:
                pass
        try:
            maxwidth2 = max(
                max([tkFont.Font().measure(mdict[jj]) for jj in list(mdict.keys())]),
                maxwidth2)
        except:
            try:
                maxwidth2 = max(
                max([tkFont.Font().measure(mdict[jj]) for jj in mdict]),
                maxwidth2)
            except:
                pass
        tree.column("name", width = maxwidth1)
        tree.column("content", width = maxwidth2)
        # tree.pack(side="top", expand=True)  #, in_=self.pframe)
        tree.heading("name", text="attribute name")
        tree.heading("content", text="attribute value")
        print ("-- ", title, " --")
        print ("  name, value")
        try:
            keylist = list(mdict.keys())
            idxlist = np.argsort(np.array(keylist))
            #print (keylist, mdict)
            for idx in idxlist:
                key = keylist[idx]
                try:
                    tree.insert("", "end", key, values=(key, mdict[key]))
                    print (key, mdict[key])
                except OSError:  # python 3
                    print (key, "string, due to netCDF4 h5py incompatibility not displayable")
                except IOError:
                    print (key, "string, due to netCDF4 h5py incompatibility not displayable")
        except:
            print (mdict.keys())
            _ = input("d")
            keylist = mdict
            for key in keylist:
                print (key)
        try:
            mval = eval("master."+key)
        except:
            mval = eval("master.getncattr("+key+")")
            print (key, mval)
            tree.insert("","end",key, values=(key,mval))
    def destroy(self):
        self.root.destroy()
        return


class FASTPLOT1D(object):
    def __init__(self):
        root = Tk.Toplevel()
        self.plotframe = Fp.Figureframe(root, (7, 7))
        self.plotframe.grid(column=0, row=0, sticky="nsew")
        Tk.Grid.columnconfigure(root, 0, weight=1)
        Tk.Grid.rowconfigure(root, 0, weight=1)
        self.manipframe = Tk.Frame(root)
        self.manipframe.grid(column=0, row=1, sticky="nsew")

    def addplot(self, xdata, ydata, yerr=None, xerr=None):
        if yerr is None:
            yerr = dataobj(None, "")
        if xerr is None:
            xerr = dataobj(None, "")
        try:
            line  = self.plotframe.a.errorbar(
                xdata.data, ydata.data, yerr.data, xerr.data,
                label=xdata.title + " vs " + ydata.title)
        except Exception as ex:
            line = self.plotframe.a.plot(xdata.data,ydata.data,
                                         label=xdata.title + " vs " + ydata.title)
        self.plotframe.a.legend()
        self.plotframe.canvas.show()
        self.plotframe.toolbar.update()
        maniframe = changelineplot(self, self.manipframe, line)
        return line


class changelineplot(object):
    def __init__(self, master, mframe, lineobj):
        maniframe = Tk.Frame(mframe)
        maniframe.pack(side="top")
        self.line = lineobj.get_children()[0]
        self.obj = lineobj
        self.hide = Tk.IntVar()
        self.master = master
        self.ez2 = Tk.Entry(maniframe, width=50)
        self.ez2.pack(side="left")
        self.ez2.focus_set()
        button1 = Tk.Button(maniframe,text="get",command=self.getdata)
        button1.pack(side="left")
        button2 = Tk.Button(maniframe, text="help", command=self.mhelp)
        button2.pack(side="left")
        button3 = Tk.Checkbutton(maniframe, text="hide", variable=self.hide,
                                 onvalue=1, offvalue=0,
                                 command=self.mupdate)
        button3.pack(side="left")

    def mhelp(self):
        d = HELPWIN("help for line plots", "lightyellow")
        mtext = ("Type commands here to change line styles. \n"
                 "the commands need to have the form: \n"
                 " key1=value1, key2=value2, key3=value3 \n"
                 " available for keys are: \n"
                 " linecolor: sets line color \n"
                 " marker: sets marker stype \n"
                 " width: sets line width \n"
                 " style: sets line style \n"
                 " size: sets marker size (marker needs to be set) \n"
                 " markercolor: sets marker color (marker needs to be set) \n"
                 " delete: delete this line-marker-plot \n"
                 " label: overwrite the label")
        d.configtext(mtext)
        return

    def mupdate(self):
        if isinstance(self.obj, matplotlib.lines.Line2D):
            alllines = [self.obj]
        else:
            alllines = self.obj.get_children()
        if self.hide.get() is 0:
            for oneline in alllines:
                try:
                    oneline.set_visible(True)
                except:
                    pass
        else:
            for oneline in alllines:
                try:
                    oneline.set_visible(False)
                except:
                    pass
        self.master.plotframe.a.legend()
        self.master.plotframe.canvas.show()
        return

    def getdata(self):
        text = self.ez2.get()
        self.processtext(text)
        return

    def processtext(self, text):
        mtext = text.split(",")
        self.legend=self.master.plotframe.a.legend()
        for entry in mtext:
            key, value = entry.split("=")
            key = key.strip(" ")
            value = value.strip(" ")
            if "linecolor" in key:
                for line in self.obj:
                    try:
                        line.set_color(value)
                    except:
                        try:
                            line[0].set_color(value)
                        except:
                            pass
            if "markercolor" in key:
                self.line.set_markerfacecolor(value)
                self.line.set_markeredgecolor(value)
            if key in "marker":
                self.line.set_marker(value)
            if "width" in key:
                try:
                    self.line.set_linewidth(float(value))
                except Exception as e:
                	print (e)
            if "style" in key:
                self.line.set_linestyle(value)
            if "size" in key:
                self.line.set_markersize(float(value))
            if "delete" in key:
                self.line.remove()
                self.obj.set_label("_nolegend_")
                self.legend.remove()
            if "label" in key:
                #self.master.plotframe.a.legend
                self.obj.set_label(value)
        self.legend=self.master.plotframe.a.legend()
        self.master.plotframe.canvas.show()
        return


class dataobj(object):
    def __init__(self, data, descriptor):
        self.data = data
        self.title = descriptor
        return


class ButtonFrame(object):
    def __init__(self, master):
        mframe = master.extraframe
        self.master = master
        self.ndim3buttonplus = Tk.Button(mframe, text="+", command=self.plus)
        self.ndim3readfield = Tk.Label(mframe, text=0)
        self.ndim3buttonminus = Tk.Button(mframe, text="-", command=self.minus)
        self.ndim3buttonplus.pack(side="right")
        self.ndim3readfield.pack(side="right")
        self.ndim3buttonminus.pack(side="right")
        self.value = 0
        self.orient = 0
        self.sliceslider = Tk.Scale(
            mframe, from_=0, to=2, orient="horizontal", command=self.update)
        self.sliceslider.pack(side="right")
        self.fieldtxt = Tk.Label(
                mframe, text="slice along dimension: ")
        self.fieldtxt.pack(side="right")

    def update(self, val):
        val = str(val)
        if val =="2":
            self.orient = 2
        elif val =="1":
            self.orient = 1
        elif val == "0":
            self.orient = 0
        self.reconfigview()


    def plus(self):
        self.value = self.value + 1
        self.reconfigview()
        return

    def minus(self):
        self.reconfigview()
        self.value = self.value - 1
        return

    def reconfigview(self):
        self.ndim3readfield.configure(text=self.value)
        if self.orient == 0:
            self.master.data = self.master.datao[self.value]
        elif self.orient == 1:
            self.master.data = self.master.datao[:,self.value,:]
        elif self.orient == 2:
            self.master.data = self.master.datao[:,:,self.value]
        self.master.process_raw_data(self.master.data,
                                     self.master.mtitle)
        self.master.configure(self.master.mtitle)
        return


class MTable():
    def __init__(self, master, mkey, mfile):
        self.master = master
        self.pframe = ttk.Frame()
        if master.hdfflag == 5:
            self.datao = mfile[mkey]
        elif master.hdfflag == 4:
            self.datao = mfile.select(mkey)
        elif master.hdfflag == "netcdf":
            self.datao = mfile[mkey]
        elif master.hdfflag == "eos":
            self.datao = np.array(mfile[:])
        self.data = None
        self.mtitle = mkey
        self.pframe.pack(fill="both", expand=True)
        try:
            print(mkey)
            print(self.datao.shape)
            self.process_data(self.datao, mkey)
            self.data = self.datao
        except AttributeError as Eee:
            print (Eee)
            if master.hdfflag == 5 or master.hdfflag == "netcdf":
                try:
                    ndim = self.datao.value.ndim
                except AttributeError:
                    try: 
                        ndim = self.datao.ndim
                    except:
                        ndim = 0
            elif master.hdfflag == 4:
                ndim = self.datao.info()[1]
            elif master.hdfflag == "eos":
                try:
                    ndim = self.datao.ndim
                except:
                    ndim = 1 # not right? TODO
            if ndim <= 2:
                if self.master.hdfflag == 5 or self.master.hdfflag == "netcdf":
                    self.data = self.datao
                    self.process_raw_data(self.data, mkey)
                elif self.master.hdfflag == 4 or self.master.hdfflag == "eos":
                    self.data = self.datao[:]
                    self.process_raw_data(self.data, mkey)
            else:
                try:
                    self.datao = np.squeeze(self.datao[:])
                except Exception as exc:
                    print (exc)
                    self.datao = np.squeeze(self.datao)
                    print("squeeze failed")
                    print("************************************************")
                print ("after squeeze", self.datao.shape)
                if len(self.datao.shape)==3:
                    if self.master.hdfflag == 5 or self.master.hdfflag == "netcdf":
                        self.data = self.datao[0]
                    elif self.master.hdfflag == 4 or self.master.hdfflag == "eos":
                        self.data = (self.datao[:])[0]
                    self.extraframe = Tk.Frame(self.pframe)
                    self.extraframe.grid(column=2, row=0)
                    self.newframe = ButtonFrame(self)
                    self.process_raw_data(self.data, mkey)
                elif len(self.datao.shape)==2:
                    if self.master.hdfflag == 5 or self.master.hdfflag == "netcdf":
                        self.data = self.datao
                        self.process_raw_data(self.datao, mkey)
                    elif self.master.hdfflag == 4 or self.master.hdfflag == "eos":
                        self.data = self.datao[:]
                        self.process_raw_data(self.data, mkey)
                elif len(self.datao.shape)>3:
                    print("data has shape: ", self.datao.shape, "too high dimension to display")
        try:
            self.configure(mkey)
        except AttributeError:
            pass

    def process_data(self, data, mkey):
        print(mkey)
        try:
            allkeys = tuple(list(data.value.dtype.fields.keys()))
        except Exception as exc:
            print (exc)
            print (data.shape)
            print("key:", mkey)
            try:
                allkeys = tuple(range(len(data.value)))
            except TypeError:
                allkeys = tuple(range(1))
        self.tree = ttk.Treeview(columns=allkeys, show="headings")
        for key in allkeys:
            self.tree.heading(
                key, text=key, command=lambda c=key: self.OnClick(c))
            self.tree.column(key, width=tkFont.Font().measure(key.title()))
        try:
            for idx, line in enumerate(data.value):
                mline = [line[key] for key in allkeys]
                self.tree.insert("", idx, str(idx), text=str(idx), values=mline)
        except:
            mline = []
            mline = [data.value[key] for key in allkeys]
            self.tree.insert("", "end", str(1), text=str(1), values=mline)
        return

    def process_raw_data(self, data, mkey):
        try:
            ndim = data.ndim
        except:
            ndim = data.value.ndim
        if ndim == 2:
            if data.shape[1]>0:
                # print("data shape", data.shape)
                self.tree = ttk.Treeview(  # this is for 2D matrix
                    columns=list(range(data.shape[1])), show="headings")
                for idx in list(range(data.shape[1])):
                    self.tree.heading(idx, text=str(idx),
                                    command=lambda c=idx: self.OnClick(c))
                for line in data:
                    mline = [val for val in line]
                    self.tree.insert("", "end", values=mline)
            else:
                if data.shape[0]>0:
                    self.tree = ttk.Treeview(  # this is for 2D matrix
                        columns=mkey, show="headings")
                    self.tree.heading(0, text=0,
                                command=lambda c=mkey: self.OnClick(c))
                    for line in np.squeeze(data):
                        self.tree.insert("", "end", values=line)
                else:
                    self.tree = ttk.Treeview(  # this is for 0D matrix
                        columns=mkey, show="headings")
                    self.tree.heading(0, text=0)
                    mtext = data[:]
                    if isinstance(mtext, str):
                        mtext = '"' + mtext + '"'
                    self.tree.insert("", "end", values=mtext)
        elif ndim == 1:
            if data.shape[0]>0:
                self.tree = ttk.Treeview(  # this is for 2D matrix
                    columns=mkey, show="headings")
                self.tree.heading(0, text=0,
                                command=lambda c=mkey: self.OnClick(c))
                for line in data:
                    self.tree.insert("", "end", values=line)
            else:
                self.tree = ttk.Treeview(  # this is for 0D matrix
                    columns=mkey, show="headings")
                self.tree.heading(0, text=0)
                mtext = data[:]
                if isinstance(mtext, str):
                    mtext = '"' + mtext + '"'
                self.tree.insert("", "end", values=mtext)
        elif ndim == 0:
            self.tree = ttk.Treeview(  # this is for 0D matrix
                columns=mkey, show="headings")
            self.tree.heading(0, text=0)
            try:
                mtext = data.value
            except AttributeError:
                mtext = data[:]
            if isinstance(mtext, str):
                mtext = '"' + mtext + '"'  # needed because spaces not handled
            self.tree.insert("", "end", values=mtext)
        elif ndim > 2:
            warning=HELPWIN(mkey)
            warning.configtext("currently not implemented to handle data with higher dimension than 3\n")
        return

    def configure(self, mkey):
        self.vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.tree.grid(column=1, row=1, sticky='nsew', in_=self.pframe)
        self.button = Tk.Button(
            self.pframe, text="x", width=1, command=self.delete, bg="red")
        title = Tk.Label(text=mkey, fg="red")
        title.grid(column=1, row=0, sticky='nsew', in_=self.pframe)
        self.button.grid(column=0, row=0, sticky='nsew', in_=self.pframe)
        self.vsb.grid(column=2, row=1, sticky='ns', in_=self.pframe)
        self.hsb.grid(column=1, row=2, sticky='ew', in_=self.pframe)
        self.tree.bind("<Double-1>", self.OnClick2)
        self.pframe.grid_rowconfigure(1, weight=1)
        self.pframe.grid_columnconfigure(1, weight=1)
        self.pframe.grid_rowconfigure(0, weight=0)
        self.pframe.grid_columnconfigure(0, weight=0)
        self.pframe.grid_columnconfigure(2, weight=0)
        return

    def delete(self):
        self.pframe.pack_forget()
        self.pframe.destroy()
        return

    def make_idx_of_item(self, itemstring):
        try:
            number = int(itemstring)
        except:
            # try without the first diget
            number = int(itemstring[1:], 16)-1
        return number

    def OnClick2(self, event):
        item = self.tree.selection()[0]
        idx = self.make_idx_of_item(item)
        if self.master.focus is "off":
            try:
                Fp.FASTPLOT(self.data[idx], title=self.mtitle +  # .flatten()
                            " line " + str(idx))
            except:
                warnwin = HELPWIN(self.mtitle + " line " + str(idx))
                warnwin.configtext("not a matrix. Not sure what to do")
        elif self.master.focus is "on_x":
            try:
                self.master.xdata = dataobj(self.data[idx],
                                            self.mtitle + " line " + str(idx))
                self.configtext("x")
            except:
                warnwin = HELPWIN(self.mtitle + " line " + str(idx))
                warnwin.configtext("not a matrix. Not sure what to do")
        elif self.master.focus is "on_y":
            try:
                self.master.ydata = dataobj(self.data[idx],
                                            self.mtitle + " line " + str(idx))
                self.configtext("y")
            except:
                warnwin = HELPWIN(self.mtitle + " line " + str(idx))
                warnwin.configtext("not a matrix. Not sure what to do")
        elif self.master.focus is "on_errory":
            try:
                self.master.yerr = dataobj(self.data[idx],
                                           self.mtitle + " line " + str(idx))
                self.configtext("yerror")
            except:
                warnwin = HELPWIN(self.mtitle + " line " + str(idx))
                warnwin.configtext("not a matrix. Not sure what to do")
        elif self.master.focus is "on_errorx":
            try:
                self.master.xerr = dataobj(self.data[idx],
                                           self.mtitle + " line " + str(idx))
                self.configtext("xerror")
            except:
                warnwin = HELPWIN(self.mtitle + " line " + str(idx))
                warnwin.configtext("not a matrix. Not sure what to do")
        return

    def configtext(self, letter):
        if letter is "x":
            text = "x data: {}".format(self.master.xdata.title)
            self.master.textx.configure(text=text)
        if letter is "y":
            text = "y data: {}".format(self.master.ydata.title)
            self.master.texty.configure(text=text)
        if letter is "xerror":
            text = "x error: {}".format(self.master.xerr.title)
            self.master.textx.configure(text=text)
        if letter is "yerror":
            text = "y error: {}".format(self.master.yerr.title)
            self.master.texty.configure(text=text)
        return

    def OnClick(self, key):
        try:
            ndim = self.data.ndim
        except:
            ndim = self.data.value.ndim
        if self.master.focus is "off":
            if isinstance(key, int):  # I need the column, not the row!
                if ndim == 2:
                    Fp.FASTPLOT(self.data[:, key].flatten(), title=self.mtitle 
                                + " column " + str(key)) # added flatt
                else:
                    Fp.FASTPLOT(self.data[key], title=self.mtitle +
                                " column " + str(key))
            else:
                try:
                    Fp.FASTPLOT(self.data.value[key].flatten(), title=key)
                    # added flatt
                except:
                    try:
                        Fp.FASTPLOT(self.data.flatten(), title=key)
                        # added flatt
                    except:
                        try:
                            Fp.FASTPLOT(self.data.value.flatten(), title=key)
                        except Exception as e:
                            Fp.FASTPLOT(self.data, title=key)
                        # added flatt
        elif self.master.focus is "on_x":
            if isinstance(key, int):  # I need the column, not the row!
                if ndim == 2:
                    self.master.xdata = dataobj(
                        self.data[:, key], self.mtitle + " column " + str(key))
                else:
                    self.master.xdata = dataobj(
                        self.data[key], self.mtitle + " column " + str(key))
            else:
                try:
                    self.master.xdata = dataobj(self.data[key], key)
                except:
                    try:
                        self.master.xdata = dataobj(self.data[:], key)
                    except:
                        self.master.xdata = dataobj(self.data, key)
            self.configtext("x")
        elif self.master.focus is "on_y":
            if isinstance(key, int):  # I need the column, not the row!
                if ndim == 2:
                    self.master.ydata = dataobj(
                        self.data[:, key], self.mtitle + " column " + str(key))
                else:
                    self.master.ydata = dataobj(
                        self.data[key], self.mtitle + " column " + str(key))
            else:
                try:
                    self.master.ydata = dataobj(self.data.value[key], key)
                except:
                    try:
                        self.master.ydata = dataobj(self.data[:], key)
                    except:
                        self.master.ydata = dataobj(self.data, key)
            self.configtext("y")
        elif self.master.focus is "on_errory":
            if isinstance(key, int):  # I need the column, not the row!
                if ndim == 2:
                    self.master.yerr = dataobj(
                        self.data[:, key], self.mtitle + " column " + str(key))
                else:
                    self.master.yerr = dataobj(
                        self.data[key], self.mtitle + " column " + str(key))
            else:
                try:
                    self.master.yerr = dataobj(self.data.value[key], key)
                except:
                    try:
                        self.master.yerr = dataobj(self.data[:], key)
                    except:
                        self.master.yerr = dataobj(self.data, key)
            self.configtext("yerror")
        elif self.master.focus is "on_errorx":
            if isinstance(key, int):  # I need the column, not the row!
                if ndim == 2:
                    self.master.xerr = dataobj(
                        self.data[:, key], self.mtitle + " column " + str(key))
                else:
                    self.master.xerr = dataobj(
                        self.data[key], self.mtitle + " column " + str(key))
            else:
                try:
                    self.master.xerr = dataobj(self.data.value[key], key)
                except:
                    try:
                        self.master.xerr = dataobj(self.data[:], key)
                    except:
                        self.master.xerr = dataobj(self.data, key)
            self.configtext("xerror")
        return


def main(mfile=None):
    root = Tk.Tk()
    if mfile is None:
        if (len(sys.argv) == 2):
            mfilename = sys.argv[1:][0]
            root.wm_title(mfilename)
            root.wm_iconname(mfilename)
            app = App(root, mfilename)
        else:
            app = App(root)
    else:
        mfilename = mfile
        root.wm_title(mfilename)
        root.wm_iconname(mfilename)
        app = App(root, mfilename)
    root.mainloop()

if __name__ == "__main__":
    main()
