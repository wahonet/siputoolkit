# image_canvas.py
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ImageCanvas(FigureCanvas):
    """
    负责展示影像，并提供鼠标滚轮缩放及中键拖拽功能
    """

    def __init__(self):
        # 创建图形对象时设置更好的性能参数
        self.fig = Figure(dpi=100)
        self.fig.patch.set_facecolor('white')  # 设置背景色
        super().__init__(self.fig)  # 调用父类构造方法
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_position([0, 0, 1, 1])  # 让图像填满整个画布
        
        self.image_data = None
        self.transform = None  # 存储影像变换信息
        self.enable_pan = True
        self.is_panning = False
        self.north_arrow = None  # 用于存放指北针对象

        # 绑定事件
        self.mpl_connect('scroll_event', self.on_scroll)
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('motion_notify_event', self.on_move)
        self.mpl_connect('button_release_event', self.on_release)

        # 性能优化设置
        self.fig.set_tight_layout(False)  # 禁用tight_layout以避免自动调整
        self.ax.set_adjustable('box')
        
        # 禁用不必要的交互功能以提高性能
        self.ax.set_navigate(False)
        self.ax.set_autoscale_on(False)

    def show_image(self, image_array, transform):
        """
        显示传入的影像数据（格式为 H x W x 波段，一般为 RGB 或 RGBA）
        并设置对应的变换信息，同时绘制指北针
        """
        self.transform = transform  # 设置 transform 属性
        self.ax.clear()
        self.image_data = image_array
        
        # 使用性能更好的显示设置，保持原始比例
        self.ax.imshow(self.image_data, interpolation='nearest', aspect='equal')
        self.ax.axis('off')
        
        # 添加指北针
        self.add_north_arrow()
        
        # 使用draw_idle()代替draw()来提高性能
        self.draw_idle()

    def add_north_arrow(self):
        """
        在图像右上角添加指北针（红色箭头和"N"标识）。
        使用 Axes 坐标系（0–1）进行定位。
        """
        # 若已存在则先移除旧对象
        if self.north_arrow is not None:
            try:
                self.north_arrow.remove()
            except Exception:
                pass
            self.north_arrow = None
        # 在 Axes 坐标系中添加箭头：位置为右上角
        self.north_arrow = self.ax.annotate(
            '', xy=(0.98, 0.90), xytext=(0.98, 0.80),
            xycoords='axes fraction',
            arrowprops=dict(facecolor='red', edgecolor='red', width=2, headwidth=10)
        )
        # 在箭头上侧添加 "N" 标签
        self.ax.text(0.98, 0.95, "N", transform=self.ax.transAxes,
                     ha='center', va='center', fontsize=14, color='red')

    def on_scroll(self, event):
        if self.image_data is None or event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        # 使用更平滑的缩放比例
        base_scale = 1.05
        scale_factor = base_scale if event.button == 'up' else 1 / base_scale

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        new_xmin = x - (x - cur_xlim[0]) / scale_factor
        new_xmax = x + (cur_xlim[1] - x) / scale_factor
        new_ymin = y - (y - cur_ylim[0]) / scale_factor
        new_ymax = y + (cur_ylim[1] - y) / scale_factor

        self.ax.set_xlim(new_xmin, new_xmax)
        self.ax.set_ylim(new_ymin, new_ymax)

        # 使用draw_idle()代替draw()来提高性能
        self.draw_idle()

    def on_press(self, event):
        """
        鼠标中键按下时，若允许拖拽则进入拖拽状态
        """
        if event.button == 2 and self.enable_pan:
            self.is_panning = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata

    def on_move(self, event):
        """
        鼠标移动时，若处于拖拽状态则更新图像边界
        """
        if not self.is_panning or event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        dx = event.xdata - self.pan_start_x
        dy = event.ydata - self.pan_start_y

        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        self.ax.set_xlim(x_min - dx, x_max - dx)
        self.ax.set_ylim(y_min - dy, y_max - dy)

        self.pan_start_x = event.xdata
        self.pan_start_y = event.ydata
        
        # 使用draw_idle()代替draw()来提高性能
        self.draw_idle()

    def on_release(self, event):
        """
        鼠标中键释放时结束拖拽
        """
        if event.button == 2 and self.is_panning:
            self.is_panning = False
            self.pan_start_x = None
            self.pan_start_y = None

    def set_label_mode(self, enabled):
        """
        设置是否启用标注模式
        """
        self.enable_pan = not enabled  # 启用标注时禁用拖拽