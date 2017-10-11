from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from test_ui import Ui_MainWindow  # 界面与逻辑分离
import sys
import xlrd
import scipy as sp
import warnings
import seaborn as sns
from Calculation_Functions import *

warnings.filterwarnings("ignore")


def read_file(file_path, DBC_index, Car_index, Driver_index, type='txt'):
    def readfile(path, type='excel'):
        if type == 'excel':
            filename = re.match(r'^([0-9a-zA-Z/:_.\u4e00-\u9fa5]+)\\'  # 父文件夹
                                r'([0-9a-zA-Z]+)_([0-9a-zA-Z]+)_([a-z]+)_([0-9]?.xls|xlsx)$', i)  # 文件名
            CarName = filename.group(2)
            TestName = filename.group(3)
            DriverName = filename.group(4)
            print('Start Transform ' + DriverName + filename.group(5) + ' data.')
            bk = xlrd.open_workbook(path)
            shxrange = range(bk.nsheets)
            try:
                sh = bk.sheet_by_index(0)
            except:
                pass

            nrows = sh.nrows  # 获取行数
            ncols = sh.ncols  # 获取列数
            # print("nrows %d, ncols %d" % (nrows, ncols))
            initial_field = sh.row_values(14)  # 原始字段，供查找
            row_list = []  # 获取各行数据
            for j in range(17, nrows):  # 数据行的起点
                row_data = sh.row_values(j)
                row_list.append(row_data)
            row_array = np.array(row_list)  # 转换为 ndarray 格式

        elif type == 'csv':
            filename = re.match(r'^([0-9a-zA-Z/:_.\u4e00-\u9fa5]+)\\'  # 父文件夹
                                r'([0-9a-zA-Z]+)_([0-9a-zA-Z]+)_([0-9a-zA-Z]+)_([0-9]+)_([0-9]+).(csv)$', i)  # 文件名
            CarName = filename.group(2)
            TestName = filename.group(3)
            DriverName = filename.group(4)
            Testid_com = filename.group(6)
            csvdata = pd.read_csv(path)
            row_array = np.array(csvdata)
            initial_field = csvdata.columns.tolist()

        elif type == 'txt':
            filename = re.match(r'^([0-9a-zA-Z/:_.\u4e00-\u9fa5]+)\\'  # 父文件夹
                                r'([0-9a-zA-Z]+)_([0-9a-zA-Z]+)_([a-z]+)_([0-9]+)_([0-9]+).(txt)$', i)  # 文件名
            CarName = filename.group(2)
            TestName = filename.group(3)
            DriverName = filename.group(4)
            Testid_com = filename.group(6)
            # print('Start Transform ' + DriverName + filename.group(5) + ' data.')

            with open(path, 'r') as file_to_read:
                table = pd.read_table(file_to_read, sep='\t', header=12, index_col=False)  # 12行为表头，自动删除空行
                table.drop([0, 1], axis=0, inplace=True)
                row_array = np.array(table.iloc[:, 0:-1])  # 最后一列去掉
                initial_field = table.columns.tolist()[0:-1]
        return row_array, CarName, TestName, DriverName, initial_field, Testid_com, \
               [DriverName + filename.group(5) + ' data']

    DBC_csv_Refer = open(DBC_index, 'r')
    csvreader = csv.reader(DBC_csv_Refer)
    DBC_field_csv = []
    for rows in csvreader:
        DBC_field_csv.append(rows)  # DBC定义的变量名

    Dri_csv_Refer = open(Driver_index, 'r')
    csvreader = csv.reader(Dri_csv_Refer)
    Dri_index_csv = []
    for rows in csvreader:
        Dri_index_csv.append(rows)  # 驾驶员姓名索引

    Car_csv_Refer = open(Car_index, 'r')
    csvreader = csv.reader(Car_csv_Refer)
    Car_index_csv = []
    for rows in csvreader:
        Car_index_csv.append(rows)  # 车辆索引

    path_list = glob.glob(file_path)  # 获取文件目录下所有的 .xls 文件
    Travel_ID = 0

    for i in path_list:
        row_array, CarName, TestName, DriverName, initial_field, Testid_com, message = readfile(i, type)
        DriverID = 0
        CarID = 0
        if int(Testid_com) == 1:
            Travel_ID = Travel_ID + 1

        for m in Dri_index_csv:
            if DriverName == m[1]:
                DriverID = m[0]
                break

        for m in Car_index_csv:
            if CarName == m[1]:
                CarID = m[0]
                break

        Intest_field = np.array(
            ['Travel_ID', 'Driver_ID', 'Car_ID', 'Data_ID', 'Date', 'Time', 'Longitude', 'Latitude', 'Altitude',
             'Direction', 'GPS_Vspd', 'X_acc', 'Y_acc', 'Z_acc', 'Tempeature', 'Box_odo', 'Alarm_spd'])  # Intest表头

        data_zeros = np.matrix(np.zeros(row_array.shape[0])).T
        data_TravelID = data_zeros.copy()
        data_TravelID[data_TravelID == 0] = Travel_ID
        data_driID = data_zeros.copy()
        data_driID[data_driID == 0] = DriverID
        data_car = data_zeros.copy()
        data_car[data_car == 0] = CarID
        data_null = data_zeros.copy()
        data_null[data_null == 0] = np.nan

        Intest_data = np.concatenate((data_TravelID, data_driID, data_car, row_array[:, 0:14]), axis=1)
        Intest_table_total = np.concatenate((np.matrix(Intest_field), Intest_data), axis=0)

        DBC_data = np.concatenate((data_zeros, data_zeros), axis=1)
        for Field_ID in DBC_field_csv:
            for field_id in Field_ID:
                try:
                    field_index_ = initial_field.index(field_id)
                    # kk = np.matrix(row_array[:, field_index_])
                    DBC_data = np.concatenate((DBC_data, np.matrix(row_array[:, field_index_]).T), axis=1)
                    break
                except ValueError as e:
                    pass
                if field_id == Field_ID[-1]:
                    # kkkk = np.array(data_null).tolist()
                    DBC_data = np.concatenate((DBC_data, np.array(data_null)), axis=1)

        DBC_data = sp.delete(DBC_data, 0, 1)
        DBC_data = sp.delete(DBC_data, 0, 1)
        DBC_field = np.matrix(DBC_field_csv)[:, 0]
        DBC_table_total = np.concatenate((DBC_field.T, DBC_data), axis=0)
        Total_table = np.concatenate((Intest_table_total, DBC_table_total), axis=1)
        Combine_file_name = CarName + '_' + TestName + '_data.csv'
        csvfile = open(Combine_file_name, 'a', newline='')  # 改成追加了 ‘a‘
        # reference "C:\Users\Lu\Desktop\AS24\python学习\CSV写入存在空行问题.pdf"
        csvwriter = csv.writer(csvfile)
        if i == path_list[0]:
            csvwriter.writerows(Total_table.tolist())
        else:
            del_head = Total_table.tolist()
            del_head.pop(0)
            csvwriter.writerows(del_head)
        yield message, path_list.__len__(), Combine_file_name


def data_process(file_path, save_name):
    # --------------------------- Main Scripts  -------------------------------
    data_file_name = file_path
    # data_file_name = "C:/Users/Lu/Desktop/驾驶行为工作/PYProject\\ZS11_Standard_data.csv"
    # data_file_name = "E:/驾驶行为工作/PYProject\\ZS11_Standard_data.csv"
    filename = re.match(r'^([0-9a-zA-Z/:_.\u4e00-\u9fa5]+)/'  # 父文件夹 相对路径
                        r'([0-9a-zA-Z]+)_([0-9a-zA-Z]+)_([a-z]+.csv)$', data_file_name)  # 文件名
    CarName = filename.group(2)
    csvdata = pd.read_csv(data_file_name)

    Target_Driver_Date_ful = csvdata.loc[:, ['Driver_ID', 'Date', 'Travel_ID']]
    Target_Driver_Date = Target_Driver_Date_ful.drop_duplicates()

    resultarray = []
    backup_data = []

    # print('DriverID', 'Date', 'TravelID')

    for i in range(Target_Driver_Date.shape[0]):  # 样本数据个数
        DriverID = Target_Driver_Date.iloc[i][0]
        Date = Target_Driver_Date.iloc[i][1]
        TravelID = Target_Driver_Date.iloc[i][2]
        Target_Driver = csvdata[(csvdata['Travel_ID'] == TravelID)]  # 筛出的样本集

        # Target_Driver = ignore_charging(Target_Driver)
        try:
            charge_pos = ((Target_Driver['ElecVehSysMd'] == 8).tolist()).index(True)  # 找不到充电会出错
            Target_Driver = Target_Driver.iloc[0:charge_pos]  # 充电后的都不要，防止末电量出错
        except ValueError as ve:
            pass

        Target_Driver.drop(Target_Driver[(Target_Driver['ElecVehSysMd'] == 8) |
                                         (Target_Driver['BMSPackSOC'] == float(0))].index, axis=0, inplace=True)
        # Target_Driver.drop(Target_Driver[(Target_Driver['EPTDrvngMdSwSts'] == 0) |
        #                                  (Target_Driver['EPTDrvngMdSwSts'] == 2)].index, axis=0, inplace=True)
        Target_Driver = Target_Driver[Target_Driver['EPTDrvngMdSwSts'] == 1]
        # 删掉充电阶段的数据以及电量异常的数据，只取得N模式的数据（Eco\Normal\Sport）

        if Target_Driver.shape[0] > 1000:  # 太短的样本选择丢弃

            Fuel_Csump = Target_Driver['Fuel_Csump'].tolist()
            # X_acc = Target_Driver['X_acc'].tolist()
            vspd = five_points_avg(Target_Driver['Veh_Spd_NonDrvn'].tolist())
            Strg_Whl_Ang = Target_Driver['Strg_Whl_Ang'].tolist()
            str_multi_vspd = Target_Driver['Veh_Spd_NonDrvn'] * Target_Driver['Strg_Whl_Ang']
            acc_ped = Target_Driver['Acc_Actu_Pos'].tolist()
            L_Dir_lamp = Target_Driver['L_Dir_lamp'].tolist()
            R_Dir_lamp = Target_Driver['R_Dir_lamp'].tolist()
            VSE_Longt_Acc = (Target_Driver['VSE_Longt_Acc'] / 9.8).tolist()
            time = range(len(Fuel_Csump))
            X_acc = five_points_avg_acc(vspd)
            Y_acc = Target_Driver['Y_acc'].tolist()

            # longitude, latitude = GPS_fix(Target_Driver['Longitude'], Target_Driver['Latitude'])
            # ang_abs, ang_delta = heading_angle(list(longitude), list(latitude))
            # ang = heading_angle_cal(list(longitude), list(latitude))
            # turn_lab = turnning_cal(ang)

            # ------------------- Style features ---------------------
            odemeter = odemeter_cal(vspd)
            fuel_cons = fuel_cal(Fuel_Csump) / odemeter * 100  # L/100km
            # overtake_times = overtake_cal(turn_lab, ang_abs, np.array(Strg_Whl_Ang), np.array(vspd))  # 计算速度还是太低 AS24跑不动
            overtake_times = 0
            brake_skill_score = brake_skill(VSE_Longt_Acc, vspd)
            sudden_acc_times = sudden_acc(X_acc, vspd, CarName)
            sudden_brake_times = sudden_brake(X_acc, CarName)
            sudden_steering_times = sudden_steering(Y_acc, CarName)
            tip_in_times = tip_in(acc_ped)
            over_speed_propotion = over_speed_cal(Target_Driver, vspd)

            # ----------------- Statistics features ------------------
            soc_start = Target_Driver['BMSPackSOC'].tolist()[0]
            soc_end = Target_Driver['BMSPackSOC'].tolist()[-1]
            soc_balance_ratio = soc_balance_time_ratio(Target_Driver['BMSPackSOC'])
            mean_spd = np.mean(vspd)
            std_spd = np.std(vspd)
            mean_Strg_Whl_Ang = np.mean(Strg_Whl_Ang)
            std_Strg_Whl_Ang = np.std(Strg_Whl_Ang)
            mean_Strg_Whl_Ang_pos = Target_Driver[Target_Driver['Strg_Whl_Ang'] > 0].Strg_Whl_Ang.mean()
            mean_Strg_Whl_Ang_neg = Target_Driver[Target_Driver['Strg_Whl_Ang'] < 0].Strg_Whl_Ang.mean()
            mean_X_acc = np.mean(X_acc)
            std_X_acc = np.std(X_acc)
            mean_X_acc_pos = np.array(X_acc)[np.array(X_acc) > 0].mean()
            mean_X_acc_neg = np.array(X_acc)[np.array(X_acc) < 0].mean()
            mean_acc_ped = np.mean(acc_ped)
            std_acc_ped = np.std(acc_ped)

            print(DriverID, Date, TravelID, '....finish')

            sudden_acc_score = (sudden_acc_times[0] + sudden_acc_times[1] * 3 + sudden_acc_times[2] * 7) / odemeter
            sudden_brake_score = (sudden_brake_times[0] + sudden_brake_times[1] * 3 + sudden_brake_times[
                2] * 7) / odemeter
            sudden_steering_score = (sudden_steering_times[0] + sudden_steering_times[1] * 3 + sudden_steering_times[
                2] * 7) / odemeter

            sudden_acc_times = np.array(sudden_acc_times) / odemeter
            sudden_brake_times = np.array(sudden_brake_times) / odemeter
            sudden_steering_times = np.array(sudden_steering_times) / odemeter

            resultarray.append([DriverID, Date, brake_skill_score, sudden_acc_score, sudden_brake_score,
                                sudden_steering_score, overtake_times / odemeter])
            backup_data.append([TravelID, sudden_acc_times[0], sudden_acc_times[1], sudden_acc_times[2],
                                sudden_brake_times[0], sudden_brake_times[1], sudden_brake_times[2],
                                sudden_steering_times[0], sudden_steering_times[1], sudden_steering_times[2],
                                brake_skill_score, overtake_times / odemeter, tip_in_times[0] / odemeter,
                                odemeter, mean_spd, mean_Strg_Whl_Ang, mean_Strg_Whl_Ang_pos, mean_Strg_Whl_Ang_neg,
                                mean_X_acc, mean_X_acc_pos, mean_X_acc_neg, mean_acc_ped,
                                std_spd, std_Strg_Whl_Ang, std_X_acc, std_acc_ped, over_speed_propotion,
                                fuel_cons, soc_balance_ratio, soc_start, soc_end])
        else:
            print(DriverID, Date, TravelID, '....Poor data to analyse')

    resultarray = np.array(resultarray)
    output_array = id_to_name(resultarray[:, 0:2])
    output_array = np.concatenate((output_array, backup_data), axis=1)
    field_name = np.array(['DriveID', 'Date', 'Name',
                           'TravelID', 'SoftAcc', 'MidAcc', 'RadiAcc', 'SoftBrk', 'MidBrk',
                           'RadiBrk', 'SoftStr', 'MidStr', 'RadiStr', 'BrkSkill', 'OverTake', 'Tip_in', 'Odemeter',
                           'MeanSpd', 'Mean_Str_Whl_Ang', 'Mean_Str_Whl_Ang_Pos', 'Mean_Str_Whl_Ang_Neg',
                           'Mean_X_acc', 'Mean_X_acc_Pos', 'Mean_X_acc_Neg', 'Mean_acc_ped',
                           'Std_spd', 'Std_Strg_Whl_Ang', 'Std_X_acc', 'Std_acc_ped', 'OverSpeed_ratio',
                           'FuelCons', 'Soc_balance_ratio', 'Soc_start', 'Soc_end'])
    output_array = np.concatenate((np.matrix(field_name), output_array))
    output_array = dropDupli(output_array)
    save_name = save_name + '.csv'
    pd.DataFrame(output_array).to_csv(save_name, header=False, index=False, mode='a')
    # (pd.DataFrame(output_array).drop_duplicates()).to_csv('Drive_score.csv', header=None, index=None)
    return output_array


class LoginDlg(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(LoginDlg, self).__init__(parent)
        self.setupUi(self)
        self.menu_InputData.triggered.connect(self.open_data)  # 继承图形界面的主菜单Menu_plot的QAction，绑定回调函数
        self.menu_CalData.triggered.connect(self.cal_data)
        self.open_DBC.clicked.connect(self.push_DBC_Index_file)
        self.open_CAR.clicked.connect(self.push_CAR_Index_file)
        self.open_DRIVER.clicked.connect(self.push_Driver_Index_file)
        self.pushButton_2.clicked.connect(self.datatableview_show)
        self.filepath_fulldata = ''
        self.filepath_DBC = './DBC_index.csv'  # 默认值
        self.filepath_Car = './Car_index.csv'
        self.filepath_Driver = './Driver_index.csv'

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

    def datatableview_show(self):
        self.model = QtGui.QStandardItemModel(self.DatatableView)
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('HH'))
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("FF"))
        self.model.setItem(0, 0, QtGui.QStandardItem('1'))
        self.model.setItem(1, 1, QtGui.QStandardItem('4'))
        self.DatatableView.setModel(self.model)
        self.DatatableView.resizeColumnsToContents()

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
