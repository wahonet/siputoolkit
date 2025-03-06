# label_manager.py
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox
)

class LabelDialog(QDialog):
    """
    用于创建标注时的对话框，输入“标注序号”和“内容”
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建标注")

        self.order_edit = QLineEdit()
        self.content_edit = QLineEdit()

        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("标注序号："))
        layout.addWidget(self.order_edit)
        layout.addWidget(QLabel("标注内容："))
        layout.addWidget(self.content_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        """
        返回 (标注序号文本, 标注内容文本)
        """
        return self.order_edit.text().strip(), self.content_edit.text().strip()


class LabelManager:
    """
    负责管理标注信息及其导出逻辑
    """
    def __init__(self, canvas, table_widget):
        """
        :param canvas: ImageCanvas 对象
        :param table_widget: QTableWidget 显示标注列表
        """
        self.canvas = canvas
        self.ax = self.canvas.ax
        self.table_widget = table_widget

        # 每条标注: { x, y, order, content, text_obj }
        self.annotations = []
        self.is_labeling = False
        self._temp_text_artist = None  # 汇总文本对象

        # 设置表格列
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["标注序号", "内容"])

        self.ax.set_title("")
        self.ax.axis('off')

    def start_labeling(self):
        """进入标注模式"""
        self.is_labeling = True
        self.canvas.set_label_mode(True)

    def stop_labeling(self):
        """退出标注模式"""
        self.is_labeling = False
        self.canvas.set_label_mode(False)

    def add_annotation(self, x, y, order_str, content_str):
        """
        在图上绘制一条标注并存储
        """
        try:
            if not order_str or not content_str:
                raise ValueError("标注序号和内容不能为空")

            text_obj = self.ax.text(
                x, y,
                f"{order_str}",
                fontsize=10,
                color='red',
                transform=self.ax.transData,
                ha='center',
                va='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="red", alpha=0.5)
            )
            one_ann = {'x': x, 'y': y, 'order': order_str, 'content': content_str, 'text_obj': text_obj}
            self.annotations.append(one_ann)

            row_index = self.table_widget.rowCount()
            self.table_widget.insertRow(row_index)
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(str(order_str)))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(str(content_str)))

            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(None, "标注错误", f"添加标注时发生错误：{str(e)}")

    def clear_annotations(self):
        """清除所有标注和表格内容"""
        for ann in self.annotations:
            try:
                ann['text_obj'].remove()
            except Exception:
                pass
        self.annotations.clear()
        self.table_widget.setRowCount(0)
        self.canvas.draw()

    def export_labeled_image(self, out_path):
        """
        导出带标注图像，临时添加比例尺信息
        """
        try:
            if (not self.annotations) or (self.canvas.image_data is None):
                QMessageBox.warning(None, "提示", "无图像或无标注，无法导出！")
                return

            fig = self.canvas.fig
            ax = self.canvas.ax

            if self._temp_text_artist:
                self._temp_text_artist.remove()
                self._temp_text_artist = None

            lines = [f"{idx + 1}. {ann['content']}" for idx, ann in enumerate(self.annotations)]
            final_text = "\n".join(lines).strip()
            if final_text:
                self._temp_text_artist = ax.text(
                    0.01, 0.01,
                    final_text,
                    transform=ax.transAxes,
                    va='bottom',
                    ha='left',
                    fontsize=14,
                    color='black',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.3')
                )

            fig.savefig(out_path, dpi=100, bbox_inches='tight', pad_inches=0.05)
            QMessageBox.information(None, "提示", f"已导出带标注图像：{out_path}")

        except Exception as e:
            QMessageBox.critical(None, "导出失败", f"导出图像时发生错误：{str(e)}")
