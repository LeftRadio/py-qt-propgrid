import sys
from PyQt4.QtCore import Qt, SIGNAL, QObject, QString
import PyQt4.QtGui as QtGui

from TreeModel import *
Config_Objects = []
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
from Ui_editor import Ui_Dialog

class Dialog_Editor(QDialog, Ui_Dialog):
    changed = pyqtSignal()
    type_changed = pyqtSignal(str)
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.Settings = ConfigTreeModel(self)
        #Setup the interface configuration parameters

        self.treeView.model = self.Settings 
        self.treeView.setModel(self.Settings )
        self.delagate = ItemDelegate(self)
        self.treeView.setItemDelegate(self.delagate)
        self.treeView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        
        self.Settings.dataChanged.connect(self.param_changed)
        self.delagate.closeEditor.connect(self.param_changed)
        self.supported_types = []
        self.data = {'gui_type':'group'}
        self.command = ConfigCommand()
        #self.Settings.
    def set_types(self, types):
        types
        self.types = []
        for k, v in types.iteritems():
            self.types.append(k[7:])
            self.cb_guitype.addItem(k[7:])
    def param_changed(self):
        json = self.GetData()
        self.obj.updateJSON(json)
        self.changed.emit()
    def GetData(self):
        data = self.Settings.getConfigArray()
        result = {}
        for item in data:
            result[item['name']] = item['value']
        return result
    def SetData(self, data):
        self.obj = data
        self.data = data.json
        skips = ( 'gui_type', 'members', 'value')
        index = self.types.index(data.json['gui_type'])
        self.cb_guitype.setCurrentIndex(index)
        items = []
        
        for key  in data.json:
            if key in skips:
                continue
            
            val = data.json[key]
            
            if type(val) is str:
                t = 'String'
            elif type(val) is int:
                t = 'Integer'
            elif type(val) is float:
                t = 'Double'
            elif type(val) is bool:
                t = 'Bool'
            elif type(val) is list:
                t = 'StringList'
            else:
                t = 'String'
            
            a = {'gui_type':t,  'name':key, 'value':val, 'required':True}

            items.append(a)
        self.command.load_json(items)
        self.Settings.setConfigData(self.command)
        self.treeView.resizeColumnToContents(0)  
    
    @pyqtSignature("QString")
    def on_cb_guitype_textChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("QString")
    def on_cb_guitype_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        
        if p0 != self.data['gui_type']:
            self.type_changed.emit(p0)


        
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
        
        
from PyQt4.QtGui   import QTreeView
from TreeModel import ItemDelegate,  TreeModel

class ConfigTreeModel(TreeModel):
    """When subclassing QAbstractItemModel, at the very least you must implement index(), parent(), rowCount(), columnCount(), and data(). 
    These functions are used in all read-only models, and form the basis of editable models."""
    def __init__(self, parent = None):
        TreeModel.__init__(self, parent)
        self.top = Config_Base(None)
        self.top.updateJSON({'name':'top'})
        self.config_data = None
        self.supported_types = loadItems()
        
        #Todo populate supported_types
    def getSupportedTypes(self):
        return self.supported_types
    def setConfigData(self, objects, parent=None):
        if parent == None:
            self.clear()
            self.command = objects
            #self.top.children = objects.children
            #self.top.children = objects.children
            parent = self.top
            #parent.children = objects.children
            
        for obj in objects.children:
            index = self.addConfigItem(obj, parent)
            #self.setConfigData(obj, index)
        
        self.layoutChanged.emit()
        self.emit(SIGNAL("layoutChanged()"))
                
    def ModifyParamter(self, index, obj):
        #Obtain pointer, and row / column count of current selected_index
        row = index.row()
        parent = index.parent().internalPointer()
        p = index.parent()
        if parent == None:
            parent = self.top
        #Remove current selected index
        self.removeRow(row, index.parent())

        # Add parameter at end
        index = self.addConfigItem(obj,parent)
        #Move to new position
        #parent.moveChild(row)
        from_row = self.rowCount(p) -1
        self.moveRows(  p,  from_row, from_row ,p,row)
        #self.layoutChanged.emit()
        return self.index(row,0, p )
        
    def addConfigItem(self, item,  parent):
        if(parent == None):
            parent = self.top
        #TODO Get item
        
        if item in parent.children:
            pass
        else:
            parent.children.append(item)
            
        gui_item = item.getTreeItem(parent)
        
        self.layoutChanged.emit()
        
        row = parent.childIndex(gui_item)
        index = self.index(row, 0, parent)
        
        return index
    def getConfigArray(self, parent=None):
        config = []
        if(parent == None):
            parent = self.top

        for item in parent.children:
            #TODO This needs to be done a different way  A group could have a value, and children
            if(item.json['gui_type']== 'Group'): 
                item.json['members'] = self.getConfigArray(item)
            """
            elif(len(item.columns) <= 1):
                item.obj.json['value'] = ''
            else:
                item.obj.set_value(item.columns[1].value)
                
            if item.obj.json['gui_type'] == 'Group':
                item.obj.json['checked'] = False
            elif item.columns[0].checkable == False:
                item.obj.json['checked'] = True
            elif   (item.columns[0].checkstate != Qt.Unchecked):
                item.obj.json['checked'] = True
            else:
                item.obj.json['checked'] = False
            """
            config.append(item.json)
        return config
        
class ConfigCommand(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.children = []
        self.active_members = []
        self.format = 'long'
        self.command_text = ''
        self.last_index =  0.0
        self.html = ''
    def load_json(self, jsons):
        #TODO delete objects.
        self.children = []
        types = loadItems()
        for json in jsons:
            obj = JsonToObject(types, json)
            #self.add_item(obj)
            self.children.append(obj)

        self.build_active()
        self.connect_signals()
        self.build_indexs()
        self.emit(SIGNAL('RESET'))
    def get_html(self):
        return self.html
    def delete_item(self, item, parent):
        if parent == None:
            parent = self
        if item in parent.children:
            parent.children.remove(item)
        if item in self.active_members:
            self.active_members.remove(item)
            self.rebuild_command()
    def add_item(self, obj, parent=None):
        #obj.num_index = 0 #TODO.
        if obj.num_index == -1:
            obj.num_index = self.last_index
        if parent == None:
            parent = self

        if  obj in parent.children:
            self.build_indexs()
            return
        parent.children.append(obj)
        self.build_indexs()
        
        self.connect_signals(obj.children)
        self.connect(obj, SIGNAL('checked_changed'), self.check_changed)
        #Objects value changes.
        self.connect(obj, SIGNAL('value_changed'), self.param_changed)
        
        #Todo figure out how to fix this correctly
        
        
                
        if obj.json['checked']:
            self.active_members.append(obj)
            self.param_changed(obj)
            
        self.build_active(obj.children)
        
    def build_indexs(self, objects=None):
        if objects == None:
            objects = self.children
            self.last_index = 0.0
        for obj in objects:
            obj.num_index = self.last_index
            self.last_index += 1
            self.build_indexs(obj.children)

        
    def connect_signals(self, objects=None):
        if objects == None:
            objects = self.children
        for obj in objects:
            #Object is checked / unchecked.
            self.connect(obj, SIGNAL('checked_changed'), self.check_changed)
            #Objects value changes.
            self.connect(obj, SIGNAL('value_changed'), self.param_changed)
            self.connect_signals(obj.children)

    def build_active(self, objects=None):
        if objects == None:
            objects = self.children
            self.active_members = []
        for obj in objects:
            if obj.json['checked']:
                self.active_members.append(obj)
                self.param_changed(obj)
            self.build_active(obj.children)
            
    def check_changed(self, emit=True):
        obj = self.sender()
        if obj.json['checked'] and obj in self.active_members: #Object already exists
            return
        elif obj.json['checked']:
            self.active_members.append(obj) #Mabye insert this into the middle?
            #Kind of lame, but sorting a sorted list should be fast.
            self.active_members = sorted(self.active_members, key=lambda obj: obj.num_index)
            self.param_changed(obj, rebuild=False) #Update the object text, causes rebuild_command to be called.
        elif obj in self.active_members and not obj.json['checked']:
            self.active_members.remove(obj) #remove the object
        if emit:
            self.rebuild_command() #Rebuild the command.
            
    def set_format(self, format):
        self.format = format
        
        for obj in self.active_members:
            self.param_changed(obj, rebuild=False)
            
        self.rebuild_command()
    def rebuild_command(self):
        self.command_text = ''
        for obj in self.active_members:
            self.command_text += ' ' + obj.text
        self.emit(SIGNAL('command_changed'), self.command_text)
    def param_changed(self, obj=None, rebuild=True):
        if(obj == None):
            obj = self.sender()
            
        #Grab the text for later.
        obj.text = obj.toCommandLine(self.format)
        
        #If the parameter changes then we want to check the object.
        obj.set_checked(True)
        
        if rebuild:
            if obj in self.active_members:
                self.rebuild_command()
        
    def get_command_text(self, format):
        text = ''
        for obj in self.active_members:
            text += ' ' +  obj.toCommandLine(self.format)
        return text
    def get_json(self):
        json = []
        for obj in self.children:
            json.append(obj.json)
        return json

class ConfigGridTreeView(QTreeView):
    def __init__(self, parent=None):
        super(QTreeView, self).__init__(parent)
        self.selected_index = None
        self.ConfigHeader = ConfigTreeModel(None)
        self.setModel(self.ConfigHeader)
        self.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.delagate = ItemDelegate(self)
        self.setItemDelegate(self.delagate)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.setAlternatingRowColors(True)
        style = """
        QTreeView {
                background-color: #EAF5FF;
                alternate-background-color: #D5EAFF;
        }
        QTreeView::item {
              border: 1px solid #d9d9d9;
             border-top-color: transparent;
             border-bottom-color: transparent;
        }
        QTreeView::item:hover {
             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
             border: 1px solid #bfcde4;
         }
         QTreeView::item:selected {
             border: 1px solid #567dbc;
         }
         QTreeView::item:selected:active{
             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
         }
         QTreeView::item:selected:!active {
             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
         }


        """
        self.setStyleSheet(style)
        #self.delagate.closeEditor.connect(self.param_changed)
        self.ConfigHeader.dataChanged.connect(self.param_changed)

        self.pressed.connect( self.presseda)
        
        self.data = None
        self.supported_types = loadItems()
        
        self.menu_Enabled = True
        self.convert_actions = []
        
        self.menuAddItem = QtGui.QMenu(self)
        self.menuAddItem.setTitle(QtGui.QApplication.translate("Right CLick", "Add Item..", None, QApplication.UnicodeUTF8))
        self.menuAddItem.setObjectName(_fromUtf8("menuAddItem"))
        
        self.menuConvertTo = QtGui.QMenu(self)
        self.menuConvertTo.setTitle(QtGui.QApplication.translate("Right CLick", "Convert To..", None, QApplication.UnicodeUTF8))
        self.menuConvertTo.setObjectName(_fromUtf8("menuConvertTo"))
        
        self.menuAddItem = QtGui.QMenu(self)
        self.menuAddItem.setTitle(QtGui.QApplication.translate("Right CLick", "Add Item..", None, QApplication.UnicodeUTF8))
        self.menuAddItem.setObjectName(_fromUtf8("menuAddItem"))
        
        types = loadItems()
        
        #Set up drag and drop stuff...
        self.dragEnabled() 
        self.acceptDrops() 
        self.showDropIndicator() 
        self.setDragDropMode(QAbstractItemView.InternalMove) 
        
        for type, val in types.items():
            name = val().json['gui_type']
            
            act = QtGui.QAction(self)
            act.my_type = val
            act.setText(QtGui.QApplication.translate("MainWindow", name, None, QtGui.QApplication.UnicodeUTF8))
            act.setObjectName(_fromUtf8("actionConvertTo" + name))
            act.triggered.connect(self.convert_to)
            self.menuConvertTo.addAction(act)

        self.type_names = []
        self.type_definitions = {}
        for type, val in types.items():
            name = val().json['gui_type']
            
            self.type_names.append(name)
            self.type_definitions[name] = val
            act = QtGui.QAction(self)
            act.my_type = type
            act.setText(QtGui.QApplication.translate("MainWindow", name, None, QtGui.QApplication.UnicodeUTF8))
            act.setObjectName(_fromUtf8("actionAddItem" + name))
            act.triggered.connect(self.add_param)
            self.menuAddItem.addAction(act)
            
        self.actionDelete_Item = QtGui.QAction(self)
        self.actionDelete_Item.setText('Delete Item')
        self.actionDelete_Item.triggered.connect(self.delete_item)
                
                
        self.editor = Dialog_Editor(self)
        self.editor.changed.connect(self.editor_changed)
        self.editor.type_changed.connect(self.editor_convert_to)
        self.editor.set_types(self.ConfigHeader.supported_types)
        self.editor.supported_types = loadItems()

        self.actionEdit_Item = QtGui.QAction(self)
        self.actionEdit_Item.setText('Edit Item')
        self.actionEdit_Item.triggered.connect(self.edit_item)
        
       
    def editor_changed(self):
        pass
    def editor_convert_to(self, type):
        if self.selected_index == None:
            return
        item = self.selected_index.internalPointer()
        if item.json['gui_type'] == type:
            return
        obj = self.supported_types['Config_' + str(type)]()
        self.convert_to_type(obj.json.copy())


    def edit_item(self):
        self.editor.show()
    def delete_item(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        parent = self.selected_index.parent()
        item = self.selected_index.internalPointer()
        row = self.selected_index.row()
        count = 0
        if (item.json['gui_type'] == 'Group' and len(item.children) > 0):

            reply = QtGui.QMessageBox.question(self, 'Message', "Do you want to keep the groups children?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        
            if reply == QtGui.QMessageBox.Yes:
                count = item.rowCount()
                self.ConfigHeader.moveRows(self.selected_index,  0, count-1 , parent, row+1)
            
        self.ConfigHeader.removeRow(row , parent)
        self.command.delete_item(item, parent.internalPointer())
        top_left          = self.ConfigHeader.index( row, 0, parent)
        bottom_right = self.ConfigHeader.index(row+count, parent)
        
        self.selected_index = None
    def convert_to(self):
        sender = self.sender()
        data = sender.my_type().json.copy()
        data['checked'] = self.selected_index.internalPointer().columns[0].checkstate == Qt.Checked
        self.convert_to_type(data)
        
    def convert_to_type(self, new_type):
        con     = self.selected_index.internalPointer().json
        old_obj = self.selected_index.internalPointer()
        parent = self.selected_index.internalPointer().parent
        num_index = self.selected_index.internalPointer().num_index
        try:#Attempt to hold the old value
            con['value'] = type(new_type['value'])(con['value'])
        except:
            con['value'] = new_type['value']
        
        for key in con:
            if key == 'gui_type':
                continue
            new_type[key] = con[key]
        
        obj = self.supported_types['Config_' + new_type['gui_type']]()
        obj.updateJSON(new_type)
        
        #Obtain pointer, and row / column count of current selected_index
        row = self.selected_index.row()
        p = self.selected_index.parent()
        
        
        #Remove current selected index
        self.ConfigHeader.removeRow(row , self.selected_index.parent())

        # Add parameter at end
        obj.num_index = num_index
        self.command.delete_item(old_obj, p.internalPointer())
        self.command.add_item(obj, parent)
        self.ConfigHeader.addConfigItem(obj,parent)
        #Move to new position
        parent.moveChild(row)
        self.command.build_indexs() #TODO ...
        self.set_selected_index(self.ConfigHeader.index(row, 0, p))
        
        #self.editor.SetData(self.selected_index.internalPointer() )
        #self.editor.index = self.selected_index
    def set_selected_index(self, index):
        if index == self.selected_index:
            return
        self.selected_index = index
        self.editor.SetData(index.internalPointer())
        self.emit(SIGNAL('argument_selected'), index)
        

    def add_param(self, a):
        sender = self.sender()

        x  = self.supported_types[sender.my_type]()
        parent = self.selected_index
        
        if(parent == None):
            self.command.add_item(x, None)
            self.ConfigHeader.addConfigItem(x,None)
            
            self.resizeColumnToContents(0)  
            return

        val = parent.internalPointer()
        
        if(val.json['gui_type'] != 'Group'):
            val = val.parent
        start_col = self.ConfigHeader.top.getMaxColumnCount()
        self.command.add_item(x, val)
        self.ConfigHeader.addConfigItem(x,val)
        end_col =  self.ConfigHeader.top.getMaxColumnCount()
        if start_col != end_col:
            self.tv_arguments.resizeColumnToContents(0) 
 
    def presseda(self, index):
            #self.selected_index = index
        item = index.internalPointer()
        #print index
        #Doc 2.0 editor / viewer...
        self.set_selected_index(index)

    def mousePressEvent(self, event):
        val = super(ConfigGridTreeView, self).mousePressEvent(event)
        #print self.selectedIndexes()
        index = self.selectedIndexes()

        if len(index) > 0:
            index = index[0]
            self.selected_index = index
            self.editor.SetData(self.selected_index.internalPointer() )
            #print self.selected_index
        else:
            index = None

        #index = self.selected_index
        buttons = QApplication.mouseButtons()
        if buttons == Qt.RightButton:

            if(self.selected_index == None):
                #todo select an item if possible
                pass
                
            #self.tv_arguments.mousePressEventB(event)
            self.param_right_clicked(self.selected_index)
       
        return val

    def param_right_clicked(self, index):
        buttons = QApplication.mouseButtons()
        self.selected_index = index #Store the selected_index for future use...
        if buttons == Qt.RightButton:
            menu = QMenu(self)
            #action editor...
            actions = [self.menuAddItem.menuAction(),self.menuConvertTo.menuAction() , self.actionEdit_Item, self.actionDelete_Item ]
            #actionDeleteItem
            if index == None:
                actions.pop(1)
                actions.pop(1)
                actions.pop(1)
            for act in actions:
                menu.addAction(act)    
            menu.exec_(QCursor.pos())
    def set_command(self, command):
        #TODO delete objects.
        self.command = command
        self.ConfigHeader.setConfigData(self.command)
        #TODO Setup a bunch of signal connections.

    def set_config(self, config, data=None):
        print "TODO Replace with load_json"
        self.load_json(config)
        return
    def param_changed(self, index_a,  index_b):
        #print index_a
        #print index_b
        if index_a == index_b:
            a=  index_a.internalPointer()
            #b= index_a.internalPointer().obj
            #c= index_a.internalPointer().obj.json            
            #print c
        else:
            pass
            #print index_a.obj


def JsonToObject(items, json):
        name = 'Config_' + json['gui_type']
        item = items[name]()
        item.updateJSON(json)
        return item
        
if __name__ == "__main__":
    items = loadItems()
    item = JsonToObject(items, {'gui_type':'CheckBox'})

    from PyQt4.QtCore import *
    from PyQt4.QtGui   import *
    import PyQt4.QtGui as QtGui
    app = QtGui.QApplication([])
    a = ConfigGridTreeView(None)
    command = ConfigCommand()
    #items = [{'gui_type':'Group', 'name':'Test1', 'members':[{'gui_type':'Group', 'name':'test2'}, {'name':'blah','gui_type':'CheckBox'}]}, {'gui_type':'String'},{'gui_type':'Group', 'name':'Test', 'members':[{'name':'blah','gui_type':'CheckBox'}]}, {'gui_type':'String'}]
    items = [{'gui_type':'Bool', 'name':'aBool', 'value':True}, {'gui_type':'Group', 'name':'Test1', 'members':[ {'gui_type':'ComboBox', 'name':'test3', 'options':['yes', 'no', 'maybe'],'value':'blah'}]}, {'gui_type':'String', 'name':'test3', 'value':'blah2'}]
    items = [ {'gui_type':'Group', 'name':'Test1', 'members':[ {'gui_type':'ComboBox', 'name':'test3', 'options':['yes', 'no', 'maybe'],'value':'blah'}]}]
    command.load_json(items)
    a.set_command(command)

    a.show()
    app.exec_()
