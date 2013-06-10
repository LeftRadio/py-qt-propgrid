from PyQt4.QtCore import *
import sys
import PyQt4.QtGui

from PyQt4.QtGui import (QStyledItemDelegate,  QItemDelegate, QLineEdit)
#TODO Make this work so that a child can belong to many parents....
from PyQt4.QtGui import *
class ObjectStringBox( QTextEdit):
    def __init__(self, parent=None):
        super(QTextEdit, self).__init__(parent)

        self.setFixedHeight(1 * QFontMetrics(self.font()).lineSpacing() + 10 + 20)
        self.setLineWrapMode(QTextEdit.NoWrap)
    def text(self):
        return self.toPlainText()
    def setObjects(self, objects, short_long):
        self.objects = objects
        self.len = len(objects)
        self.text_positions = []
        text = self.get_console_line(self.objects, short_long)
        
        self.setText(text)
    def get_console_line(self, settings, short_long):
        line = ''

        if short_long:
            primary = 'short'
            redundant = 'long'
        else:
            primary = 'long'
            redundant = 'short'
        last_position = 0
        for mem in settings:
            line = line.strip()
            id = primary
            if mem[id] == "":
                id = redundant
            text = ' ' + mem[id].format( mem['value'])
            position = {'start':last_position, 'end':last_position+len(text)}
            self.text_positions.append(position)
            line += text
        return line
        #def keyPressEvent (self, event):
        #print event
        #print event.text()
        #print self.cursorPosition()
#Todo somehow make this better....
class ItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)
        self.orig_editorEvent = super(ItemDelegate, self).editorEvent
        self.orig_eventFilter = super(ItemDelegate, self).eventFilter
    def paint(self,  painter, option, index):
        ok = True #
        if not index.isValid():
            ok = False
        buttons = QApplication.mouseButtons()
        if buttons == Qt.RightButton:
            ok = False
        if ok:
            item = index.internalPointer()
            col = index.column()
        if ok and hasattr(item.columns[col], 'paint'):
            pass
        else:
            ok = False
        #Check for appropiate function
        if ok:
            item.columns[col].paint(painter, option, index)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
    def setModelData(self, editor, model, index):
        ok = True #
        if not index.isValid():
            ok = False

        if ok:
            item = index.internalPointer()
            col = index.column()
        if ok and hasattr(item.columns[col], 'setModelData'):
            pass
        else:
            ok = False
        #Check for appropiate function
        if ok:
            return item.columns[col].setModelData(editor, model, index)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)
    def setEditorData(self, editor, index):
        ok = True #
        if not index.isValid():
            ok = False

        if ok:
            item = index.internalPointer()
            col = index.column()
        if ok and hasattr(item.columns[col], 'setEditorData'):
            pass
        else:
            ok = False
        #Check for appropiate function
        if ok:
            return item.columns[col].setEditorData(editor, index)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)
    def createEditor(self, parent, option, index):
        ok = True #
        
        buttons = QApplication.mouseButtons()
        if buttons == Qt.RightButton:
            return None
        if not index.isValid():
            ok = False
        if ok:
            item = index.internalPointer()
            col = index.column()
        if ok and hasattr(item.columns[col], 'createEditor'):
                pass
        else:
            ok = False

        #Check for appropiate function
        if ok:
            self.editor = item.columns[col].createEditor( parent, option, index)
        else:
            self.editor = QStyledItemDelegate.createEditor(self, parent, option, index)
        return  self.editor
    def sizeHint(self, option, index):
        ok = False #
        if not index.isValid():
            ok = False
        if ok == True:
            item = index.internalPointer()
        #Check for appropiate function
        if ok == True:
            pass
        else:
            return QStyledItemDelegate.sizeHint(self, option, index)
    def editorEvent(self,  event, model, option, index):
        ok = True #
        if not index.isValid():
            ok = False
        if ok == True:
            item = index.internalPointer()
            col = index.column()
        if ok and hasattr(item.columns[col], 'editorEvent'):
            return item.columns[col].editorEvent(event, model, option, index, self)
        else:
            return self.orig_editorEvent(event, model, option, index)
    def eventFilter ( self, editor, event ):

        if hasattr(editor, 'eventFilter_overide'):
            result = editor.eventFilter_overide(event, self.orig_eventFilter)
            if result == True:
                self.commitData.emit(editor);
                self.closeEditor.emit(editor, QStyledItemDelegate.NoHint);
            return result
        return self.orig_eventFilter(editor, event)
class TreeColumn(QObject):
    def __init__(self, value):
        QObject.__init__(self)
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
        

class Config_Base(QObject):
    """Base Config Item."""
    def __init__(self, parent=None):
        QObject.__init__(self)
        self.json = {'gui_type':'Base', 'name':'base', 'tooltip':'', 'long':'','short':'','required':False, 'checked':False, 'value':''}
        self.columns = [TreeColumn(self.json['name'])]
        """        
        Qt.ItemIsDragEnabled	      4	It can be dragged.
        Qt.ItemIsDropEnabled	      8	It can be used as a drop target.
        """
        self.columns[0].flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled  
        self.parent = parent
        self.children = []
        self.setup = False
        self.num_index = -1
        #If parent exists then we add ourself to the parent
        if(not parent == None):
            self.parent.addChild(self)
    def updateJSON(self, json):

        for k, v in json.iteritems():
            if v == None:
                continue
            self.json[k] = v
            self.emit(SIGNAL(k + '_changed'))
            if k == 'name':
                self.columns[0].value = v
                index = self.columns[0].index
                if self.columns[0].index != None:                    
                    index.model().dataChanged.emit(index, index)
            if k == 'value':
                if len(self.columns) > 1:
                    self.columns[1].value = v
        self.getTreeItem(self.parent)
    def set_value(self, value):
        if  self.json['value'] == value:
            return
        self.json['value'] = value
        if len(self.columns) > 1:
            self.columns[1].value = value
        self.emit(SIGNAL("value_changed"),)
    def set_checked(self, value):
        if self.json['checked'] == value:
            return
        self.json['checked'] = value
        map = {True:Qt.Checked, False:Qt.Unchecked}
        self.columns[0].checkstate = map[value]
        self.emit(SIGNAL('checked_changed'))
    def toCommandLine(self, format_key='long'):
        #Sometimes there isn't 2 keys.
        secondary_key = 'short'
        if(format_key == 'short'):
            secondary_key = 'long'

        if(self.json[format_key] == ''):
            format_key = secondary_key
        return self.json[format_key].format(self.json['value'])
    def getAnchorName(self):
        name = self.json['name']
        import string
        name = string.replace(str(name),'-', '_')
        name = "param_" + name
        return name
        
    def toHtml(self):
        html = """<div id="%s" class="param">
        <h3>%s</h3>
        <div  class="param_descrip">%s</div>
        </div>""" % (self.getAnchorName(), self.json['name'], self.json['tooltip'])
        return html
    def getTreeItem(self, parent):
        self.parent = parent
        #if self.setup:
            #return self
        self.setupTreeItem()
        self.finalizeTreeItem()
        self.setup = True
        return self
    def setupTreeItem(self):
        return self
    def finalizeTreeItem(self):
        if self.json.has_key('tooltip'):
            self.columns[0].tooltip = self.json['tooltip']
        if not self.json['gui_type']== 'Group':
            self.columns[0].checkable = True
            self.columns[0].flags |= Qt.ItemIsUserCheckable
        if self.json.has_key('checked'):
            if self.json['checked']:
                self.columns[0].checkstate = Qt.Checked
            else:
                self.columns[0].checkstate = Qt.Unchecked
        if self.json.has_key('required'):
            if self.json['required'] == True or self.json['required'] == 'True':
                self.columns[0].checkable = False
                self.checkstate = Qt.Checked
        return self
    
    def parent(self):
        #print self.parent
        if(self.parent == None):
            return QModelIndex()
        return self.parent
    def columnCount(self):
        return 2
        return len(self.columns)
    def children(self):
        return self.children
    def moveChild(self, new_index, old_index = -1):
        child = self.children.pop(old_index)
        self.children.insert(new_index, child)
        
    def addChild(self, child):
        if child in self.children:
            #print "Woopsie"
            return
        self.children.append(child)
        child.parent = self
    def childIndex(self, child):
        return self.children.index(child)
    def getMaxColumnCount(self):
        max = len(self.columns)
        for child in self.children:
            if(max < child.getMaxColumnCount()):
                max = child.getMaxColumnCount()
        return 2 #Todo
        return max
    def hasChildren(self):
        """hasChildren(self, parent)
        
        Returns true if the item corresponding to the parent index has
        child items; otherwise returns false.
        
        To begin with, we assume that all top-level items (packages) have
        children to reduce calls to the server. Once these items have been
        opened, more precise information will be provided by the rowCount()
        method.
        
        """
        return len(self.children) > 0

    def data(self, role, column):
        """const QModelIndex & index, int role = Qt.DisplayRole
        data ( const QModelIndex & index, int role = Qt.DisplayRole ) const [pure virtual]
        Returns the data stored under the given role for the item referred to by the index.
        Note: If you do not have a value to return, return an invalid QVariant instead of returning 0.
        Qt.DisplayRoles
        --------------------------------
        Qt.DisplayRole	        0	The key data to be rendered in the form of text. (QString)
        Qt.DecorationRole	1	The data to be rendered as a decoration in the form of an icon. (QColor, QIcon or QPixmap)
        Qt.EditRole	            2	The data in a form suitable for editing in an editor. (QString)
        Qt.ToolTipRole	        3	The data displayed in the item's tooltip. (QString)
        Qt.StatusTipRole	    4	The data displayed in the status bar. (QString)
        Qt.WhatsThisRole	    5	The data displayed for the item in "What's This?" mode. (QString)
        Qt.SizeHintRole	  13	The size hint for the item that will be supplied to views. (QSize)
        
        Roles describing appearance and meta data (with associated types):
        Qt.FontRole	6	The font used for items rendered with the default delegate. (QFont)
        Qt.TextAlignmentRole	7	The alignment of the text for items rendered with the default delegate. (Qt.AlignmentFlag)
        Qt.BackgroundRole	8	The background brush used for items rendered with the default delegate. (QBrush)
        Qt.BackgroundColorRole	8	This role is obsolete. Use BackgroundRole instead.
        Qt.ForegroundRole	9	The foreground brush (text color, typically) used for items rendered with the default delegate. (QBrush)
        Qt.TextColorRole	9	This role is obsolete. Use ForegroundRole instead.
        Qt.CheckStateRole	10	This role is used to obtain the checked state of an item. (Qt.CheckState)
            Qt.Unchecked	0	The item is unchecked.
            Qt.PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
            Qt.Checked	2	The item is checked.
        Accessibility roles (with associated types):
        Qt.AccessibleTextRole	11	The text to be used by accessibility extensions and plugins, such as screen readers. (QString)
        Qt.AccessibleDescriptionRole	12	A description of the item for accessibility purposes. (QString) 
        
        For user roles, it is up to the developer to decide which types to use and ensure that components use the correct types when accessing and setting data.
        """
        if role == Qt.DisplayRole:
            pass
        elif role == Qt.CheckStateRole:
            pass
        elif Qt.UserRole <= role < Qt.UnusedRole:
            pass
        elif role == Qt.ToolTipRole:
            pass
        else:
            return QVariant()
        if column >= len(self.columns):
            return QVariant()
        if role == Qt.DisplayRole:

            if self.columns[column].value == None:
                return QVariant()
            return QVariant(str(self.columns[column].value))
        elif (role == Qt.CheckStateRole) and (self.columns[column].checkable == True):
            return QVariant(self.columns[column].checkstate)
        elif role == Qt.ToolTipRole and not self.columns[column].tooltip == '':
            return QVariant(self.columns[column].tooltip)
        else:
            return QVariant()
        return QVariant()
        
    def rowCount(self):
        """rowCount(self, parent)
        
        Returns the number of rows containing child items corresponding to
        children of the given parent index.
        """
        return len(self.children)
    def setCheckstate(self, parent, column, value):
         
        if self.columns[column].checkstate == value: 
            return #Value is already the same don't reset, and possibly emit a 2nd event message..
        else:
            self.columns[column].checkstate = value
            
        if column == 0:
            self.json['checked'] = value == Qt.Checked
            self.emit(SIGNAL('checked_changed'))
        
        #If its a tristate checkbox, then set its children to the paren'ts value
        if self.columns[column].flags & Qt.ItemIsTristate and value.toInt()[0] !=  Qt.PartiallyChecked: 
            for item in self.children:
                    if(column < len(item.columns)):
                        item.setCheckstate(parent, column, value)
    def getSelectedItems(self, currentSelected=[]):
        if(self.columns[0].checkstate == Qt.Checked):
            currentSelected.append(self)
        for item in self.children: #Get all of the children's items
            currentSelected = item.getSelectedItems(currentSelected)
        return currentSelected

class TreeNoneColumn(TreeColumn):
    def __init__(self):
        TreeColumn.__init__(self, None)
        self.flags = 0
        import sys
        self.value = None
        self.flags |= Qt.ItemIsEditable

class TreeCheckboxColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        value = self.obj.json['value']

        TreeColumn.__init__(self, value)
        
        import sys
        try:
            self.value = bool(value)
        except:
            self.value = 0
        self.flags |= Qt.ItemIsEditable
    def setModelData(self, editor, model, index):
        #model.setData(index, QVariant(editor.value()))
        value = editor.checkState()
        self.value = value
        self.obj.set_value(value)
    def setEditorData(self, editor, index):
        editor.setCheckState(self.value)
    def setData(self, data, value):
        value = value == Qt.Checked
        self.value = value
        self.obj.set_value(value)

    def createEditor(self, parent, option, index):
        #TODO Cleanup this spinbox by subclassing it and extending textFromValue and valueFromText.
        #TODO Let it support hex numbers
        #TODO Let it support 3e-5
        #TODO Don't show a bazillion zeros to obtain full precision, thats just silly.
        #TODO Do the same thing for integers.
        checkbox =  PyQt4.QtGui .QCheckBox(parent)
        checkbox.setCheckState(self.value)
        self.editor = checkbox
        return checkbox
class TreeStringColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        value = self.obj.json['value']
        TreeColumn.__init__(self, value)
        self.value = str(value)
        self.flags |= Qt.ItemIsEditable
    def setModelData(self, editor, model, index):
        #model.setData(index, QVariant(editor.value()))
        value = str(editor.text())
        self.value = value
        self.obj.set_value(value)

    def setEditorData(self, editor, index):

        editor.setText(self.value)
    def setData(self, data, value):
        
        self.value = value
        self.obj.set_value(value)

class TreeStringListColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        value = self.obj.json['value']

        TreeColumn.__init__(self, value)
        self.value = value
        self.flags |= Qt.ItemIsEditable
    def setModelData(self, editor, model, index):
        #model.setData(index, QVariant(editor.value()))
        options = str(editor.text()).split(',')
        value = options
        self.value = value
        self.obj.set_value(value)

    def setEditorData(self, editor, index):
        txt = ''
        for val in self.value[:-1]:
            txt += str(val) + ','
        txt += self.value[-1]
        editor.setText(txt)
    def setData(self, data, value):
        self.value = value
        self.obj.set_value(value)

class TreeSpinBoxColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        try:
            self.value = int(obj.json['value'])
        except:
            self.value = 0

        TreeColumn.__init__(self, self.value)

        import sys
        self.min = -sys.maxint - 1
        self.max = sys.maxint

        self.flags |= Qt.ItemIsEditable
    def setModelData(self, editor, model, index):
        #model.setData(index, QVariant(editor.value()))
        value = editor.value()
        self.value = value
        self.obj.set_value(value)

    def setEditorData(self, editor, index):
        editor.setValue(self.value)
    def setData(self, data, value):
        value = int(value)
        self.value = value
        self.obj.set_value(value)

    def createEditor(self, parent, option, index):
        #TODO Cleanup this spinbox by subclassing it and extending textFromValue and valueFromText.
        #TODO Let it support hex numbers
        #TODO Let it support 3e-5
        #TODO Don't show a bazillion zeros to obtain full precision, thats just silly.
        #TODO Do the same thing for integers.
        
        spinbox =  PyQt4.QtGui .QSpinBox(parent)
        spinbox.setRange(self.min, self.max)
        spinbox.setValue(int(self.value))
        spinbox.setSingleStep(1)
        spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.editor = spinbox
        return spinbox
class TreeSpinBoxDoubleColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        value = self.obj.json['value']

        TreeColumn.__init__(self, value)
        import sys
        self.min = -sys.float_info.max
        self.max = sys.float_info.max
        self.value = value
        self.decimals = sys.float_info.max_10_exp + 15
        self.flags |= Qt.ItemIsEditable
    def setModelData(self, editor, model, index):
        #model.setData(index, QVariant(editor.value()))
        value = editor.value()
        self.value = value
        self.obj.set_value(value)

    def setEditorData(self, editor, index):
        editor.setValue(self.value)
    def setData(self, data, value):
        value = value
        self.value = value
        self.obj.set_value(value)

    def createEditor(self, parent, option, index):
        #TODO Cleanup this spinbox by subclassing it and extending textFromValue and valueFromText.
        #TODO Let it support hex numbers
        #TODO Let it support 3e-5
        #TODO Don't show a bazillion zeros to obtain full precision, thats just silly.
        #TODO Do the same thing for integers.
        
        spinbox =  PyQt4.QtGui .QDoubleSpinBox(parent)
        spinbox.setRange(self.min, self.max)
        spinbox.setValue(self.value)
        spinbox.setDecimals(self.decimals)
        spinbox.setSingleStep(1)
        spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.editor = spinbox
        return spinbox
#File Picker
#TODO Lots and lots of stuff
# Pick file
# Pick Directory
# Pick Files
# Pick Directories
# List selected files/directories in list
class FilePicker(PyQt4.QtGui.QWidget):
    def __init__(self, parent, obj):
        self.obj = obj
        value = self.obj.json['value']

        self.value = value
        self.is_in = False
        PyQt4.QtGui.QWidget.__init__(self, parent)
        
        self.line_edit = PyQt4.QtGui.QLineEdit(self)
        #self.line_edit.setReadOnly(True)
        line = ''
        if type(value) is list:
            for i in value:
                line += ' ' + i
        elif value == None:
            pass
        else:
            line = value
        self.line_edit.setText(line)
        self.line_edit.textChanged.connect(self.textChanged)
        self.line_edit.returnPressed.connect(self.returnPressed)
        self.tool_button = PyQt4.QtGui.QToolButton(self)
        self.tool_button.setText("...")
        
        #self.connect(self.tool_button, SIGNAL("clicked()"), self.button_clicked)
        #self.connect(self.line_edit, SIGNAL("clicked()"), self.button_clicked) 
        self.tool_button.clicked.connect(self.button_clicked)
        self.layout = PyQt4.QtGui.QHBoxLayout(self)
        
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.tool_button)
        
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.value = value
        self.dialog = PyQt4.QtGui.QFileDialog (self, "File Picker", ".", "all files (*)" )
        
        self.options = None
        self.fileMode = PyQt4.QtGui.QFileDialog.AnyFile
        self.acceptMode = PyQt4.QtGui.QFileDialog.AcceptOpen
        
        self.launched = False
        self.done_picking = False
        
    def textChanged(self, text):
        self.value = str(text)
    def returnPressed(self):
        self.done_picking = True
        self.emit(SIGNAL("valueChanged"))
        self.emit(SIGNAL("editingFinished"))
    def button_clicked(self):
        if not self.options == None:
            self.dialog.setOptions (self.options)
        self.dialog.setFileMode(self.fileMode)
        self.dialog.setAcceptMode(self.acceptMode)

        self.launched = True
        
        #Populate the dialog
        if self.fileMode &  PyQt4.QtGui.QFileDialog.Directory:
            self.dialog.setDirectory(self.value)

        elif self.fileMode & PyQt4.QtGui.QFileDialog.ExistingFiles:
            self.value = []
            for file in self.dialog.selectedFiles():
                self.value.append(str(file))
        elif (self.fileMode == PyQt4.QtGui.QFileDialog.ExistingFile)  or (self.fileMode == PyQt4.QtGui.QFileDialog.AnyFile):
            self.dialog.selectFile(self.value)
        #Display the dialg
        if (self.dialog.exec_()):
            if self.fileMode &  PyQt4.QtGui.QFileDialog.Directory:
                self.value = str(self.dialog.directory().path())
            elif self.fileMode & PyQt4.QtGui.QFileDialog.ExistingFiles:
                self.value = []
                for file in self.dialog.selectedFiles():
                    self.value.append(str(file))
            elif (self.fileMode == PyQt4.QtGui.QFileDialog.ExistingFile)  or (self.fileMode == PyQt4.QtGui.QFileDialog.AnyFile):
                self.value = self.dialog.selectedFiles()
                self.value = str(self.value[0]) #There is only 1 file name...
                
            self.emit(SIGNAL("valueChanged"))
            self.emit(SIGNAL("editingFinished"))
        #self.filelist = [PyQt4.QtGui.QFileDialog.getOpenFileName(self,"", ".")]
        #self.value= self.filelist[0]
        self.set_files(self.value)
        self.done_picking = True
    def set_files(self, file):
        self.value = file
        line  =''
        if type(self.value) == list:
            for f in file:
                line +=' ' + f 
        else:
            line = file
        self.line_edit.setText(line)
    def eventFilter_overide(self, event, parent_filter):
        if event.type() == QEvent.Enter:
            self.is_in = True
        elif event.type() == QEvent.Leave:
            self.is_in = False
        if self.done_picking == True:
            return True
        if self.launched == False and self.is_in == False:
            return parent_filter(self, event)
        return False
        
class TreeDirectoryPickerColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        value = self.obj.json['value']

        TreeColumn.__init__(self, value)
        self.flags |= Qt.ItemIsEditable
        self.filelist = value
        self.options = PyQt4.QtGui.QFileDialog.ShowDirsOnly
        self.fileMode = PyQt4.QtGui.QFileDialog.Directory
    def setModelData(self, editor, model, index):
        self.value = editor.value
        self.obj.set_value(self.value)
    def setEditorData(self, editor, index):
        editor.set_files(self.value)
        #i = editor.findData(QVariant(self.value))
        #editor.setCurrentIndex(i)
    def setData(self, data, value):
        self.value = str(value)
        
    def createEditor(self, parent, option, index):
        self.editor = FilePicker(parent, self.obj) 
        self.editor.fileMode = self.fileMode
        self.editor.options = self.options
        return self.editor

class TreeFilePickerColumn(TreeColumn):
    def __init__(self, obj):
        self.obj = obj
        value = self.obj.json['value']

        TreeColumn.__init__(self, value)
        self.flags |= Qt.ItemIsEditable
        self.filelist = self.setData(None, value)
    def setModelData(self, editor, model, index):
        self.value = editor.value
        self.obj.set_value(self.value)
    def setEditorData(self, editor, index):
        editor.set_files(self.value)
        editor.line_edit.setFocus()
        #i = editor.findData(QVariant(self.value))
        #editor.setCurrentIndex(i)
    def setData(self, data, value):
            self.value = value
    def createEditor(self, parent, option, index):
        self.editor = FilePicker(parent, self.obj) 
        return self.editor

class TreeBoolColumn(TreeColumn):
    def __init__(self,obj):
        self.obj = obj

        
        TreeColumn.__init__(self, obj.json['value'])
        self.json = obj.json
        self.flags |= Qt.ItemIsEditable
        self.type = str
        self.options = ['True', 'False']
    def editorEvent (self,  event, model, option, index, delagate ):
        item = index.internalPointer()
        col = index.column()
        col = item.columns[col]
        
        
        menu = PyQt4.QtGui.QMenu()
        i = 0
        selected = 0
        for value in self.options:
            action = QAction(value, menu)
            menu.addAction(action)
            if(str(item.json['value']) == value):
                selected = i
                menu.setActiveAction(action)
            i+=1

        pos = QCursor.pos()
        h = menu.sizeHint().height()
        item_height = h/len(self.options )
        adjust = int( item_height * selected + item_height/2.0)
        
        #+ (h/len(col.options))*.5)
        pos.setY(pos.y() - adjust)
        result = menu.exec_(pos)
        if result != None:
            
            col.value = self.type(result.text()) == 'True'
            item.set_value(col.value)
            
            model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            model.dataChanged.emit(index, index)
            
            delagate.closeEditor.emit(None,   QAbstractItemDelegate.NoHint)
            #model.delagate.emit(SIGNAL("closeEditor(QWidget*,QAbstractItemDelegate::EndEditHint)"), menu,  QAbstractItemDelegate.NoHint)
        return True



class TreeComboBoxColumn(TreeColumn):
    def __init__(self,obj):
        self.obj = obj

        
        TreeColumn.__init__(self, obj.json['value'])
        self.json = obj.json
        self.flags |= Qt.ItemIsEditable
        self.type = str
        

    def editorEvent (self,  event, model, option, index, delagate ):
        item = index.internalPointer()
        col = index.column()
        col = item.columns[col]
        
        
        menu = PyQt4.QtGui.QMenu()
        i = 0
        selected = 0
        for value in self.options:
            action = QAction(value, menu)
            menu.addAction(action)
            if(str(item.json['value']) == value):
                selected = i
                menu.setActiveAction(action)
            i+=1

        pos = QCursor.pos()
        h = menu.sizeHint().height()
        item_height = h/len(self.options )
        adjust = int( item_height * selected + item_height/2.0)
        
        #+ (h/len(col.options))*.5)
        pos.setY(pos.y() - adjust)
        result = menu.exec_(pos)
        if result != None:
            
            col.value = self.type(result.text())
            item.set_value(col.value)
            
            model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            model.dataChanged.emit(index, index)
            
            delagate.closeEditor.emit(None,   QAbstractItemDelegate.NoHint)
            #model.delagate.emit(SIGNAL("closeEditor(QWidget*,QAbstractItemDelegate::EndEditHint)"), menu,  QAbstractItemDelegate.NoHint)
        return True

class TreeModel(QAbstractItemModel):
    """When subclassing QAbstractItemModel, at the very least you must implement index(), parent(), rowCount(), columnCount(), and data(). 
    These functions are used in all read-only models, and form the basis of editable models."""
    def __init__(self,  parent = None):
        QAbstractItemModel.__init__(self, parent)
        self.parent = parent
        self.clear()
        self.delagate = None #TODO...
        self.move_index = None
        self.top_index = None
        self.setSupportedDragActions(Qt.MoveAction)
    def supportedDropActions(self):
        return Qt.MoveAction
    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation != Qt.Horizontal:
            return QVariant()
        items = ['Parameter', 'Value']
        return QVariant(items[section])
    def clear(self):
        self.beginResetModel()
        self.top = Config_Base(None)
        self.top.updateJSON({'name':'Master Parent'})
        self.endResetModel()
    def moveRows(self,  sourceParent,  sourceFirst,  sourceLast, destinationParent, destinationChild ):
        count = sourceLast - sourceFirst
        if sourceParent == destinationParent:
            if( sourceFirst < destinationChild and destinationChild <= (sourceLast+1) ):
                return False
            if destinationChild < sourceFirst:
                pass
            if destinationChild > sourceFirst:
                # 1 2 3 4 5 6
                destinationChild = destinationChild - count
        #TODO Check to make sure destinationParent is not a child of sourceParent....
        
        source = sourceParent.internalPointer()
        dest = destinationParent.internalPointer()
        if dest == None:
            dest = self.top
        if source == None:
            source = self.top
        if not self.beginMoveRows (  sourceParent,  sourceFirst,  sourceLast, destinationParent, destinationChild ):
            return False
        
        ind =destinationChild
        for i in range(count+1):
            item = source.children.pop(sourceFirst)
            item.parent = dest
            dest.children.insert(ind, item)
            #dest.children.append(item)
            ind+=1
        
        self.endMoveRows()
        return True

    def mimeTypes(self):
        #print "HI"
        return ['application/index']

    def mimeData(self, indexes):

        self.move_index = indexes[0] #Store the selected index so we can move it.
        mimedata = QMimeData()
        #Not really needed, but maybe someone will do something with this....
        import json
        index = indexes[0].internalPointer()
        data = json.dumps(index.json)
        mimedata.setData('application/index', data)
        
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        if self.move_index == None:
            return False #Some sort of error...
        #print 'dropMimeData %s %s %s %s' % (data.data('application/index'), action, row, parent) 
        parent_index = parent.internalPointer()
        if parent_index == None:
            row = len(self.top.children)
            parent = QModelIndex()
        else:
            row = self.rowCount(parent)
            if parent_index.json['gui_type']  != 'Group':
                row = parent.row()
                parent = parent.parent()
            parent_dest = self.move_index.parent()
            
        #moveRows(  sourceParent,  sourceFirst,  sourceLast, destinationParent, destinationChild ):
        self.moveRows(  self.move_index.parent(),  self.move_index.row(),  self.move_index.row(), parent, row )
        self.move_index = None
        return False

    def removeRows(self, row, count, parent=QModelIndex()):
        if not hasattr(parent, 'isValid'):
            if hasattr(parent, 'children'):
                parent_item = parent #Looks like they directly passed the parent list in... this is bad..
            else:
                parent_item = self.top
        elif not parent.isValid(): 
            # Top-level items
            parent_item = self.top
        else:
            parent_item = parent.internalPointer()
        
        if (row+count-1) >= len(parent_item.children) or row < 0:
            return False
        self.beginRemoveRows(parent, row, row + count -1)
        for i in range(count):
            parent_item.children.pop(row)
        self.endRemoveRows () 
        return True
            
    def index(self, row, column, parent=QModelIndex()):
        """index( int row, int column, const QModelIndex & parent = QModelIndex() )
        Returns the index of the item in the model specified by the given row, column and parent index.
        When reimplementing this function in a subclass, call createIndex() to generate model indexes that
        other components can use to refer to items in your model.
        """
        if not hasattr(parent, 'isValid'):
            if hasattr(parent, 'children'):
                parent_item = parent #Looks like they directly passed the parent list in... this is bad..
            else:
                parent_item = self.top
        elif not parent.isValid(): 
            # Top-level items
            parent_item = self.top
        else:
            parent_item = parent.internalPointer()
        
        #elif not (parent_item is None )and column > (len(parent_item.columns)):
        #   print "-- %d %d" % ( column,  len(parent_item.columns))
        #    return QModelIndex()
        
        if row >= len(parent_item.children) or row < 0:
            return QModelIndex()
        if  column < 0 or len(parent_item.children[row].columns) <= column:
            return QModelIndex()

        #All columns indexes currently point to their row
        parent_item.children[row].columns[column].index = self.createIndex(row, column, parent_item.children[row])
        
        return parent_item.children[row].columns[column].index


    def parent(self, index):
        """parent(self, index)
            QModelIndex QAbstractItemModel::parent ( const QModelIndex & index ) const [pure virtual]
            Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned.
            A common convention used in models that expose tree data structures is that only items in the first column have children. 
            For that case, when reimplementing this function in a subclass the column of the returned QModelIndex would be 0.
            When reimplementing this function in a subclass, be careful to avoid calling QModelIndex member functions, such as QModelIndex::parent(), 
            since indexes belonging to your model will simply call your implementation, leading to infinite recursion.
        """
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if item == None:
            return QModelIndex()
        if not hasattr(item, 'parent'):
            parent = self.top
        else:
            parent = item.parent
        if parent == self.top:
            # Top-level packages have no parent.
            return QModelIndex()
        if parent == None: #TODO Y is this needed?
            return QModelIndex()
        elif parent.columns[0].index == None:
            return QModelIndex()
        else:
            return parent.columns[0].index
            pp = parent.parent
            row = pp.childIndex(parent)
            col = index.column()
            return parent.index
            return self.createIndex(row, col,parent)
        return QModelIndex()


    def hasChildren(self, index):
        """hasChildren(self, parent)
        
        Returns true if the item corresponding to the parent index has
        child items; otherwise returns false.
        
        To begin with, we assume that all top-level items (packages) have
        children to reduce calls to the server. Once these items have been
        opened, more precise information will be provided by the rowCount()
        method.
        
        """

        if not index.isValid():
            # Top-level items always have children...
            return True
        parent_item = index.internalPointer()
        return parent_item.hasChildren()

    def rowCount(self, index):
    
        """rowCount(self, parent)
        
        Returns the number of rows containing child items corresponding to
        children of the given parent index.
        """
        if not index.isValid():
            # Top-level items
            return len(self.top.children)
        return index.internalPointer().rowCount()

    def columnCount(self, parent):
    
        """columnCount(self, parent)
        
        Returns the number of columns in the model regardless of the number
        of columns containing items corresponding to children of the parent
        index.
        
        The number returned is based on the number of sections we want to
        expose to views.
        
        Returns the number of columns for the children of the given parent.
        In most subclasses, the number of columns is independent of the parent.
        Note: When implementing a table based model, columnCount() sh headers[row]['node']ould return 0 when the parent is valid.
        
        """

        if not parent.isValid():
            # Top-level items
            parent_item = self.top
            
        else:
            parent_item = parent.internalPointer()
        return 2
        return parent_item.getMaxColumnCount()
        
    def data(self, index, role):
        """const QModelIndex & index, int role = Qt.DisplayRole
            data ( const QModelIndex & index, int role = Qt.DisplayRole ) const [pure virtual]
            Returns the data stored under the given role for the item referred to by the index.
            Note: If you do not have a value to return, return an invalid QVariant instead of returning 0.
            Qt.DisplayRoles
            --------------------------------
            Qt.DisplayRole	        0	The key data to be rendered in the form of text. (QString)
            Qt.DecorationRole	1	The data to be rendered as a decoration in the form of an icon. (QColor, QIcon or QPixmap)
            Qt.EditRole	            2	The data in a form suitable for editing in an editor. (QString)
            Qt.ToolTipRole	        3	The data displayed in the item's tooltip. (QString)
            Qt.StatusTipRole	    4	The data displayed in the status bar. (QString)
            Qt.WhatsThisRole	    5	The data displayed for the item in "What's This?" mode. (QString)
            Qt.SizeHintRole	  13	The size hint for the item that will be supplied to views. (QSize)
            
            Roles describing appearance and meta data (with associated types):
            Qt.FontRole	6	The font used for items rendered with the default delegate. (QFont)
            Qt.TextAlignmentRole	7	The alignment of the text for items rendered with the default delegate. (Qt.AlignmentFlag)
            Qt.BackgroundRole	8	The background brush used for items rendered with the default delegate. (QBrush)
            Qt.BackgroundColorRole	8	This role is obsolete. Use BackgroundRole instead.
            Qt.ForegroundRole	9	The foreground brush (text color, typically) used for items rendered with the default delegate. (QBrush)
            Qt.TextColorRole	9	This role is obsolete. Use ForegroundRole instead.
            Qt.CheckStateRole	10	This role is used to obtain the checked state of an item. (Qt.CheckState)
                Qt.Unchecked	0	The item is unchecked.
                Qt.PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
                Qt.Checked	2	The item is checked.
            Accessibility roles (with associated types):
            Qt.AccessibleTextRole	11	The text to be used by accessibility extensions and plugins, such as screen readers. (QString)
            Qt.AccessibleDescriptionRole	12	A description of the item for accessibility purposes. (QString) 
            
            For user roles, it is up to the developer to decide which types to use and ensure that components use the correct types when accessing and setting data.
        """
        item = index.internalPointer()
        
        if item == None:
            return QVariant()
        
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        if not 0 <= row < self.rowCount(index.parent()):
            return QVariant()

        column = index.column()
        
        return item.data(role, column)

        
    def setData(self, index, value, role):
        """"
        bool QAbstractItemModel::setData ( const QModelIndex & index, const QVariant & value, int role = Qt::EditRole )   [virtual]
        Sets the role data for the item at index to value. Returns true if successful; otherwise returns false.
        The dataChanged() signal should be emitted if the data was successfully set.
        The base class implementation returns false. This function and data() must be reimplemented for editable models. Note that the dataChanged() signal must be emitted explicitly when reimplementing this function.
        See also Qt::ItemDataRole, data(), and itemData().
            Qt.DisplayRoles
            --------------------------------
            Qt.DisplayRole	        0	The key data to be rendered in the form of text. (QString)
            Qt.DecorationRole	    1	The data to be rendered as a decoration in the form of an icon. (QColor, QIcon or QPixmap)
            Qt.EditRole	            2	The data in a form suitable for editing in an editor. (QString)
            Qt.ToolTipRole	        3	The data displayed in the item's tooltip. (QString)
            Qt.StatusTipRole	    4	The data displayed in the status bar. (QString)
            Qt.WhatsThisRole	    5	The data displayed for the item in "What's This?" mode. (QString)
            Qt.SizeHintRole	  13	The size hint for the item that will be supplied to views. (QSize)
            
            Roles describing appearance and meta data (with associated types):
            Qt.FontRole	6	The font used for items rendered with the default delegate. (QFont)
            Qt.TextAlignmentRole	7	The alignment of the text for items rendered with the default delegate. (Qt.AlignmentFlag)
            Qt.BackgroundRole	8	The background brush used for items rendered with the default delegate. (QBrush)
            Qt.BackgroundColorRole	8	This role is obsolete. Use BackgroundRole instead.
            Qt.ForegroundRole	9	The foreground brush (text color, typically) used for items rendered with the default delegate. (QBrush)
            Qt.TextColorRole	9	This role is obsolete. Use ForegroundRole instead.
            Qt.CheckStateRole	10	This role is used to obtain the checked state of an item. (Qt.CheckState)
                Qt.Unchecked	0	The item is unchecked.
                Qt.PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
                Qt.Checked	2	The item is checked.
            Accessibility roles (with associated types):
            Qt.AccessibleTextRole	11	The text to be used by accessibility extensions and plugins, such as screen readers. (QString)
            Qt.AccessibleDescript)ionRole	12	A description of the item for accessibility purposes. (QString) 
            
            For user roles, it is up to the developer to decide which types to use and ensure that components use the correct types when accessing and setting data.
        """
        #obtain item
        if not index.isValid():
            return False
        else:
            item = index.internalPointer()
        column = index.column()


        
        #decide to continue or stop
        if role == Qt.CheckStateRole and item.columns[column].checkable == True:
            if value ==  Qt.PartiallyChecked and not (item.columns[column].flags & Qt.ItemIsTristate):
                return False
            pass
        elif role == Qt.CheckStateRole:
            pass
        elif not hasattr(item.columns[column], "setData"):
            result = item.columns[column].setData(value, role)
            item.obj.emit(SIGNAL('changed'), item.obj) #TODO...
            return result
        elif role == Qt.DisplayRole:
            return False
        #elif Qt.UserRole <= role < self.UnusedRole:
        #   pass
        else:
            return False
        #Switch on data
        if role == Qt.CheckStateRole:
            #Don't update if it stay's the same, avoids an inf recursion bull $. Jeepers
            
            if value == self.data(index, role):
                return False
            #Update this node and its children
            item.setCheckstate(self, column, value)
            item.emit(SIGNAL('checked_changed'), item)

            #Update itself
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            
            #Update its children
            if(len(item.children) > 0):
                first = item.children[0].columns[column].index
                last = item.children[-1].columns[column].index #Grab last child
                if first != None and last != None: #If the thing wasn't expanded then there wont be any indexes to update....
                    self.dataChanged.emit(first, last)
                    self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), first, last)
                
            #Update this node's parent if all of its children are checked or unchecked
            #Update parent
            
            parent = index.parent()
            
            if not parent.isValid():
                return True
            
            item = parent.internalPointer()

            if(column >= len(item.columns)):
                return True
            
            if not (item.columns[column].flags & Qt.ItemIsTristate):
                return True
            count = 0
            #Determine if all of the parents children's values are checked
            for row in range(len(item.children)):
                    state = self.data(parent.child(row, column), role).toInt()[0]
                    count = count + state
            #This is kind of tricky.  
            #Because the states are integers we can just sum up all of the states and see if they are equal to the checked state.
            
            if count == len(item.children)*(Qt.Checked):
                self.setData(parent, QVariant( Qt.Checked), role)
            elif count == len(item.children)*Qt.Unchecked:
                self.setData(parent, QVariant(Qt.Unchecked), role)
            else:
                self.setData(parent, QVariant(Qt.PartiallyChecked), role)
            
            return True
    def flags(self, index):
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
        
        if not index.isValid():
            flags = QAbstractItemModel.flags(self, index)
            return flags | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled |Qt.ItemIsSelectable
        column = index.column()
        item = index.internalPointer()
        #print item.json
        #print item.columns[column].flags
        #print column
        parent = index.parent()
        try:
            #print parent.internalPointer().json
            pass
        except:
            pass

        return  item.columns[column].flags



if __name__ == "__main__":
    from modeltest import ModelTest
    import PyQt4.QtCore
    
    tree_model = TreeModel(None)
    blah = Config_Base(  tree_model.top)
    blah2 = Config_Base(blah)
    blah2.columns.append(TreeColumn(PyQt4.QtCore.QString("Test"))) #Add some stuff to this thing.
    blah2.columns.append(TreeSpinBoxColumn(blah2)) #Add more stuff to this thing.
    blah2.columns[2].flags |=  Qt.ItemIsEditable 
    blah2.checkable = True
    
    print "TEST START"
    modeltest = ModelTest(tree_model, None)
    print "TEST END"
