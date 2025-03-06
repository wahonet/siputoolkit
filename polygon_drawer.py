"""
polygon_drawer.py

实现在正射影像上交互式绘制多边形：
-  left-click：依次添加顶点
-  right-click 或按 Esc：结束绘制
-  在图像上用红色线条显示已绘制的多边形轮廓
-  新增：在清空多边形时更稳健，避免移除线条时程序崩溃
"""

from PyQt5.QtWidgets import QMessageBox
from matplotlib.lines import Line2D

class PolygonDrawer:
    def __init__(self, canvas):
        """
        :param canvas: ImageCanvas 对象
        """
        self.canvas = canvas
        self.ax = self.canvas.ax

        # 是否处于多边形绘制模式
        self._is_drawing_polygon = False

        # 用于记录当前正在绘制的多边形的顶点列表 [(x1, y1), (x2, y2), ...]
        self.current_polygon_points = []

        # 连接 ID（mpl_connect 返回）
        self.cid_click = None

        # 用于 Matplotlib 显示当前多边形过程的 line
        self.drawing_line = None

        # 已经完成的多边形线段对象，用于后续清空
        self.polygon_patches = []

    @property
    def is_drawing_polygon(self):
        return self._is_drawing_polygon

    @is_drawing_polygon.setter
    def is_drawing_polygon(self, val):
        self._is_drawing_polygon = val

    def start_polygon_mode(self):
        """
        进入多边形绘制模式：绑定鼠标事件、初始化顶点列表和绘制线
        """
        if self.is_drawing_polygon:
            return

        self.is_drawing_polygon = True
        self.current_polygon_points = []

        # 连接鼠标点击事件
        self.cid_click = self.canvas.mpl_connect("button_press_event", self.on_mouse_click)

        # 创建红色虚线+小圆点的线对象，用于显示多边形绘制过程
        self.drawing_line = Line2D([], [], color="red", linestyle="--", marker="o")
        self.ax.add_line(self.drawing_line)
        self.canvas.draw()

    def stop_polygon_mode(self):
        """
        退出多边形绘制模式：若点数 >= 3，自动闭合多边形并保持在图中；否则移除当前线条
        """
        if not self.is_drawing_polygon:
            return

        self.is_drawing_polygon = False

        # 断开鼠标事件
        if self.cid_click is not None:
            self.canvas.mpl_disconnect(self.cid_click)
            self.cid_click = None

        # 若已足够点数，则闭合多边形
        if len(self.current_polygon_points) >= 3:
            self.close_polygon()
        else:
            # 不够 3 个点，说明不构成多边形，移除临时线
            if self.drawing_line:
                try:
                    self.drawing_line.remove()
                except Exception:
                    pass

        self.current_polygon_points = []
        self.drawing_line = None
        self.canvas.draw()

    def on_mouse_click(self, event):
        """
        处理鼠标点击：
        - 左键：在图上添加一个顶点
        - 右键：结束多边形绘制
        """
        if not self.is_drawing_polygon:
            return

        # 若鼠标右键（button=3），则结束
        if event.button == 3:
            self.stop_polygon_mode()
            return

        # 仅处理鼠标左键（button=1）
        if event.button != 1:
            return

        # 确认点击发生在坐标轴上
        if event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        # 添加一个新顶点
        self.current_polygon_points.append((x, y))

        # 更新临时线对象
        xs = [p[0] for p in self.current_polygon_points]
        ys = [p[1] for p in self.current_polygon_points]
        self.drawing_line.set_data(xs, ys)

        self.canvas.draw()

    def close_polygon(self):
        """
        将当前多边形首尾相连，以闭合形状，并将该线条对象保存到 polygon_patches
        """
        if len(self.current_polygon_points) < 3:
            return

        # 闭合：将首点再追加一次，让最后画回首点
        xs = [p[0] for p in self.current_polygon_points]
        ys = [p[1] for p in self.current_polygon_points]
        xs.append(xs[0])
        ys.append(ys[0])

        # 用 drawing_line 表示闭合多边形
        self.drawing_line.set_data(xs, ys)

        # 存储到 polygon_patches，方便后续清空
        self.polygon_patches.append(self.drawing_line)

        self.canvas.draw()

    def clear_polygons(self):
        """
        清空已绘制的多边形，并结束绘制状态（若在绘制中）。
        通过 line.remove() 来移除，从而避免 'ArtistList has no attribute remove' 。
        """
        # 若仍在绘制，先 stop
        if self.is_drawing_polygon:
            self.stop_polygon_mode()

        # 移除已完成的多边形
        for line_obj in self.polygon_patches:
            try:
                line_obj.remove()  # 调用 line 对象自身的 remove()
            except Exception:
                pass
        self.polygon_patches.clear()

        # 移除正在绘制线
        if self.drawing_line:
            try:
                self.drawing_line.remove()
            except Exception:
                pass
            self.drawing_line = None

        self.current_polygon_points = []
        self.canvas.draw()

