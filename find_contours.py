import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ezdxf


def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if filepath:
        display_image(filepath)


def display_image(filepath):
    global contours  # 保存轮廓以供导出使用
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 更新高斯模糊参数
    blurred = cv2.GaussianBlur(gray, (7, 7), 7)

    # 更新Canny边缘检测参数
    edges = cv2.Canny(blurred, 15, 90)

    # 寻找并绘制轮廓
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (0, 0, 0), 3)  # 使用黑色绘制轮廓

    original_image = Image.open(filepath)
    contour_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    original_image.thumbnail((400, 400))
    contour_image.thumbnail((400, 400))

    original_tk = ImageTk.PhotoImage(original_image)
    contour_tk = ImageTk.PhotoImage(contour_image)

    original_label.config(image=original_tk)
    original_label.image = original_tk
    processed_label.config(image=contour_tk)
    processed_label.image = contour_tk


def export_to_dxf():
    if 'contours' not in globals() or not contours:
        messagebox.showerror("错误", "请先打开并处理图像。")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF files", "*.dxf")])
    if not filepath:
        return

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    for contour in contours:
        points = [(pt[0][0], pt[0][1]) for pt in contour]
        msp.add_lwpolyline(points, close=True)

    doc.saveas(filepath)
    messagebox.showinfo("导出成功", f"CAD文件已成功导出到 {filepath}")


# 创建主窗口
root = Tk()
root.title("正射影像处理")

frame = Frame(root)
frame.pack(padx=10, pady=10)

original_label = Label(frame)
original_label.grid(row=0, column=0, padx=5, pady=5)

processed_label = Label(frame)
processed_label.grid(row=0, column=1, padx=5, pady=5)

open_button = Button(root, text="打开影像", command=open_file)
open_button.pack(side=LEFT, padx=10, pady=10)

export_button = Button(root, text="导出为CAD", command=export_to_dxf)
export_button.pack(side=RIGHT, padx=10, pady=10)

root.mainloop()