# dimension_annotator.py
import math
from PyQt5.QtWidgets import QMessageBox
from matplotlib.lines import Line2D

class DimensionAnnotator:
    """
    实现尺寸标注功能：
    用户依次点击两点，系统根据 ImageCanvas 的 transform 参数计算两点间真实距离，
    并在图上绘制尺寸线及标注距离。
    """
    def __init__(self, canvas):
        self.canvas = canvas
        self.ax = self.canvas.ax
        self.active = False
        self.points = []       # 存放点击的2个点 (x, y)
        self.annotations = []  # 存放已绘制的尺寸标注（线和文字）
        self.cid_click = None

    def start_dimension_mode(self):
        """
        进入尺寸标注模式，绑定鼠标点击事件
        """
        if self.active:
            return
        self.active = True
        self.points = []
        self.cid_click = self.canvas.mpl_connect("button_press_event", self.on_click)
        QMessageBox.information(None, "提示", "已进入尺寸标注模式：\n请依次点击两点进行测距，完成后自动绘制标注。\n按 ESC 退出该模式。")

    def stop_dimension_mode(self):
        """
        退出尺寸标注模式，解绑事件
        """
        if self.active:
            if self.cid_click is not None:
                self.canvas.mpl_disconnect(self.cid_click)
                self.cid_click = None
            self.active = False
            self.points = []

    def on_click(self, event):
        """
        处理鼠标左键点击，记录2个点后计算距离并绘制标注
        """
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        self.points.append((x, y))
        if len(self.points) == 2:
            (x1, y1), (x2, y2) = self.points
            dx = x2 - x1
            dy = y2 - y1
            if self.canvas.transform is not None:
                pixel_size_x = abs(self.canvas.transform.a)
                pixel_size_y = abs(self.canvas.transform.e)
                distance = math.sqrt((dx * pixel_size_x)**2 + (dy * pixel_size_y)**2)
                distance_str = f"{distance:.2f} m"
            else:
                distance = math.sqrt(dx**2 + dy**2)
                distance_str = f"{distance:.2f} px"
            line = Line2D([x1, x2], [y1, y2], color="blue", linewidth=2)
            self.ax.add_line(line)
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            text = self.ax.text(mid_x, mid_y, distance_str, fontsize=12, color="blue",
                                backgroundcolor="white", ha="center", va="bottom")
            self.annotations.append((line, text))
            self.canvas.draw()
            self.points = []

    def clear_annotations(self):
        """
        清除所有已绘制的尺寸标注
        """
        for line, text in self.annotations:
            try:
                line.remove()
            except Exception:
                pass
            try:
                text.remove()
            except Exception:
                pass
        self.annotations.clear()
        self.canvas.draw()