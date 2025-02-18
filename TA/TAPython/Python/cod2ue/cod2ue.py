#Welcome to my code. This code is not the cleanest. If there was any type of error qt crashes and unreal engine with it, so, I had to "convert"
#the whole thing to a (almost) crash proof program. There are a lot of extra ifs, try and excepts, and etc because of this.
#Still, I think the whole idea behind every function is pretty interesting. I actually built this program 3 times before landing on this.

import importlib
import unreal
import os
import sys
import json
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox

version = 1.5

#Main settings
sys.path.append(os.path.dirname(__file__))

import necessary
import functions
importlib.reload(necessary)
importlib.reload(functions)

project_path = os.path.normpath(os.path.realpath(unreal.SystemLibrary.get_project_directory()))
current_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))
json_location = os.path.normpath(os.path.join(current_path, 'save.json'))

unreal.log(f"project_path = {project_path}")
unreal.log(f"current_path = {current_path}")
unreal.log(f"json_location = {json_location}")
print("-"*32)

if not os.path.isfile(json_location):
    print(f"Seems like {json_location} does not exist!")
    print("Please re-download the plugin!")
    sys.exit(0)

#Setup Settings
def get_data():

    global save_data
    global map_obj
    global greyhound_folder
    global import_folder
    global import_props
    global import_geometry
    global individual_geometry_objects
    global place_props
    global place_geometry
    global global_opacity
    global opacity_items

    global assets_folder_dir
    global map_name
    global map_folder
    global map_extension
    global import_folder_shown
    global import_folder
    global assets_folder

    with open(json_location) as save_data_json:
        save_data = json.load(save_data_json)

    for data in save_data:
        map_obj = os.path.normpath(data['Map Obj'])
        greyhound_folder = os.path.normpath(data['Greyhound Folder'])
        import_folder = data['Import Folder']
        import_props = data['Import Props']
        import_geometry = data['Import Geometry']
        individual_geometry_objects = data['Individual Geometry Objects']
        place_props = data['Place props']
        place_geometry = data['Place Geometry']
        global_opacity = data['Global Opacity']
        opacity_items = data['Opacity Items']


    #Fixed settings
    assets_folder_dir =  os.path.normpath(os.path.join(project_path, 'Content', import_folder, 'AssetsFolder')) # f"{project_path}/Content/{import_folder}/AssetsFolder"
    map_name = os.path.splitext(os.path.basename(map_obj))[0]
    map_folder = os.path.join(os.path.normpath(os.path.dirname(map_obj)), '') # f"{os.path.dirname(map_obj)}\\"
    map_extension = os.path.splitext(map_obj)[1]
    import_folder_shown = import_folder
    import_folder = "/Game/" + import_folder + "/"
    assets_folder = f"{import_folder}AssetsFolder/"

    # globals().update(locals())

get_data()

#Here starts the UI
class Ui_MainWindow(QWidget):
    _instance: QWidget = None  # Holds a reference to the last instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance.destroy()
            del cls._instance

        instance = super().__new__(cls)
        # cls._instance = instance
        return instance

    def __init__(self):
        super().__init__()
        unreal.log("__init__ Ui_MainWindow")

        self.main_window = QtWidgets.QMainWindow(self)
        self.setup_ui(self.main_window)
        self.main_window.show()

        unreal.parent_external_window_to_slate(int( self.main_window.winId()))

    # Deleting (Calling destructor)
    def __del__(self):
        unreal.log("__del__ Ui_MainWindow")

        if self.main_window is not None:
            self.main_window.setParent(None)
            self.main_window.close()
            self.main_window.destroy()
            del self.main_window

    def setup_ui(self, main_window):
        #Set window icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(current_path + '/ToolLogo.png'), QtGui.QIcon.Mode.Selected, QtGui.QIcon.State.On)
        main_window.setWindowIcon(icon)

        #The other stuff
        main_window.setObjectName("MainWindow")
        main_window.resize(801, 275)
        main_window.setMinimumSize(QtCore.QSize(801, 275))
        main_window.setMaximumSize(QtCore.QSize(801, 275))
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.main_settings_label = QtWidgets.QLabel(self.centralwidget)
        self.main_settings_label.setGeometry(QtCore.QRect(20, 10, 100, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.main_settings_label.setFont(font)
        self.main_settings_label.setObjectName("main_settings_label")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(20, 30, 761, 16))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.map_folder_label = QtWidgets.QLabel(self.centralwidget)
        self.map_folder_label.setGeometry(QtCore.QRect(30, 60, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.map_folder_label.setFont(font)
        self.map_folder_label.setObjectName("map_folder_label")
        self.greyhound_directory_label = QtWidgets.QLabel(self.centralwidget)
        self.greyhound_directory_label.setGeometry(QtCore.QRect(30, 90, 104, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.greyhound_directory_label.setFont(font)
        self.greyhound_directory_label.setObjectName("greyhound_directory_label")
        self.map_obj_text = QtWidgets.QLineEdit(self.centralwidget)
        self.map_obj_text.setGeometry(QtCore.QRect(140, 60, 133, 20))
        self.map_obj_text.setText("")
        self.map_obj_text.setFrame(True)
        self.map_obj_text.setDragEnabled(False)
        self.map_obj_text.setClearButtonEnabled(False)
        self.map_obj_text.setObjectName("map_obj_text")
        self.map_obj_browsebutton = QtWidgets.QToolButton(self.centralwidget)
        self.map_obj_browsebutton.setGeometry(QtCore.QRect(280, 60, 31, 21))
        self.map_obj_browsebutton.setObjectName("map_obj_browsebutton")
        self.greyhound_folder_browsebutton = QtWidgets.QToolButton(self.centralwidget)
        self.greyhound_folder_browsebutton.setGeometry(QtCore.QRect(280, 90, 31, 21))
        self.greyhound_folder_browsebutton.setObjectName("greyhound_folder_browsebutton")
        self.greyhound_folder_text = QtWidgets.QLineEdit(self.centralwidget)
        self.greyhound_folder_text.setGeometry(QtCore.QRect(140, 90, 133, 20))
        self.greyhound_folder_text.setText("")
        self.greyhound_folder_text.setFrame(True)
        self.greyhound_folder_text.setDragEnabled(False)
        self.greyhound_folder_text.setClearButtonEnabled(False)
        self.greyhound_folder_text.setObjectName("greyhound_folder_text")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(320, 40, 20, 129))
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.import_folder_text = QtWidgets.QLineEdit(self.centralwidget)
        self.import_folder_text.setGeometry(QtCore.QRect(140, 120, 171, 20))
        self.import_folder_text.setFrame(True)
        self.import_folder_text.setDragEnabled(False)
        self.import_folder_text.setClearButtonEnabled(False)
        self.import_folder_text.setObjectName("import_folder_text")
        self.import_folder_label = QtWidgets.QLabel(self.centralwidget)
        self.import_folder_label.setGeometry(QtCore.QRect(30, 120, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.import_folder_label.setFont(font)
        self.import_folder_label.setObjectName("import_folder_label")
        self.global_opacity_items_text = QtWidgets.QTextEdit(self.centralwidget)
        self.global_opacity_items_text.setGeometry(QtCore.QRect(540, 70, 161, 51))
        self.global_opacity_items_text.setObjectName("global_opacity_items_text")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(330, 120, 451, 16))
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(20, 160, 761, 16))
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.import_button = QtWidgets.QPushButton(self.centralwidget)
        self.import_button.setGeometry(QtCore.QRect(200, 180, 84, 23))
        self.import_button.setObjectName("import_button")
        self.place_button = QtWidgets.QPushButton(self.centralwidget)
        self.place_button.setGeometry(QtCore.QRect(290, 180, 84, 23))
        self.place_button.setObjectName("place_button")
        self.re_parent_materials_button = QtWidgets.QPushButton(self.centralwidget)
        self.re_parent_materials_button.setGeometry(QtCore.QRect(380, 180, 112, 23))
        self.re_parent_materials_button.setObjectName("re_parent_materials_button")
        self.save_settings_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_settings_button.setGeometry(QtCore.QRect(500, 180, 100, 23))
        self.save_settings_button.setObjectName("save_settings_button")
        self.place_geometry_button = QtWidgets.QCheckBox(self.centralwidget)
        self.place_geometry_button.setGeometry(QtCore.QRect(420, 140, 98, 17))
        self.place_geometry_button.setObjectName("place_geometry_button")
        self.place_props_button = QtWidgets.QCheckBox(self.centralwidget)
        self.place_props_button.setGeometry(QtCore.QRect(340, 140, 78, 17))
        self.place_props_button.setObjectName("place_props_button")
        self.global_opacity_button = QtWidgets.QCheckBox(self.centralwidget)
        self.global_opacity_button.setGeometry(QtCore.QRect(540, 50, 92, 17))
        self.global_opacity_button.setObjectName("global_opacity_button")
        self.import_individual_geometry_button = QtWidgets.QCheckBox(self.centralwidget)
        self.import_individual_geometry_button.setGeometry(QtCore.QRect(340, 90, 159, 17))
        self.import_individual_geometry_button.setObjectName("import_individual_geometry_button")
        self.import_geometry_button = QtWidgets.QCheckBox(self.centralwidget)
        self.import_geometry_button.setGeometry(QtCore.QRect(340, 70, 105, 17))
        self.import_geometry_button.setObjectName("import_geometry_button")
        self.import_props_button = QtWidgets.QCheckBox(self.centralwidget)
        self.import_props_button.setGeometry(QtCore.QRect(340, 50, 85, 17))
        self.import_props_button.setObjectName("import_props_button")
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 801, 21))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"CoDtoUE - Release {version}"))
        self.main_settings_label.setText(_translate("MainWindow", "Settings"))
        self.map_folder_label.setText(_translate("MainWindow", "Map Obj"))
        self.greyhound_directory_label.setText(_translate("MainWindow", "Greyhound Directory:"))
        self.map_obj_text.setPlaceholderText(_translate("MainWindow", "directory..."))
        self.map_obj_browsebutton.setText(_translate("MainWindow", "..."))
        self.greyhound_folder_browsebutton.setText(_translate("MainWindow", "..."))
        self.greyhound_folder_text.setPlaceholderText(_translate("MainWindow", "directory..."))
        self.import_folder_text.setText(_translate("MainWindow", "CoD"))
        self.import_folder_text.setPlaceholderText(_translate("MainWindow", "directory..."))
        self.import_folder_label.setText(_translate("MainWindow", "Import Folder:"))
        self.global_opacity_items_text.setPlaceholderText(_translate("MainWindow", "Items with this name will have opacity. (If global opacity is turned off)"))
        self.import_button.setText(_translate("MainWindow", "Import"))
        self.place_button.setText(_translate("MainWindow", "Place"))
        self.re_parent_materials_button.setText(_translate("MainWindow", "Re-Parent Materials"))
        self.save_settings_button.setText(_translate("MainWindow", "Save Settings"))
        self.place_geometry_button.setText(_translate("MainWindow", "Place Geometry"))
        self.place_props_button.setText(_translate("MainWindow", "Place Props"))
        self.global_opacity_button.setText(_translate("MainWindow", "Global Opacity"))
        self.import_individual_geometry_button.setText(_translate("MainWindow", "Individual Geometry Objects"))
        self.import_geometry_button.setText(_translate("MainWindow", "Import Geometry"))
        self.import_props_button.setText(_translate("MainWindow", "Import Props"))

        #Set all text boxes values
        self.map_obj_text.setText(_translate("MainWindow", map_obj))
        self.greyhound_folder_text.setText(_translate("MainWindow", greyhound_folder))
        self.import_folder_text.setText(_translate("MainWindow", import_folder_shown))
        self.global_opacity_items_text.setText(_translate("MainWindow", ", ".join(opacity_items)))

        #Set all true or false values
        self.place_geometry_button.setChecked(place_geometry)
        self.import_props_button.setChecked(import_props)
        self.import_individual_geometry_button.setChecked(individual_geometry_objects)
        self.import_geometry_button.setChecked(import_geometry)
        self.place_props_button.setChecked(place_props)
        self.global_opacity_button.setChecked(global_opacity)

        #Connect buttons
        self.save_settings_button.clicked.connect(self.save)
        self.map_obj_browsebutton.clicked.connect(self.map_obj_browser)
        self.greyhound_folder_browsebutton.clicked.connect(self.greyhound_folder_browser)
        self.import_button.clicked.connect(self.import_function)
        self.place_button.clicked.connect(self.place_function)
        self.re_parent_materials_button.clicked.connect(self.re_parent_function)

    #This is what gets executed if you click the Save button
    def save(self):

        for data in save_data:
            #Set text values
            data['Map Obj'] = os.path.normpath(self.map_obj_text.text())
            data['Greyhound Folder'] = os.path.normpath(self.greyhound_folder_text.text())
            data['Import Folder'] = self.import_folder_text.text()
            data['Opacity Items'] = self.global_opacity_items_text.toPlainText().split(", ")

            #Set true or false values
            data['Place Geometry'] = self.place_geometry_button.isChecked()
            data['Import Props'] = self.import_props_button.isChecked()
            data['Individual Geometry Objects'] =  self.import_individual_geometry_button.isChecked()
            data['Import Geometry'] = self.import_geometry_button.isChecked()
            data['Place props'] = self.place_props_button.isChecked()
            data['Global Opacity'] = self.global_opacity_button.isChecked()

        with open(json_location, "w") as new_json:
            json.dump(save_data, new_json)

        get_data()

    #Open a tab telling you to select an obj
    def map_obj_browser(self):
        _translate = QtCore.QCoreApplication.translate
        path_info = QFileDialog.getOpenFileName(self, 'Open OBJ File', '', '(*.obj *.fbx)')
        map_obj = path_info[0]
        self.map_obj_text.setText(_translate("MainWindow", map_obj))

    #Open a tab telling you to select a folder (directory)
    def greyhound_folder_browser(self):
        _translate = QtCore.QCoreApplication.translate
        greyhound_folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.greyhound_folder_text.setText(_translate("MainWindow", greyhound_folder))

    #This is what gets executed if you click the import button
    def import_function(self):

        self.save()
        unreal.log(f"place_assets_folder {assets_folder}, {assets_folder_dir}, {current_path}")
        necessary.place_assets_folder(assets_folder, assets_folder_dir, current_path)

        #First check if the required files in your pc exist! That way no crashes happen!
        if not import_folder_shown == '':
            if import_props:
                if os.path.isfile(os.path.join(map_folder, f"{map_name}_xmodels.json")):
                    functions.Props.import_props(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items)
                else:
                    unreal.log_error(f'Seems like {os.path.isfile(os.path.join(map_folder, f"{map_name}_xmodels.json"))} does not exist (bad directory)')

            if import_geometry:
                if os.path.isfile(os.path.join(map_folder, f"{map_name}_matdata.json")) and os.path.isfile(os.path.join(map_folder, f"{map_name}.obj")):
                    if individual_geometry_objects:
                        functions.Geometry.import_individual_geometry(True, map_name, map_folder, import_folder, greyhound_folder, assets_folder, individual_geometry_objects, global_opacity, opacity_items, map_extension)
                    else:
                        functions.Geometry.import_geometry(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items, map_extension)
                else:
                    unreal.log_error(f'Seems like ""{map_folder}\\{map_name}_matdata.json" or "{map_folder}\\{map_name}.obj" does not exist! (bad directory)')

        else:
            unreal.log_error("Seems like your import folder setting is empty...")

        # Ui_MainWindow.done_popup(self)

    #This is what gets executed if you click the place button
    def place_function(self):

        self.save()

        #First check if the required files in your pc exist! That way no crashes happen!
        if not import_folder_shown == '':
            if place_props:
                if os.path.isfile(os.path.join(map_folder, f"{map_name}_xmodels.json")):
                    functions.Props.place(map_name, map_folder, import_folder)
                else:
                    print(f'Seems like {os.path.join(map_folder, f"{map_name}_xmodels.json")} does not exist (bad directory)')
            if place_geometry:
                if os.path.isfile(os.path.join(map_folder, f"{map_name}_matdata.json")):
                    functions.Geometry.place(map_name, map_folder, import_folder, greyhound_folder, assets_folder, individual_geometry_objects, global_opacity, opacity_items, map_extension)
                else:
                    print(f'Seems like {os.path.join(map_folder, f"{map_name}_matdata.json")} does not exist! (bad directory)')
        else:
            print("Seems like your import folder setting is empty...")

        # Ui_MainWindow.done_popup(self)

    #This is what gets executed if you click the Re-Parent Materials button
    def re_parent_function(self):

        self.save()

        if not import_folder_shown == '':

            if import_props:
                if os.path.isfile(f"{map_folder}\\{map_name}_xmodels.json"):
                    functions.Props.re_parent_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items)

                else:
                    print(f'Seems like "{map_folder}\\{map_name}_xmodels.json" does not exist (bad directory)')

            if import_geometry:
                if os.path.isfile(f"{map_folder}\\{map_name}_matdata.json"):
                    functions.Geometry.re_parent_materials(map_name, map_folder, import_folder, greyhound_folder, assets_folder, global_opacity, opacity_items)

                else:
                    print(f'Seems like {map_folder}\\{map_name}_matdata.json" does not exist! (bad directory)')

        else:
            print("Seems like your import folder setting is empty...")


        Ui_MainWindow.done_popup(self)

    def done_popup(self):
        message = QMessageBox()
        message.setWindowTitle("CoDtoUE Notification")
        message.setText("Done!")
        message.exec_()


# MainWindow = QtWidgets.QMainWindow()
# ui = Ui_MainWindow()
# ui.setup_ui(MainWindow)
# MainWindow.show()
#
# window_id = int(MainWindow.winId())  # Explicit conversion to int
# unreal.parent_external_window_to_slate(int(MainWindow.winId()))
