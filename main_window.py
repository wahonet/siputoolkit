"""
main_window.py

主窗口，提供文件加载、坐标拾取、标注、多边形绘制及尺寸标注功能。
改进：配合 polygon_drawer.py 使用 line.remove() 来卸载线条，避免 'ArtistList' 无 remove 方法的问题。
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QStatusBar, QGroupBox, QApplication, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

from image_canvas import ImageCanvas
from orthophoto_utils import (
    read_orthophoto,
    transform_coordinate,
    decimal_degrees_to_dms,
    export_csv
)
from label_manager import LabelManager, LabelDialog
from coordinate_picker import CoordinatePicker
from polygon_drawer import PolygonDrawer  # 多边形绘制模块
from dimension_annotator import DimensionAnnotator  # 尺寸标注模块
from cad_drawer import CADDrawer  # CAD绘图模块
import building_description  # 古建筑描述工具
import stele_description  # 碑刻描述工具
import os

class MainWindow(QMainWindow):
    """
    主窗口，提供文件加载、坐标拾取、标注、多边形绘制以及尺寸标注功能。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("第四次全国文物普查内业工具包")
        self.resize(1400, 800)

        # 设置窗口图标
        self.setWindowIcon(QIcon("logo.png"))  # 确保 'logo.png' 文件在工作目录下

        # DOM / DSM / 变换等数据
        self.dataset_dom = None   # DOM 数据
        self.dataset_dsm = None   # DSM 数据
        self.transform = None
        self.coords_list = []

        # ============ 主 Widget ============
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # =========================================================================
        # 顶部按钮分组布局
        # =========================================================================
        top_groups_layout = QHBoxLayout()

        # -------------------- 数据加载分组 -------------------
        group_data_load = QGroupBox("数据加载")
        layout_data_load = QHBoxLayout(group_data_load)

        self.btn_load_tif = QPushButton("导入DOM")
        self.btn_load_tif.clicked.connect(self.load_tif_dom)
        layout_data_load.addWidget(self.btn_load_tif)

        self.btn_load_dsm = QPushButton("导入DSM")
        self.btn_load_dsm.clicked.connect(self.load_tif_dsm)
        layout_data_load.addWidget(self.btn_load_dsm)

        self.btn_clear_all = QPushButton("清空数据")
        self.btn_clear_all.clicked.connect(self.clear_all)
        layout_data_load.addWidget(self.btn_clear_all)

        top_groups_layout.addWidget(group_data_load)

        # ------------------- 坐标操作分组 -------------------
        group_coords = QGroupBox("坐标操作")
        layout_coords = QHBoxLayout(group_coords)

        self.btn_pick_coords = QPushButton("开始拾取坐标")
        self.btn_pick_coords.clicked.connect(self.toggle_coordinate_pick)
        layout_coords.addWidget(self.btn_pick_coords)

        self.btn_clear_coords = QPushButton("清空坐标")
        self.btn_clear_coords.clicked.connect(self.clear_coords)
        layout_coords.addWidget(self.btn_clear_coords)

        self.btn_export_coords = QPushButton("导出坐标")
        self.btn_export_coords.clicked.connect(self.export_coords)
        layout_coords.addWidget(self.btn_export_coords)

        top_groups_layout.addWidget(group_coords)

        # ------------------- 标注操作分组 -------------------
        group_labels = QGroupBox("标注操作")
        layout_labels = QHBoxLayout(group_labels)

        self.btn_mark = QPushButton("开始标注")
        self.btn_mark.clicked.connect(self.toggle_label_mode)
        layout_labels.addWidget(self.btn_mark)

        self.btn_clear_label = QPushButton("清空标注")
        self.btn_clear_label.clicked.connect(self.clear_label)
        layout_labels.addWidget(self.btn_clear_label)

        self.btn_export_label = QPushButton("导出标注")
        self.btn_export_label.clicked.connect(self.export_label)
        layout_labels.addWidget(self.btn_export_label)

        top_groups_layout.addWidget(group_labels)

        # ------------------ 多边形操作分组 ------------------
        group_polygon = QGroupBox("多边形操作")
        layout_polygon = QHBoxLayout(group_polygon)

        self.btn_draw_polygon = QPushButton("开始绘制多边形")
        self.btn_draw_polygon.clicked.connect(self.start_draw_polygon)
        layout_polygon.addWidget(self.btn_draw_polygon)

        self.btn_clear_polygon = QPushButton("清空多边形")
        self.btn_clear_polygon.clicked.connect(self.clear_polygon)
        layout_polygon.addWidget(self.btn_clear_polygon)

        top_groups_layout.addWidget(group_polygon)

        # ------------------ 尺寸标注分组 ------------------
        group_dimension = QGroupBox("尺寸标注")
        layout_dimension = QHBoxLayout(group_dimension)

        self.btn_dimension = QPushButton("开始尺寸标注")
        self.btn_dimension.clicked.connect(self.start_dimension_annotation)
        layout_dimension.addWidget(self.btn_dimension)

        self.btn_clear_dimension = QPushButton("清空尺寸标注")
        self.btn_clear_dimension.clicked.connect(self.clear_dimension_annotation)
        layout_dimension.addWidget(self.btn_clear_dimension)

        top_groups_layout.addWidget(group_dimension)

        # ------------------ 描述工具分组 ------------------
        group_description = QGroupBox("描述工具")
        layout_description = QHBoxLayout(group_description)

        self.btn_building_desc = QPushButton("古建筑描述工具")
        self.btn_building_desc.clicked.connect(self.open_building_description)
        layout_description.addWidget(self.btn_building_desc)

        self.btn_stele_desc = QPushButton("碑刻描述工具")
        self.btn_stele_desc.clicked.connect(self.open_stele_description)
        layout_description.addWidget(self.btn_stele_desc)

        top_groups_layout.addWidget(group_description)

        # ------------------ CAD绘图分组 ------------------
        group_cad = QGroupBox("CAD绘图")
        layout_cad = QHBoxLayout(group_cad)

        self.btn_draw_line = QPushButton("绘制直线")
        self.btn_draw_line.clicked.connect(self.start_draw_line)
        layout_cad.addWidget(self.btn_draw_line)

        self.btn_point_coord = QPushButton("点坐标")
        self.btn_point_coord.clicked.connect(self.start_point_coord)
        layout_cad.addWidget(self.btn_point_coord)

        self.btn_erase_line = QPushButton("删除直线")
        self.btn_erase_line.clicked.connect(self.start_erase_line)
        layout_cad.addWidget(self.btn_erase_line)

        # 颜色选择下拉框
        self.color_combo = QComboBox()
        self.color_combo.addItems(['蓝色', '红色', '绿色', '黄色', '黑色', '白色'])
        self.color_combo.currentTextChanged.connect(self.change_cad_color)
        layout_cad.addWidget(QLabel("颜色:"))
        layout_cad.addWidget(self.color_combo)

        self.btn_clear_cad = QPushButton("清空CAD")
        self.btn_clear_cad.clicked.connect(self.clear_cad)
        layout_cad.addWidget(self.btn_clear_cad)

        self.btn_export_cad = QPushButton("导出CAD")
        self.btn_export_cad.clicked.connect(self.export_cad)
        layout_cad.addWidget(self.btn_export_cad)

        top_groups_layout.addWidget(group_cad)

        # ------------------ 版本信息按钮 ------------------
        self.btn_version_info = QPushButton("版本信息")
        self.btn_version_info.clicked.connect(self.show_version_info)
        top_groups_layout.addWidget(self.btn_version_info)

        # 将分组布局放到主 Layout
        main_layout.addLayout(top_groups_layout)

        # =========================================================================
        # 主体：左侧影像，右侧坐标/标注列表
        # =========================================================================
        body_layout = QHBoxLayout()
        main_layout.addLayout(body_layout, stretch=1)

        # ============ 左侧：影像区域 ============
        self.canvas = ImageCanvas()
        self.canvas.mpl_connect("button_press_event", self.on_click_image)
        body_layout.addWidget(self.canvas, stretch=5)  # 增加图像区域的比例

        # ============ 右侧：坐标/标注表格 ============
        right_layout = QVBoxLayout()

        # 坐标列表
        self.label_coords = QLabel("点选坐标列表：")
        right_layout.addWidget(self.label_coords)

        self.table_coords = QTableWidget()
        self.table_coords.setColumnCount(6)
        self.table_coords.setHorizontalHeaderLabels([
            "序号", "测点类型", "纬度", "经度", "海拔高程", "测点说明"
        ])
        self.table_coords.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.table_coords, stretch=1)

        # 标注列表
        self.label_labels = QLabel("标注栏：")
        right_layout.addWidget(self.label_labels)

        self.table_labels = QTableWidget()
        self.table_labels.setColumnCount(2)
        self.table_labels.setHorizontalHeaderLabels(["标注序号", "内容"])
        self.table_labels.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.table_labels, stretch=1)

        body_layout.addLayout(right_layout, stretch=2)  # 保持右侧区域比例为2

        # 初始化标注管理器/坐标拾取器/多边形绘制器/尺寸标注器
        self.label_manager = LabelManager(self.canvas, self.table_labels)
        self.coordinate_picker = CoordinatePicker(
            self.canvas,
            self.table_coords,
            dataset_dom=self.dataset_dom,
            dataset_dsm=self.dataset_dsm
        )
        self.polygon_drawer = PolygonDrawer(self.canvas)
        self.dimension_annotator = DimensionAnnotator(self.canvas)
        self.cad_drawer = CADDrawer(self.canvas)  # 初始化CAD绘图器

    # =========================================================================
    #  事件与功能函数
    # =========================================================================

    def keyPressEvent(self, event):
        """
        监听 ESC 键：退出标注模式、坐标拾取模式、多边形绘制模式、以及尺寸标注模式
        """
        if event.key() == Qt.Key_Escape:
            if self.cad_drawer.is_drawing:
                self.cad_drawer.stop_drawing()
                QMessageBox.information(self, "提示", "已退出CAD绘图模式！")
                self.update_status("")
                return
            if self.dimension_annotator.active:
                self.dimension_annotator.stop_dimension_mode()
                QMessageBox.information(self, "提示", "已退出尺寸标注模式！")
                self.update_status("")
                return
            if self.polygon_drawer.is_drawing_polygon:
                self.polygon_drawer.stop_polygon_mode()
                QMessageBox.information(self, "提示", "已结束多边形绘制！")
                self.update_status("")
                return
            if self.label_manager.is_labeling:
                self.label_manager.stop_labeling()
                QMessageBox.information(self, "提示", "已退出标注模式！")
                self.update_status("")
                return
            if self.coordinate_picker.is_in_select_mode():
                self.coordinate_picker.toggle_coordinate_pick()
                QMessageBox.information(self, "提示", "已退出拾取坐标模式！")
                self.update_status("")
                return
        super().keyPressEvent(event)

    def on_click_image(self, event):
        """
        根据当前状态进行处理：
         1) 若处于坐标拾取模式 => return，让 coordinate_picker 自行处理
         2) 若处于多边形绘制模式 => return，让 polygon_drawer 自行处理
         3) 若处于标注模式 => 弹出标注对话框
         4) 其他状态 => 不处理
        """
        # 坐标拾取
        if self.coordinate_picker.is_in_select_mode():
            return
        # 多边形绘制
        if self.polygon_drawer.is_drawing_polygon:
            return
        # 标注模式
        if self.label_manager.is_labeling:
            if not self.dataset_dom:
                return
            if event.inaxes != self.canvas.ax:
                return
            xdata, ydata = event.xdata, event.ydata
            if xdata is None or ydata is None:
                return
            dlg = LabelDialog(self)
            if dlg.exec_() == dlg.Accepted:
                order_str, content_str = dlg.get_data()
                if order_str and content_str:
                    self.label_manager.add_annotation(xdata, ydata, order_str, content_str)

    # =========================================================================
    #  坐标拾取功能
    # =========================================================================

    def toggle_coordinate_pick(self):
        """
        切换坐标拾取模式
        """
        was_selecting = self.coordinate_picker.is_in_select_mode()
        self.coordinate_picker.toggle_coordinate_pick()
        if not was_selecting and self.coordinate_picker.is_in_select_mode():
            QMessageBox.information(self, "提示", "已进入坐标拾取模式。按 ESC 键可退出该模式。")
            self.update_status("坐标拾取模式")

    def clear_coords(self):
        """
        清空坐标列表
        """
        self.table_coords.setRowCount(0)
        self.coordinate_picker.clear_coords()

    def export_coords(self):
        """
        导出当前拾取的坐标列表到 CSV 文件
        """
        try:
            coords_to_export = self.coordinate_picker.get_coords()
            if not coords_to_export:
                QMessageBox.warning(self, "导出坐标", "当前没有拾取的坐标，无法导出！")
                return
            out_path, _ = QFileDialog.getSaveFileName(self, "导出坐标", "", "CSV Files (*.csv)")
            if not out_path:
                return
            export_csv(coords_to_export, out_path)
            QMessageBox.information(self, "导出成功", f"坐标已成功导出到：{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出坐标时发生错误：{str(e)}")

    # =========================================================================
    #  标注功能
    # =========================================================================

    def toggle_label_mode(self):
        """
        切换标注模式
        """
        if not self.label_manager.is_labeling:
            # 若坐标拾取模式，先关闭
            if self.coordinate_picker.is_in_select_mode():
                self.coordinate_picker.toggle_coordinate_pick()
            # 若多边形绘制模式，先关闭
            if self.polygon_drawer.is_drawing_polygon:
                self.polygon_drawer.stop_polygon_mode()
            self.label_manager.start_labeling()
            QMessageBox.information(self, "提示", "已进入标注模式，点击图像可创建标注。\n按ESC键退出标注模式。")
            self.update_status("标注模式")
        else:
            self.label_manager.stop_labeling()
            QMessageBox.information(self, "提示", "已退出标注模式！")
            self.update_status("")

    def clear_label(self):
        """
        清空所有标注
        """
        self.label_manager.clear_annotations()

    def export_label(self):
        """
        导出带标注的图像
        """
        out_path, _ = QFileDialog.getSaveFileName(self, "导出标注图像", "", "PNG Files (*.png)")
        if out_path:
            self.label_manager.export_labeled_image(out_path)

    # =========================================================================
    #  多边形绘制功能
    # =========================================================================

    def start_draw_polygon(self):
        """
        点击"开始绘制多边形"按钮：
         - 先退出坐标拾取/标注模式，避免冲突
         - 进入多边形绘制模式
        """
        if self.coordinate_picker.is_in_select_mode():
            self.coordinate_picker.toggle_coordinate_pick()
        if self.label_manager.is_labeling:
            self.label_manager.stop_labeling()
        self.polygon_drawer.start_polygon_mode()
        QMessageBox.information(self, "提示", "已进入多边形绘制模式：\n左键依次下顶点，右键或按ESC可结束。")

    def clear_polygon(self):
        """
        清空已绘制的多边形
        注意：在 polygon_drawer 内部使用 line.remove() 卸载线条，避免出现 remove 错误。
        """
        self.polygon_drawer.clear_polygons()
        QMessageBox.information(self, "提示", "已清空多边形。")

    # =========================================================================
    #  尺寸标注功能
    # =========================================================================

    def start_dimension_annotation(self):
        """
        开始尺寸标注模式：
         - 退出坐标拾取、标注和多边形绘制模式（避免冲突）
         - 进入尺寸标注模式，等待用户依次点击两个点进行测距
        """
        if self.coordinate_picker.is_in_select_mode():
            self.coordinate_picker.toggle_coordinate_pick()
        if self.label_manager.is_labeling:
            self.label_manager.stop_labeling()
        if self.polygon_drawer.is_drawing_polygon:
            self.polygon_drawer.stop_polygon_mode()
        self.dimension_annotator.start_dimension_mode()
        self.update_status("尺寸标注模式")

    def clear_dimension_annotation(self):
        """
        清空所有已绘制的尺寸标注
        """
        self.dimension_annotator.clear_annotations()
        QMessageBox.information(self, "提示", "已清空尺寸标注。")

    # =========================================================================
    #  数据加载和清空
    # =========================================================================

    def load_tif_dom(self):
        """
        导入DOM
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 DOM 文件", "", "TIF Files (*.tif *.tiff)")
        if file_path:
            try:
                self.dataset_dom, image_array = read_orthophoto(file_path)
                self.transform = self.dataset_dom.transform
                image_data = image_array.transpose((1, 2, 0))  # [height, width, channels]
                self.canvas.show_image(image_data, self.transform)
                self.coordinate_picker.set_dataset_dom(self.dataset_dom)
            except Exception as e:
                QMessageBox.critical(self, "读取错误", f"无法读取DOM文件：{str(e)}")

    def load_tif_dsm(self):
        """
        导入DSM文件(含高程信息)
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 DSM 文件", "", "TIF Files (*.tif *.tiff)")
        if file_path:
            try:
                dsm_dataset, _ = read_orthophoto(file_path)
                self.dataset_dsm = dsm_dataset
                self.coordinate_picker.set_dataset_dsm(self.dataset_dsm)
                QMessageBox.information(self, "提示", "已成功加载DSM文件，可获取海拔信息。")
            except Exception as e:
                QMessageBox.critical(self, "读取错误", f"无法读取DSM文件：{str(e)}")

    def clear_all(self):
        """
        清空影像、坐标和标注、多边形
         先清空多边形，再清标注与坐标，然后再 cla()
        """
        try:
            # 1) 清空多边形
            if self.polygon_drawer:
                self.polygon_drawer.clear_polygons()

            # 2) 清空标注与坐标
            self.label_manager.clear_annotations()
            self.coordinate_picker.clear_coords()
            self.table_coords.setRowCount(0)

            # 3) 若要把图像也清掉，则再 ax.cla()
            if self.canvas.ax is not None:
                self.canvas.ax.cla()
                self.canvas.draw()

            # 4) 释放 DOM / DSM
            if self.dataset_dom:
                self.dataset_dom.close()
                self.dataset_dom = None
            if self.dataset_dsm:
                self.dataset_dsm.close()
                self.dataset_dsm = None

            self.transform = None
            self.coords_list.clear()
            self.update_status("")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")

    # =========================================================================
    #  版本信息弹窗
    # =========================================================================

    def show_version_info(self):
        version_info = (
            "版本号：Ver. 0.90\n"
            "开发：嘉祥县文物保护中心\n\n"
            "新增功能：\n"
            "Ver 0.90\n"
            "1、调整了按钮布局，优化了用户界面\n"
            "2、增加了CAD绘图功能\n"
            "3、修复了一些已知问题\n"
            "Ver 0.80\n"
            "1、优化了影像显示功能，保持正确的宽高比\n"
            "2、提升了影像显示性能\n"
            "Ver 0.70\n"
            "1、增加古建筑描述模块\n"
            "2、增加碑刻描述模块\n"
            "Ver 0.60\n"
            "1、优化了UI布局\n"
            "2、增加了根据正射影像进行尺寸标注的功能\n"
            "3、增加了根据正射影像进行坐标拾取的功能\n"
            "4、增加了根据正射影像进行多边形绘制的功能\n"
            "5、增加了根据正射影像进行标注的功能\n"
        )
        QMessageBox.information(self, "版本信息", version_info)

    def open_building_description(self):
        """打开古建筑描述工具"""
        building_description.main()

    def open_stele_description(self):
        """打开碑刻描述工具"""
        stele_description.main()

    def start_draw_line(self):
        """开始直线绘制模式"""
        self.cad_drawer.start_line_mode()
        self.update_status("已进入直线绘制模式，点击两次生成直线，按ESC退出")
        
    def start_erase_line(self):
        """开始TR模式"""
        self.cad_drawer.start_erase_mode()
        self.update_status("已进入TR模式：\n1. 先点击作为剪切线的直线\n2. 再点击要剪切的直线\n3. 按ESC退出")
        
    def clear_cad(self):
        """清空CAD图层"""
        self.cad_drawer.clear_shapes()
        self.update_status("已清空CAD图层")
        
    def export_cad(self):
        """导出CAD图层"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出CAD图层",
            "",
            "PNG文件 (*.png)"
        )
        if file_path:
            self.cad_drawer.export_cad_layer(file_path)
            self.update_status(f"CAD图层已导出至: {file_path}")

    def change_cad_color(self, color_name):
        """更改CAD绘图颜色"""
        self.cad_drawer.set_color(color_name)
        self.update_status(f"已切换CAD绘图颜色为: {color_name}")

    def start_point_coord(self):
        """开始点坐标模式"""
        self.cad_drawer.start_point_coord_mode()
        self.update_status("已进入点坐标模式，点击任意位置显示坐标，按ESC退出")

    # =========================================================================
    #  辅助
    # =========================================================================

    def update_status(self, message):
        """
        更新状态栏信息
        """
        self.status_bar.showMessage(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())