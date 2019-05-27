import netCDF4
import sys
import h5py
import numpy as np

class CompareNETCDF4(object):
    def __init__(self, file1, file2, outfile):
        self.path1 = file1
        self.path2 = file2
        # print("file1: ", file1)
        # print("file2: ", file2)
        self.outfile = outfile
        self.mfile1 = netCDF4.Dataset(file1)
        self.mfile2 = netCDF4.Dataset(file2)
        self.differences = {}
        self.differences["File1"] = self.path1
        self.differences["File2"] = self.path2

    def compare(self):
        self.differences = {}
        _ = self.groupdiffs(self.mfile1, self.mfile2, "/")
        _ = self.writefile()
        return

    def attrdiffs(self, root1, root2, basekey):
        list1 = root1.ncattrs()
        list2 = root2.ncattrs()
        in1notin2 = set(list1).difference(set(list2))
        if len(in1notin2)>0:
            self.differences[basekey + "/attributes/in1_not_in2"] = ", ".join(
                np.array(list(in1notin2)).astype("str"))
        in2notin1 = set(list2).difference(set(list1))
        if len(in2notin1) > 0:
            self.differences[basekey + "/attributes/in2_not_in1"] = ", ".join(
                np.array(list(in2notin1)).astype("str"))
        for key in set(list2).intersection(set(list1)):
            arg1 = root1.getncattr(key)
            arg2 = root2.getncattr(key)
            # print(type(arg1), type(arg2))
            if arg1 == arg2:
                pass
            else:
                try:
                    mtest = np.isnan(arg1) and np.isnan(arg2)
                    if mtest:
                        continue
                    else:
                        self.differences[basekey + "/attributes/" + key] = (
                        "differ  "+"\n1: "+str(arg1) +"\n2: "+ str(arg2))
                except:
                    self.differences[basekey + "/attributes/" + key] = (
                        "differ  "+"\n1: "+str(arg1) +"\n2: "+ str(arg2))
        return

    def writefile(self):
        with h5py.File(self.outfile, "w") as h5f:
            for key in self.differences:
                try:
                    h5f.create_dataset(key, data=self.differences[key])
                except Exception as exc:
                    print (key, self.differences[key])
                    print(exc)

    def vardiff(self, mvar1, mvar2, basekey):
        _ = self.attrdiffs(mvar1, mvar2, basekey)
        # print(mvar1.name, mvar1.group().path)
        try:
            var1 = np.ma.masked_invalid(mvar1[:])
            var2 = np.ma.masked_invalid(mvar2[:])
            # print( "ok")
        except TypeError:  # this means it is a text array
            mtest = mvar1[:] == mvar2[:]
            if mtest:
                return
            else:
                self.differences[basekey + "/value(1)"] = mvar1[:]
                self.differences[basekey + "/value(2)"] = mvar2[:]
                return
        #check first if the shapes of the variables agree:
        if var1.shape == var2.shape:
            pass
        else:
            self.differences[basekey + "/values"] = (
                " shapes differ: var1: " + str(var1.shape) +
                        " var2: " + str(var2.shape))
            return
        # now, both var1 and var2 should be masked arrays. Check first if the
        # masks agree:
        maskagree = (var1.mask == var2.mask).all()
        if maskagree:
            try:
                mtest = (var1[~var1.mask] == var2[~var2.mask]).all()
            except Exception as exc:
                print (exc)
                mtest = var1 == var2
        else:
            mtest = False
        if mtest and maskagree:
            return
        else:
            try:
                mtest2 = (var1[~np.isnan(var1)] == var2[~np.isnan(var2)]).all()
                if mtest2:
                    return
            except:
                try:
                     mtest2 = (var1[~np.isnan(var1)] == var2[~np.isnan(var2)])
                     if mtest2:
                         return
                except:
                    pass
            margs = "differ, "
            if type(var1) == type(var2):
                margs = margs + "have same type same type"
            else:
                margs = (
                    margs + "types differ: var1 : " + str(type(var1)) +
                    " var2: " + str(type(var2)))
            try:
                if var1.shape == var2.shape:
                    margs =  var1 - var2
                    if np.isnan(var1).all() and np.isnan(var2).all():
                        return
                    self.differences[basekey + "/value(1)"] = var1
                    self.differences[basekey + "/value(2)"] = var2
                    self.differences[basekey + "value(1-2)"] = margs
                    return
                else:
                    margs =(
                        margs + " shapes differ: var1: " + str(var1.shape) +
                        " var2: " + str(var2.shape))
            except:
                try:
                    if len(var1) == len(var2):
                        margs =  margs + " same len"
                        try:
                            mtest = var1 == var2
                            if mtest:
                                return
                            else:
                                if type(var1)==str:
                                    if type(var2)==str:
                                        margs = margs + ("\n1: ", var1,
                                                         "\n2: ", var2)
                                pass
                        except:
                            pass
                    else:
                        margs =(
                            margs + " len differ: var1: " + str(len(var1)) +
                            " var2: " + str(len(var2)))
                except:
                    pass
            self.differences[basekey + "/values"] = margs
        return


    def groupdiffs(self, root1, root2, basekey):
        # check differences in groups:
        list1 = root1.groups.keys()
        list2 = root2.groups.keys()
        in1notin2 = set(list1).difference(set(list2))
        in2notin1 = set(list2).difference(set(list1))
        if len(in1notin2)>0:
            self.differences[basekey + "/groups_in1_not_in2"] = ", ".join(
                np.array(list(in1notin2)).astype("str"))
        if len(in2notin1) > 0:
            self.differences[basekey + "/groups_in2_not_in1"] = ", ".join(
                np.array(list(in2notin1)).astype("str"))
        for key in set(list2).intersection(set(list1)):
            newkey = basekey + "/" + key + "/"
            self.groupdiffs(root1[key], root2[key], newkey)
        # now, handle the variables:
        list1 = root1.variables.keys()
        list2 = root2.variables.keys()
        in1notin2 = set(list1).difference(set(list2))
        in2notin1 = set(list2).difference(set(list1))
        if len(in1notin2)>0:
            self.differences[basekey + "/variables_in1_not_in2"] = ", ".join(
                np.array(list(in1notin2)).astype("str"))
        if len(in2notin1) > 0:
            self.differences[basekey + "/variables_in2_not_in1"] = ", ".join(
                np.array(list(in2notin1)).astype("str"))
        for key in set(list2).intersection(set(list1)):
            newkey = basekey + "/" + key + "/"
            self.vardiff(root1[key], root2[key], newkey)
        # now, handle the attributes:
        _ = self.attrdiffs(root1, root2, basekey)
        return


def main(file1, file2, outfile):
    _ = CompareNETCDF4(file1, file2, outfile).compare()
    return


if __name__ == "__main__":
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    outfile = sys.argv[3]
    main(file1, file2, outfile)