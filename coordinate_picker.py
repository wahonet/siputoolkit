"""
coordinate_picker.py

负责“坐标拾取模式”的开启与关闭，通过鼠标点击事件获取用户在图像上的点击位置。
在拾取坐标后，会弹出对话框输入“测点类型”和“测点说明”，
并从内置 DOM 或 DSM 数据中读取海拔高程，最终将完成的坐标信息显示并可导出。
"""

from PyQt5.QtWidgets import (
    QTableWidgetItem, QMessageBox, QDialog,
    QVBoxLayout, QLabel, QComboBox, QPushButton,
    QHBoxLayout, QFileDialog
)
from orthophoto_utils import (
    transform_coordinate,
    decimal_degrees_to_dms,
    export_csv,
    get_altitude,
    get_altitude_dsm
)

class CoordDetailDialog(QDialog):
    """
    弹出对话框，用于输入“测点类型”和“测点说明”。
    测点类型: 单选框(可编辑)，默认选项: 边界点、中心点、标志点、其他
    测点说明: 单选框(可编辑)，默认选项: 西北、东北、东南、西南
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("测点信息")
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(["边界点", "中心点", "标志点", "其他"])

        self.desc_combo = QComboBox()
        self.desc_combo.setEditable(True)
        self.desc_combo.addItems(["西北角", "东北角", "东南角", "西南角"])

        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("测点类型:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("测点说明:"))
        layout.addWidget(self.desc_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        """
        返回 (测点类型, 测点说明)
        """
        return self.type_combo.currentText().strip(), self.desc_combo.currentText().strip()


class CoordinatePicker:
    def __init__(self, canvas, table_coords, dataset_dom=None, dataset_dsm=None):
        """
        :param dataset_dom: 主DOM（通常不含高程）
        :param dataset_dsm: DSM 文件，含高程
        """
        self.canvas = canvas
        self.table_coords = table_coords
        self.dataset_dom = dataset_dom
        self.dataset_dsm = dataset_dsm

        self.is_selecting_coords = False
        self.coords_list = []  # 存储拾取的坐标及测点信息
        self.cid = None  # mpl_connect 的连接ID

    def toggle_coordinate_pick(self):
        """
        切换坐标拾取模式
        """
        if self.is_selecting_coords:
            # 退出坐标拾取模式
            self.is_selecting_coords = False
            if self.cid is not None:
                self.canvas.mpl_disconnect(self.cid)
                self.cid = None
        else:
            # 进入坐标拾取模式
            self.is_selecting_coords = True
            self.cid = self.canvas.mpl_connect('button_press_event', self.pick_coords)

    def pick_coords(self, event):
        """
        鼠标点击事件拾取坐标：点击后弹出对话框，输入“测点类型”、“测点说明”。
        优先从 dataset_dsm 中获取海拔，若无DSM则从 dataset_dom 中读取或返回0.
        """
        if event.button != 1:  # 1 表示鼠标左键
            return
        if not self.canvas or event.inaxes != self.canvas.ax:
            return

        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        # 将像素坐标转换为地理坐标
        col, row = xdata, ydata
        try:
            if self.canvas.transform is None:
                QMessageBox.warning(None, "警告", "当前尚未加载正射影像，无法拾取坐标。")
                return

            lon, lat = transform_coordinate(
                col, row,
                self.canvas.transform,
                src_crs="EPSG:4548",
                dst_crs="EPSG:4490"
            )
            lon_dms = decimal_degrees_to_dms(lon, is_lat=False)[:-1]
            lat_dms = decimal_degrees_to_dms(lat, is_lat=True)[:-1]

            # 优先从 DSM 获取海拔
            alt = get_altitude_dsm(self.dataset_dsm, col, row)
            if alt == 0.0:
                alt = get_altitude(self.dataset_dom, col, row)

            dlg = CoordDetailDialog()
            if dlg.exec_() == dlg.Accepted:
                measure_type, measure_desc = dlg.get_data()

                index = len(self.coords_list) + 1
                coord_info = {
                    "index": index,
                    "type": measure_type,
                    "lat": lat_dms,
                    "lon": lon_dms,
                    "alt": round(alt, 3),
                    "desc": measure_desc
                }
                self.coords_list.append(coord_info)

                row_index = self.table_coords.rowCount()
                self.table_coords.insertRow(row_index)
                self.table_coords.setItem(row_index, 0, QTableWidgetItem(str(index)))
                self.table_coords.setItem(row_index, 1, QTableWidgetItem(measure_type))
                self.table_coords.setItem(row_index, 2, QTableWidgetItem(lat_dms))
                self.table_coords.setItem(row_index, 3, QTableWidgetItem(lon_dms))
                self.table_coords.setItem(row_index, 4, QTableWidgetItem(str(round(alt, 3))))
                self.table_coords.setItem(row_index, 5, QTableWidgetItem(measure_desc))

        except Exception as e:
            QMessageBox.critical(None, "坐标拾取错误", f"拾取坐标时发生错误：{str(e)}")

    def clear_coords(self):
        """
        清空坐标列表和表格内容
        """
        self.coords_list.clear()
        self.table_coords.setRowCount(0)

    def export_coords(self):
        """
        导出当前拾取的坐标列表到 CSV 文件
        """
        if not self.coords_list:
            QMessageBox.warning(None, "提示", "无坐标可导出！")
            return

        out_path, _ = QFileDialog.getSaveFileName(None, "导出坐标", "", "CSV Files (*.csv)")
        if out_path:
            export_csv(self.coords_list, out_path)
            QMessageBox.information(None, "提示", f"坐标已导出至 {out_path}")

    def is_in_select_mode(self):
        """
        返回当前是否处于坐标拾取模式
        """
        return self.is_selecting_coords

    def get_coords(self):
        """
        返回内部记录的坐标信息（含测点类型、说明、海拔等）
        """
        return self.coords_list

    def set_dataset_dom(self, dataset):
        """
        设置或更新 DOM 文件对应的 dataset
        """
        self.dataset_dom = dataset

    def set_dataset_dsm(self, dataset):
        """
        设置或更新 DSM 文件对应的 dataset
        """
        self.dataset_dsm = dataset
