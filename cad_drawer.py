"""
cad_drawer.py

CAD绘图模块，提供基本的绘图功能，包括：
1. 直线绘制（点击两次生成直线，带自动吸附，支持连续绘制）
2. 导出CAD图层
3. 图层可见性控制
4. 直线删除功能
5. 颜色选择功能
6. 坐标标注功能（仅蓝色线条显示）
"""

import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from PIL import Image
import io
from orthophoto_utils import decimal_degrees_to_dms, transform_coordinate

class CADDrawer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.ax = canvas.ax
        self.is_drawing = False
        self.current_tool = None
        self.current_shape = None
        self.start_point = None
        self.end_point = None
        self.shapes = []  # 存储所有绘制的图形
        self.coord_labels = []  # 存储坐标标注
        self.snap_threshold = 10  # 自动吸附阈值（像素）
        self.is_first_click = True  # 标记是否是第一次点击
        self.temp_line = None  # 临时直线对象
        self.current_color = '#0000FF'  # 默认蓝色
        self.available_colors = {
            '蓝色': '#0000FF',
            '红色': '#FF0000',
            '绿色': '#00FF00',
            '黄色': '#FFFF00',
            '黑色': '#000000',
            '白色': '#FFFFFF'
        }
        self.current_mode = None
        self.current_line = None
        self.cutting_line = None
        self._connect_events()
        
    def set_color(self, color_name):
        """设置当前绘图颜色"""
        if color_name in self.available_colors:
            self.current_color = self.available_colors[color_name]
        
    def set_visibility(self, visible):
        """设置CAD图层的可见性"""
        for shape in self.shapes:
            shape.set_visible(visible)
        if self.temp_line:
            self.temp_line.set_visible(visible)
        for label in self.coord_labels:
            label.set_visible(visible)
        self.canvas.draw_idle()
        
    def start_line_mode(self):
        """开始直线绘制模式"""
        self.current_tool = 'line'
        self.is_drawing = True
        self.is_first_click = True
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
    def start_erase_mode(self):
        """开始删除模式"""
        self.current_tool = 'erase'
        self.is_drawing = True
        self.canvas.mpl_connect('button_press_event', self.on_press)
        
    def start_point_coord_mode(self):
        """开始点坐标模式"""
        self.current_tool = 'point_coord'
        self.is_drawing = True
        self.canvas.mpl_connect('button_press_event', self.on_press)
        
    def add_coord_label(self, x, y):
        """添加坐标标注"""
        if hasattr(self.canvas, 'transform') and self.canvas.transform is not None:
            try:
                # 转换坐标到经纬度
                lon, lat = transform_coordinate(
                    x, y,
                    self.canvas.transform,
                    src_crs="EPSG:4548",
                    dst_crs="EPSG:4490"
                )
                # 转换为度分秒格式
                lon_dms = decimal_degrees_to_dms(lon, is_lat=False)
                lat_dms = decimal_degrees_to_dms(lat, is_lat=True)
                # 格式化显示文本
                label_text = f'{lon_dms}\n{lat_dms}'
                # 添加坐标标注
                label = self.ax.text(x, y, label_text, 
                                   color='black',
                                   fontsize=8,
                                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                                   ha='left', va='bottom')
                self.coord_labels.append(label)
                self.canvas.draw_idle()
            except Exception as e:
                print(f"坐标转换错误: {str(e)}")
                # 如果转换失败，显示原始坐标
                label_text = f'X: {x:.4f}\nY: {y:.4f}'
                label = self.ax.text(x, y, label_text, 
                                   color='black',
                                   fontsize=8,
                                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                                   ha='left', va='bottom')
                self.coord_labels.append(label)
                self.canvas.draw_idle()
        
    def find_nearest_point(self, x, y):
        """查找最近的点进行自动吸附"""
        if not self.shapes:
            return (x, y), None
            
        min_dist = float('inf')
        nearest_point = (x, y)
        nearest_shape = None
        
        for shape in self.shapes:
            if isinstance(shape, Line2D):
                # 检查线段的两个端点
                xdata, ydata = shape.get_data()
                for px, py in zip(xdata, ydata):
                    dist = np.sqrt((px - x)**2 + (py - y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_point = (float(px), float(py))  # 确保是元组
                        nearest_shape = shape
                    
        # 如果距离小于阈值，则吸附到最近的点
        if min_dist <= self.snap_threshold:
            return nearest_point, nearest_shape
        return (float(x), float(y)), None  # 确保是元组
        
    def on_press(self, event):
        """处理鼠标按下事件"""
        if not self.is_drawing or event.inaxes != self.ax:
            return
            
        if self.current_tool == 'point_coord':
            # 点坐标模式：直接添加坐标标注
            self.add_coord_label(event.xdata, event.ydata)
            return
            
        if self.current_tool == 'erase':
            # 删除模式：查找最近的图形并删除
            _, nearest_shape = self.find_nearest_point(event.xdata, event.ydata)
            if nearest_shape:
                # 删除图形
                nearest_shape.remove()
                self.shapes.remove(nearest_shape)
                # 删除相关的坐标标注
                for label in self.coord_labels[:]:
                    if isinstance(nearest_shape, Line2D):
                        xdata, ydata = nearest_shape.get_data()
                        if label.get_position() == (xdata[0], ydata[0]):
                            label.remove()
                            self.coord_labels.remove(label)
                self.canvas.draw_idle()
            return
            
        if self.current_tool == 'line':
            if self.is_first_click:
                # 第一次点击，记录起点
                self.start_point, _ = self.find_nearest_point(event.xdata, event.ydata)
                self.is_first_click = False
            else:
                # 第二次点击，完成直线绘制
                end_point, _ = self.find_nearest_point(event.xdata, event.ydata)
                line = Line2D([self.start_point[0], end_point[0]], 
                            [self.start_point[1], end_point[1]], 
                            color=self.current_color, linewidth=1)
                self.ax.add_artist(line)
                self.shapes.append(line)
                
                # 清除临时直线
                if self.temp_line:
                    self.temp_line.remove()
                    self.temp_line = None
                    
                # 更新起点为终点，实现连续绘制
                self.start_point = end_point
                self.canvas.draw_idle()
                
    def on_motion(self, event):
        """处理鼠标移动事件"""
        if not self.is_drawing or event.inaxes != self.ax:
            return
            
        if self.current_tool == 'line' and not self.is_first_click:
            # 更新临时直线
            if self.temp_line:
                self.temp_line.remove()
            end_point, _ = self.find_nearest_point(event.xdata, event.ydata)
            self.temp_line = Line2D([self.start_point[0], end_point[0]], 
                                  [self.start_point[1], end_point[1]], 
                                  color='red', linewidth=1, linestyle='--')
            self.ax.add_artist(self.temp_line)
            self.canvas.draw_idle()
            
    def clear_shapes(self):
        """清除所有绘制的图形"""
        for shape in self.shapes:
            shape.remove()
        self.shapes.clear()
        if self.temp_line:
            self.temp_line.remove()
            self.temp_line = None
        # 清除所有坐标标注
        for label in self.coord_labels:
            label.remove()
        self.coord_labels.clear()
        self.canvas.draw_idle()
        
    def stop_drawing(self):
        """停止绘图模式"""
        self.is_drawing = False
        self.current_tool = None
        self.is_first_click = True
        self.start_point = None
        if self.temp_line:
            self.temp_line.remove()
            self.temp_line = None
            
    def calculate_scale(self):
        """计算比例尺"""
        if not hasattr(self.canvas, 'transform') or self.canvas.transform is None:
            return None
            
        # 获取图像边界
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        
        # 计算图像宽度（像素）
        width_pixels = xmax - xmin
        
        # 计算图像中心点
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        
        try:
            # 转换中心点坐标
            lon1, lat1 = transform_coordinate(center_x, center_y, self.canvas.transform)
            # 转换图像右边界坐标
            lon2, lat2 = transform_coordinate(xmax, center_y, self.canvas.transform)
            
            # 计算两点间的距离（米）
            from pyproj import Geod
            geod = Geod(ellps='WGS84')
            _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
            
            # 计算比例尺
            scale = distance / width_pixels  # 米/像素
            return scale
        except Exception as e:
            print(f"计算比例尺错误: {str(e)}")
            return None

    def draw_scale_bar(self, ax, scale):
        """绘制比例尺"""
        if scale is None:
            return
            
        # 设置比例尺参数
        scale_length = 200  # 比例尺长度（像素）
        bar_height = 15  # 比例尺高度（像素）
        
        # 计算比例尺位置（中间偏下）
        x_start = 0.5 - 0.1  # 距离左边界的比例（居中）
        y_start = 0.1  # 距离下边界的比例
        
        # 获取图像尺寸
        bbox = ax.get_window_extent().transformed(ax.figure.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        
        # 计算实际像素位置
        x_pixels = x_start * width
        y_pixels = y_start * height
        
        # 绘制比例尺
        # 主刻度线
        ax.plot([x_pixels, x_pixels + scale_length], [y_pixels, y_pixels], 
                color='black', linewidth=1)
        
        # 刻度标记
        for i in range(0, scale_length + 1, 40):
            # 刻度线
            ax.plot([x_pixels + i, x_pixels + i], 
                    [y_pixels, y_pixels + bar_height], 
                    color='black', linewidth=1)
            # 刻度值
            distance = i * scale
            ax.text(x_pixels + i, y_pixels + bar_height + 5,
                   f'{distance:.1f}m',
                   ha='center', va='bottom', fontsize=8)
        
        # 添加比例尺说明
        scale_text = f"比例尺: 1:{scale:.2f}米/像素"
        ax.text(x_pixels + scale_length/2, y_pixels + bar_height + 20,
                scale_text,
                ha='center',
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    def export_cad_layer(self, out_path):
        """导出CAD图层为PNG文件"""
        # 创建新的图形
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        
        # 获取当前视图范围
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        
        # 复制所有图形到新图形
        for shape in self.shapes:
            if isinstance(shape, Line2D):
                xdata, ydata = shape.get_data()
                ax.plot(xdata, ydata, color=shape.get_color(), linewidth=1)
        
        # 复制所有坐标标注
        for label in self.coord_labels:
            # 创建新的bbox属性字典
            bbox_props = {
                'facecolor': 'white',
                'alpha': 0.7,
                'edgecolor': 'none'
            }
            ax.text(label.get_position()[0], label.get_position()[1],
                   label.get_text(),
                   color=label.get_color(),
                   fontsize=label.get_fontsize(),
                   bbox=bbox_props,
                   ha=label.get_ha(),
                   va=label.get_va(),
                   fontname='Times New Roman')
        
        # 设置坐标轴
        ax.set_aspect('equal')
        ax.axis('off')
        
        # 设置视图范围
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        
        # 添加指北针
        ax.annotate(
            '', xy=(0.98, 0.90), xytext=(0.98, 0.80),
            xycoords='axes fraction',
            arrowprops=dict(facecolor='red', edgecolor='red', width=2, headwidth=10)
        )
        ax.text(0.98, 0.95, "N", transform=ax.transAxes,
                ha='center', va='center', fontsize=14, color='red', fontname='Times New Roman')
        
        # 保存为PNG，增加DPI以提高分辨率
        fig.savefig(out_path, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close(fig)

    def _connect_events(self):
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion) 