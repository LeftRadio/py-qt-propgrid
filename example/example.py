from Gui import loadItems, JsonToObject,ConfigGridTreeView,ConfigCommand
from Items import Config_CheckBox,Config_Double,Config_String,Config_Group
if __name__ == "__main__":
    items = loadItems()
    #item = JsonToObject(items, {'gui_type':'CheckBox'})

    from python_qt_binding.QtCore import *
    from python_qt_binding.QtGui   import *
    import python_qt_binding.QtGui as QtGui
    app = QtGui.QApplication([])
    a = ConfigGridTreeView(None)
    

    #items = [{'gui_type':'Group', 'name':'Test1', 'members':[{'gui_type':'Group', 'name':'test2'}, {'name':'blah','gui_type':'CheckBox'}]}, {'gui_type':'String'},{'gui_type':'Group', 'name':'Test', 'members':[{'name':'blah','gui_type':'CheckBox'}]}, {'gui_type':'String'}]
    #items = [{'gui_type':'Bool', 'name':'aBool', 'value':True}, {'gui_type':'Group', 'name':'Test1', 'members':[ {'gui_type':'ComboBox', 'name':'test3', 'options':['yes', 'no', 'maybe'],'value':'blah'}]}, {'gui_type':'String', 'name':'test3', 'value':'blah2'}]
    #items = [ {'gui_type':'Group', 'name':'Test1', 'members':[ {'gui_type':'ComboBox', 'name':'test3', 'options':['yes', 'no', 'maybe'],'value':'blah'}]}]

    item1 = Config_CheckBox(name='Test')
    item2 = Config_CheckBox(name='test2')
    item3 = Config_Double(name='Double')
    item4 = Config_String(name='StringBox')
    item5 = Config_Group(name='Group')
    item5.children = [item1,item2,item3]
    items = [ item4,item5]

    a.setItems(items)

    a.show()
    app.exec_()
