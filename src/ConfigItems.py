import sys

from TreeModel import *
Config_Objects = []

class TreeColumn():
    def __init__(self, value):
        
        self.checkable = False
        self.checkstate = Qt.Unchecked
        self.value = value
        self.index = None
        self.tooltip = ''
        """
        Returns the item flags for the given index.
        The base class implementation returns a combination of flags that enables the item (ItemIsEnabled) and allows it to be selected (ItemIsSelectable).
        Qt.NoItemFlags                  0	It does not have any properties set.
        Qt.ItemIsSelectable	          1	It can be selected.
        Qt.ItemIsEditable	              2	It can be edited.
        Qt.ItemIsDragEnabled	      4	It can be dragged.
        Qt.ItemIsDropEnabled	      8	It can be used as a drop target.
        Qt.ItemIsUserCheckable   16	It can be checked or unchecked by the user.
        Qt.ItemIsEnabled	            32	The user can interact with the item.
        Qt.ItemIsTristate              64	The item is checkable with three separate states.
        """
        self.flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        

class Config_Group(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.children = []
        self.updateJSON({'gui_type':'Group', 'name':'group', 'members':[], 'tooltip':'description'})
    def updateJSON(self, json):
        Config_Base.updateJSON(self, json)
        if 'members' in json:
            self.children = []
            items = loadItems()
            for mem in self.json['members']:
                obj = JsonToObject(items,  mem) 
                obj.parent = self
                self.children.append(obj)
    def toHtml(self):
        html = """<div class="param">
        <h2>%s</h2>
        <div class="param_descrip param_group">%s</div>
        <div class="param_Group_members">
        """ % (self.json['name'], self.json['tooltip'])
        for obj in self.children:
            html += obj.toHtml()
        html += "</div></div>"
        return html
    def setupTreeItem(self):
        #Todo figure this out...
        #for child_item in self.children:
         #   #TODO Change this
         #   gui_obj = child_item.getTreeItem(item)
        col = TreeColumn(' ')
        col.flags = Qt.ItemIsSelectable
        col.value = ' '
        self.columns.append(col)
        
        return self

class Config_CheckBox(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'CheckBox', 'name':'--checkbox', 'long':'--checkbox', 'short':'',  'tooltip':'description'} )   
    def setupTreeItem(self):
        col = TreeColumn(' ')
        col.flags = Qt.ItemIsSelectable
        col.value = ' '
        self.columns.append(col)
        return self

class Config_Double(Config_Base):
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'Double', 'min':-sys.float_info.max,'max':sys.float_info.max,'name':'--double', 'long':'--double={0}', 'short':'',  'value':0})
    def setupTreeItem(self):
            box = TreeSpinBoxDoubleColumn(self)
            if('min' in self.json):
                box.min = self.json['min']
            if('max' in self.json):
                box.max = self.json['max']
            self.columns.append(box)
            return self

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
    def __init__(self):
        Config_Base.__init__(self)
        self.updateJSON({'gui_type':'String', 'name':'--string', 'long':'--string={0}', 'short':'', 'value':'input', 'tooltip':'description'})
    def setupTreeItem(self):
        self.columns.append(TreeStringColumn(self))
        return self

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
        
