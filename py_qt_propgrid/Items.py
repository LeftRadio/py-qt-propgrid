import sys

from TreeModel import *
Config_Objects = []
from python_qt_binding.QtCore import QObject



class Config_CheckBox(Config_Base):
    def __init__(self, *args, **kwargs):
        Config_Base.__init__(self, args, kwargs)
        col = TreeColumn(' ')
        col.selectable = True
        col.enabled = True
        col.checkable = True

        self.columns.append(col)
        self.value = False

    @property
    def value(self):
        return self.columns[1].checked
    @value.setter
    def value(self,value):
        print value
        self.columns[1].checked = value
class Config_Double(Config_Base):
    def __init__(self, *args, **kwargs):
        Config_Base.__init__(self,args,kwargs)
        self.min = -sys.float_info.max
        self.max =  sys.float_info.max
        
        box = TreeSpinBoxDoubleColumn(self)
        box.min = self.min
        box.max = self.max
        self.columns.append(box)
        self.value = 0



class Config_Integer(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'Integer',  'min':- sys.maxint,'max': sys.maxint,'name':'--integer', 'long':'--integer={0}', 'short':'', 'value':0})
    def setupTreeItem(self):
        box = TreeSpinBoxColumn(self)
        if('min' in self.json):
            box.min = self.json['min']
        if('max' in self.json):
            box.max = self.json['max']
        self.columns.append(box)
        return self

class Config_String(Config_Base):
    def __init__(self, *args, **kwargs):
        Config_Base.__init__(self, args, kwargs)
        self.columns.append(TreeStringColumn(self))


class Config_Directory(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'Directory', 'name':'--directory directory', 'long':'--directory={0}'})
    def setupTreeItem(self):
        self.columns.append(TreeDirectoryPickerColumn(self))
        return self

class Config_File(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'File', 'name':'--file file', 'long':'--file={0}'})
    def setupTreeItem(self):
        self.columns.append(TreeFilePickerColumn(self))
        return self
        
class Config_ComboBox(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)        
        self.updateJSON({'gui_type':'ComboBox', 'name':'--select=value', 'long':'bool={0}', 'short':'bool={0}', 'tooltip':'', 'value':'True', 'options':['True', 'False']})
        self.cb = TreeComboBoxColumn(self )
        self.connect(self, SIGNAL('options_changed'), self.change_options)
    def setupTreeItem(self):
        cb = TreeComboBoxColumn(self )
        self.columns.append(cb)
        return self
    def change_options(self):
        self.columns[1].options = self.json['options']

class Config_Bool(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'Bool','value':True,  'name':'--bool=', 'options':['True', 'False']})
        #self.cb = TreeBoolColumn(self )
    def setupTreeItem(self):
        self.columns.append(TreeBoolColumn(self))
        return self

class Config_StringList(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'StringList', 'name':'--select=value', 'long':'strings={0}', 'short':'strings={0}', 'tooltip':'', 'value':['True', 'False']})
    def setupTreeItem(self):
        self.columns.append(TreeStringListColumn(self))
        return self

def loadItems():
    import sys, inspect
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    parameters = {}
    for c in classes:
        if c[1].__bases__:
            if c[1].__bases__[0].__name__ == "Config_Base":
                parameters[c[0]] = c[1]
    return parameters
        #print inspect.getclasstree(c[0])
        
def JsonToObject(items, json):
        name = 'Config_' + json['gui_type']
        item = items[name]()
        item.updateJSON(json)
        return item
        
