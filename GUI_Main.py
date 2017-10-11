from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from test_ui import Ui_MainWindow  # 界面与逻辑分离
from Calculation_Functions import *  # 算法逻辑
import sys
import warnings

warnings.filterwarnings("ignore")


class LoginDlg(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(LoginDlg, self).__init__(parent)
        self.setupUi(self)
        self.menu_InputData.triggered.connect(self.open_data)  # 继承图形界面的主菜单Menu_plot的QAction，绑定回调函数
        self.menu_CalData.triggered.connect(self.cal_data)
        self.open_DBC.clicked.connect(self.push_DBC_Index_file)
        self.open_CAR.clicked.connect(self.push_CAR_Index_file)
        self.open_DRIVER.clicked.connect(self.push_Driver_Index_file)
        self.pushButton_2.clicked.connect(self.graphicview_show)
        self.DatatableView.clicked.connect(self.graphicview_show)
        self.filepath_fulldata = './AS24_predict_data.csv'
        self.filepath_DBC = './DBC_index.csv'  # 默认值
        self.filepath_Car = './Car_index.csv'
        self.filepath_Driver = './Driver_index.csv'

        # -------------------------------- 回调函数------------------------------------------

    def open_data(self):
        self.statusbar.showMessage('测试数据导入中……')
        filepath = QFileDialog.getExistingDirectory(self)
        filepath_full = filepath + '/*.txt'
        self.main_process_thread = Main_process(filepath_full, self.filepath_DBC, self.filepath_Car,
                                                self.filepath_Driver, Process_type='input_data')
        self.main_process_thread.Message_Signal.connect(self.thread_message)  # 传递参数不用写出来，对应好接口函数即可
        self.main_process_thread.Message_Finish.connect(self.thread_message)
        self.main_process_thread.start()

    def cal_data(self):
        self.statusbar.showMessage('计算中……')
        self.main_process_thread = Main_process(self.filepath_fulldata, Save_name=self.plainTextEdit_4.toPlainText(),
                                                Process_type='cal_data')
        self.main_process_thread.Message_Signal.connect(self.thread_message)
        self.main_process_thread.Message_Data.connect(self.datatableview_show)
        self.main_process_thread.start()

    def thread_message(self, mes_str):
        self.statusbar.showMessage(mes_str)
        self.filepath_fulldata = './' + mes_str[6::]

    def datatableview_show(self, data_list):
        self.model = QtGui.QStandardItemModel(self.DatatableView)
        # self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('HH'))
        # self.model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("FF"))
        for i in range(data_list.__len__()):
            for j in range(data_list[0].__len__()):
                self.model.setItem(i, j, QtGui.QStandardItem(data_list[i][j]))

        self.DatatableView.setModel(self.model)
        self.DatatableView.resizeColumnsToContents()

    def graphicview_show(self):
        Current_index = self.DatatableView.currentIndex()
        Dri_ID = self.model.data(self.model.index(Current_index.row(), 0))
        Date = self.model.data(self.model.index(Current_index.row(), 1))
        Time = self.model.data(self.model.index(Current_index.row(), 2))
        self.scene = QtWidgets.QGraphicsScene()
        try:
            self.routine_pic = QtGui.QPixmap('./RoutinePic/AS24_'+str(int(float(Dri_ID)))+'_'+str(int(float(Date))) +
                                             '_'+str(int(float(Time)))+'.png')  # 车型问题没定义好   待解决 2017/9/30
            self.scene.addPixmap(self.routine_pic)
            self.graphicsView.setScene(self.scene)
        except:
            pass

    def accept(self):
        # QMessageBox.warning(self, 'chenggong', 'heh', QMessageBox.Yes)
        self.pushButton.setHidden(True)

    def messlistview(self):
        # self.MessagelistView.setWindowTitle('显示')
        # model = QtGui.QStandardItemModel(self.MessagelistView)
        # self.MessagelistView.setModel(model)
        # self.MessagelistView.show()
        # message_item = QtGui.QStandardItem(mes[0][0])  # 只接受string
        # model.appendRow(message_item)
        pass

    def push_DBC_Index_file(self):
        filepath = QFileDialog.getOpenFileName(self)
        self.plainTextEdit.setPlainText(filepath[0])
        self.filepath_DBC = filepath[0]

    def push_CAR_Index_file(self):
        filepath = QFileDialog.getOpenFileName(self)
        self.plainTextEdit_2.setPlainText(filepath[0])
        self.filepath_Car = filepath[0]

    def push_Driver_Index_file(self):
        filepath = QFileDialog.getOpenFileName(self)
        self.plainTextEdit_3.setPlainText(filepath[0])
        self.filepath_Driver = filepath[0]


class Main_process(QtCore.QThread):  # 务必不要继承主窗口，并在线程里面更改主窗口的界面，会莫名其妙的出问题

    Message_Signal = QtCore.pyqtSignal(str)
    Message_Finish = QtCore.pyqtSignal(str)
    Message_Data = QtCore.pyqtSignal(list)

    def __init__(self, filepath, DBC_path='', Car_path='', Driver_path='', Save_name='', Process_type='input_data'):
        super(Main_process, self).__init__()
        self.file_path = filepath
        self.DBC_path = DBC_path
        self.Car_path = Car_path
        self.Driver_path = Driver_path
        self.Save_name = Save_name
        self.Process_type = Process_type
        self.output_data = []

    def run(self):  # 重写进程函数
        if self.Process_type == 'input_data':
            message = read_file(self.file_path, self.DBC_path, self.Car_path, self.Driver_path)
            k = 1
            while k:
                try:
                    mes = message.__next__()  # generator [消息,总任务数]
                    # self.progressBar.setValue(int(k / mes[1]) * 100)
                    # self.progressBar.show()
                    # self.statusbar.showMessage('测试数据导入' + str(k))
                    self.Message_Signal.emit("测试数据 " + mes[0][0] + "导入中……")
                    k = k + 1
                except:
                    self.Message_Signal.emit("导入完成……")
                    k = 0
            try:
                self.Message_Finish.emit("存储文件名:" + mes[2])
            except:
                self.Message_Finish.emit("导入失败")

        elif self.Process_type == 'cal_data':
            self.out_putdata = data_process(self.file_path, self.Save_name)
            self.Message_Signal.emit("计算完成！")
            self.Message_Data.emit(self.out_putdata)


app = QApplication(sys.argv)
dlg = LoginDlg()
dlg.show()
sys.exit(app.exec())
