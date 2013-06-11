from py_qt_propgrid.Gui import loadItems, JsonToObject,ConfigGridTreeView,ConfigCommand
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
