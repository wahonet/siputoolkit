#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import platform

# ----------------------------------------------------
# 数据选项
# ----------------------------------------------------
# 碑冠/碑首选项
crown_type_options = ["有碑冠", "无碑冠"]
head_type_options = ["圆首", "平首"]  # 无碑冠时的选项

# 碑身材质选项
material_options = ["汉白玉", "青石", "板岩", "大理石", "其他"]

# 碑座类型选项
base_type_options = ["方形碑座", "龟趺碑座"]

# ----------------------------------------------------
# 回调函数
# ----------------------------------------------------
def generate_description():
    """生成碑刻描述"""
    # 获取所有输入值
    total_height = var_total_height.get().strip()
    total_width = var_total_width.get().strip()
    total_thickness = var_total_thickness.get().strip()
    crown_type = var_crown_type.get()
    
    description = f"碑高{total_height}厘米，宽{total_width}厘米，厚{total_thickness}厘米。"
    
    # 处理碑冠/碑首部分
    if crown_type == "有碑冠":
        dragon_pattern = var_dragon_pattern.get().strip()
        front_text = var_front_text.get().strip()
        back_text = var_back_text.get().strip()
        
        description += f"碑冠饰以{dragon_pattern}，"
        if front_text or back_text:
            description += "碑额"
            if front_text:
                description += f"阳面刻「{front_text}」"
            if back_text:
                if front_text:
                    description += "，"
                description += f"阴面刻「{back_text}」"
            description += "。"
    else:
        head_type = var_head_type.get()
        pattern = var_head_pattern.get().strip()
        front_text = var_head_front_text.get().strip()
        back_text = var_head_back_text.get().strip()
        
        description += f"碑首为{head_type}"
        if pattern:
            description += f"，饰以{pattern}"
        if front_text or back_text:
            description += "，碑额"
            if front_text:
                description += f"阳面刻「{front_text}」"
            if back_text:
                if front_text:
                    description += "，"
                description += f"阴面刻「{back_text}」"
        description += "。"
    
    # 处理碑身部分
    material = var_material.get()
    if material == "其他":
        material = var_other_material.get().strip()
    
    front_content = var_front_content.get().strip()
    back_content = var_back_content.get().strip()
    
    description += f"\n碑身为{material}质，"
    description += f"阳面刻「{front_content}」，"
    description += "阴面" + (f"刻「{back_content}」" if back_content else "无字") + "。"
    
    # 处理碑座部分
    base_type = var_base_type.get()
    if base_type == "方形碑座":
        length = var_length.get().strip()
        width = var_width.get().strip()
        height = var_height.get().strip()
        description += f"\n方形碑座，长{length}厘米，宽{width}厘米，高{height}厘米。"
    else:
        turtle_length = var_turtle_length.get().strip()
        turtle_width = var_turtle_width.get().strip()
        turtle_height = var_turtle_height.get().strip()
        description += f"\n龟趺碑座，龟长{turtle_length}厘米，龟背宽{turtle_width}厘米，高{turtle_height}厘米。"
    
    # 更新结果
    result_var.set(description)
    char_count_var.set(f"字数：{len(description)}")

def copy_result():
    """复制生成的描述到剪贴板"""
    content = result_var.get()
    if content.strip():
        root.clipboard_clear()
        root.clipboard_append(content)

def on_crown_type_change(*args):
    """当碑冠类型改变时更新界面"""
    crown_type = var_crown_type.get()
    if crown_type == "有碑冠":
        # 显示碑冠相关组件
        for widget in crown_widgets:
            widget.grid()
        # 隐藏碑首相关组件
        for widget in head_widgets:
            widget.grid_remove()
    else:
        # 隐藏碑冠相关组件
        for widget in crown_widgets:
            widget.grid_remove()
        # 显示碑首相关组件
        for widget in head_widgets:
            widget.grid()

def on_material_change(*args):
    """当碑身材质改变时更新界面"""
    if var_material.get() == "其他":
        label_other_material.grid()
        entry_other_material.grid()
    else:
        label_other_material.grid_remove()
        entry_other_material.grid_remove()

def on_base_type_change(*args):
    """当碑座类型改变时更新界面"""
    base_type = var_base_type.get()
    if base_type == "方形碑座":
        # 显示方形碑座相关组件
        for widget in square_base_widgets:
            widget.grid()
        # 隐藏龟趺碑座相关组件
        for widget in turtle_base_widgets:
            widget.grid_remove()
    else:
        # 隐藏方形碑座相关组件
        for widget in square_base_widgets:
            widget.grid_remove()
        # 显示龟趺碑座相关组件
        for widget in turtle_base_widgets:
            widget.grid()

def _on_mousewheel_windows(event):
    """Windows系统的鼠标滚轮事件处理"""
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_mousewheel_other(event):
    """其他系统的鼠标滚轮事件处理"""
    canvas.yview_scroll(int(-1 * event.delta), "units")

def _bind_mousewheel(widget):
    """绑定鼠标滚轮事件"""
    if platform.system() == "Windows":
        widget.bind("<MouseWheel>", _on_mousewheel_windows)
    else:
        widget.bind("<Button-4>", _on_mousewheel_other)
        widget.bind("<Button-5>", _on_mousewheel_other)

def _unbind_mousewheel(widget):
    """解绑鼠标滚轮事件"""
    if platform.system() == "Windows":
        widget.unbind("<MouseWheel>")
    else:
        widget.unbind("<Button-4>")
        widget.unbind("<Button-5>")

def _bound_to_mousewheel(event):
    """鼠标进入组件时绑定滚轮事件"""
    _bind_mousewheel(canvas)

def _unbound_to_mousewheel(event):
    """鼠标离开组件时解绑滚轮事件"""
    _unbind_mousewheel(canvas)

def main():
    """主函数"""
    global root, var_total_height, var_total_width, var_total_thickness
    global var_crown_type, var_dragon_pattern, var_front_text, var_back_text
    global var_head_type, var_head_pattern, var_head_front_text, var_head_back_text
    global var_material, var_other_material, var_front_content, var_back_content
    global var_base_type, var_length, var_width, var_height
    global var_turtle_length, var_turtle_width, var_turtle_height
    global result_var, char_count_var
    global label_other_material, entry_other_material
    global crown_widgets, head_widgets, square_base_widgets, turtle_base_widgets
    global canvas

    # ----------------------------------------------------
    # 主窗口
    # ----------------------------------------------------
    root = tk.Tk()
    root.title("碑刻描述生成器")
    root.geometry("1200x1200")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # 左侧（表单）
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # 创建滚动画布
    canvas = tk.Canvas(left_frame)
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 绑定鼠标滚轮事件
    if platform.system() == "Windows":
        canvas.bind("<MouseWheel>", _on_mousewheel_windows)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel_windows)
    else:
        canvas.bind("<Button-4>", _on_mousewheel_other)
        canvas.bind("<Button-5>", _on_mousewheel_other)
        scrollable_frame.bind("<Button-4>", _on_mousewheel_other)
        scrollable_frame.bind("<Button-5>", _on_mousewheel_other)

    # 右侧（结果显示）
    right_frame = ttk.Frame(main_frame, width=300)
    right_frame.pack(side="right", fill="y", padx=10, pady=10)

    # ----------------------------------------------------
    # 变量定义
    # ----------------------------------------------------
    # 结果相关变量
    result_var = tk.StringVar(value="")
    char_count_var = tk.StringVar(value="字数：0")

    # 整体尺寸相关变量
    var_total_height = tk.StringVar(value="")
    var_total_width = tk.StringVar(value="")
    var_total_thickness = tk.StringVar(value="")

    # 碑冠/碑首相关变量
    var_crown_type = tk.StringVar(value=crown_type_options[0])
    var_dragon_pattern = tk.StringVar(value="")
    var_front_text = tk.StringVar(value="")
    var_back_text = tk.StringVar(value="")

    var_head_type = tk.StringVar(value=head_type_options[0])
    var_head_pattern = tk.StringVar(value="")
    var_head_front_text = tk.StringVar(value="")
    var_head_back_text = tk.StringVar(value="")

    # 碑身相关变量
    var_material = tk.StringVar(value=material_options[0])
    var_other_material = tk.StringVar(value="")
    var_front_content = tk.StringVar(value="")
    var_back_content = tk.StringVar(value="")

    # 碑座相关变量
    var_base_type = tk.StringVar(value=base_type_options[0])
    var_length = tk.StringVar(value="")
    var_width = tk.StringVar(value="")
    var_height = tk.StringVar(value="")
    var_turtle_length = tk.StringVar(value="")
    var_turtle_width = tk.StringVar(value="")
    var_turtle_height = tk.StringVar(value="")

    # 绑定变量变化事件
    var_crown_type.trace_add("write", on_crown_type_change)
    var_material.trace_add("write", on_material_change)
    var_base_type.trace_add("write", on_base_type_change)

    # ----------------------------------------------------
    # 开始布局（将所有组件放在 scrollable_frame 中）
    # ----------------------------------------------------
    row_index = 0

    # ----------------- 整体尺寸部分 -----------------
    label_size_title = ttk.Label(scrollable_frame, text="【整体尺寸】", font=("kaiti", 14), foreground="blue")
    label_size_title.grid(row=row_index, column=0, columnspan=2, padx=5, pady=10, sticky="w")
    row_index += 1

    # 整体高度
    label_total_height = ttk.Label(scrollable_frame, text="碑高(厘米)：", font=("kaiti", 12))
    label_total_height.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_total_height = ttk.Entry(scrollable_frame, textvariable=var_total_height, width=20)
    entry_total_height.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1

    # 整体宽度
    label_total_width = ttk.Label(scrollable_frame, text="碑宽(厘米)：", font=("kaiti", 12))
    label_total_width.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_total_width = ttk.Entry(scrollable_frame, textvariable=var_total_width, width=20)
    entry_total_width.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1

    # 整体厚度
    label_total_thickness = ttk.Label(scrollable_frame, text="碑厚(厘米)：", font=("kaiti", 12))
    label_total_thickness.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_total_thickness = ttk.Entry(scrollable_frame, textvariable=var_total_thickness, width=20)
    entry_total_thickness.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1

    # ----------------- 碑冠/碑首部分 -----------------
    label_title = ttk.Label(scrollable_frame, text="【碑冠/碑首】", font=("kaiti", 14), foreground="blue")
    label_title.grid(row=row_index, column=0, columnspan=2, padx=5, pady=10, sticky="w")
    row_index += 1

    # 碑冠类型选择
    label_crown_type = ttk.Label(scrollable_frame, text="类型：", font=("kaiti", 12))
    label_crown_type.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    frame_crown_type = ttk.Frame(scrollable_frame)
    frame_crown_type.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    for i, option in enumerate(crown_type_options):
        rb = ttk.Radiobutton(frame_crown_type, text=option, variable=var_crown_type, value=option)
        rb.grid(row=0, column=i, padx=5)
    row_index += 1

    # 碑冠相关组件
    crown_widgets = []

    label_dragon = ttk.Label(scrollable_frame, text="蟠龙纹样式：", font=("kaiti", 12))
    label_dragon.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_dragon = ttk.Entry(scrollable_frame, textvariable=var_dragon_pattern, width=40)
    entry_dragon.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    crown_widgets.extend([label_dragon, entry_dragon])
    row_index += 1

    label_front_text = ttk.Label(scrollable_frame, text="碑额阳面刻字：", font=("kaiti", 12))
    label_front_text.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_front_text = ttk.Entry(scrollable_frame, textvariable=var_front_text, width=40)
    entry_front_text.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    crown_widgets.extend([label_front_text, entry_front_text])
    row_index += 1

    label_back_text = ttk.Label(scrollable_frame, text="碑额阴面刻字：", font=("kaiti", 12))
    label_back_text.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_back_text = ttk.Entry(scrollable_frame, textvariable=var_back_text, width=40)
    entry_back_text.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    crown_widgets.extend([label_back_text, entry_back_text])
    row_index += 1

    # 碑首相关组件
    head_widgets = []

    label_head_type = ttk.Label(scrollable_frame, text="碑首类型：", font=("kaiti", 12))
    label_head_type.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    frame_head_type = ttk.Frame(scrollable_frame)
    frame_head_type.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    for i, option in enumerate(head_type_options):
        rb = ttk.Radiobutton(frame_head_type, text=option, variable=var_head_type, value=option)
        rb.grid(row=0, column=i, padx=5)
    head_widgets.extend([label_head_type, frame_head_type])
    row_index += 1

    label_head_pattern = ttk.Label(scrollable_frame, text="碑首纹饰：", font=("kaiti", 12))
    label_head_pattern.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_head_pattern = ttk.Entry(scrollable_frame, textvariable=var_head_pattern, width=40)
    entry_head_pattern.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    head_widgets.extend([label_head_pattern, entry_head_pattern])
    row_index += 1

    label_head_front = ttk.Label(scrollable_frame, text="碑首阳面刻字：", font=("kaiti", 12))
    label_head_front.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_head_front = ttk.Entry(scrollable_frame, textvariable=var_head_front_text, width=40)
    entry_head_front.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    head_widgets.extend([label_head_front, entry_head_front])
    row_index += 1

    label_head_back = ttk.Label(scrollable_frame, text="碑首阴面刻字：", font=("kaiti", 12))
    label_head_back.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_head_back = ttk.Entry(scrollable_frame, textvariable=var_head_back_text, width=40)
    entry_head_back.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    head_widgets.extend([label_head_back, entry_head_back])
    row_index += 1

    # 初始隐藏碑首相关组件
    for widget in head_widgets:
        widget.grid_remove()

    # ----------------- 碑身部分 -----------------
    label_body_title = ttk.Label(scrollable_frame, text="【碑身】", font=("kaiti", 14), foreground="blue")
    label_body_title.grid(row=row_index, column=0, columnspan=2, padx=5, pady=10, sticky="w")
    row_index += 1

    # 碑身材质
    label_material = ttk.Label(scrollable_frame, text="材质：", font=("kaiti", 12))
    label_material.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    frame_material = ttk.Frame(scrollable_frame)
    frame_material.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    for i, option in enumerate(material_options):
        rb = ttk.Radiobutton(frame_material, text=option, variable=var_material, value=option)
        rb.grid(row=0, column=i, padx=5)
    row_index += 1

    # 其他材质输入框
    label_other_material = ttk.Label(scrollable_frame, text="其他材质：", font=("kaiti", 12))
    label_other_material.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_other_material = ttk.Entry(scrollable_frame, textvariable=var_other_material, width=40)
    entry_other_material.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    label_other_material.grid_remove()
    entry_other_material.grid_remove()
    row_index += 1

    # 碑身内容
    label_front_content = ttk.Label(scrollable_frame, text="阳面内容：", font=("kaiti", 12))
    label_front_content.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_front_content = ttk.Entry(scrollable_frame, textvariable=var_front_content, width=40)
    entry_front_content.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1

    label_back_content = ttk.Label(scrollable_frame, text="阴面内容：", font=("kaiti", 12))
    label_back_content.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_back_content = ttk.Entry(scrollable_frame, textvariable=var_back_content, width=40)
    entry_back_content.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    row_index += 1

    # ----------------- 碑座部分 -----------------
    label_base_title = ttk.Label(scrollable_frame, text="【碑座】", font=("kaiti", 14), foreground="blue")
    label_base_title.grid(row=row_index, column=0, columnspan=2, padx=5, pady=10, sticky="w")
    row_index += 1

    # 碑座类型选择
    label_base_type = ttk.Label(scrollable_frame, text="类型：", font=("kaiti", 12))
    label_base_type.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    frame_base_type = ttk.Frame(scrollable_frame)
    frame_base_type.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    for i, option in enumerate(base_type_options):
        rb = ttk.Radiobutton(frame_base_type, text=option, variable=var_base_type, value=option)
        rb.grid(row=0, column=i, padx=5)
    row_index += 1

    # 方形碑座相关组件
    square_base_widgets = []

    label_length = ttk.Label(scrollable_frame, text="长(厘米)：", font=("kaiti", 12))
    label_length.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_length = ttk.Entry(scrollable_frame, textvariable=var_length, width=20)
    entry_length.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    square_base_widgets.extend([label_length, entry_length])
    row_index += 1

    label_width = ttk.Label(scrollable_frame, text="宽(厘米)：", font=("kaiti", 12))
    label_width.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_width = ttk.Entry(scrollable_frame, textvariable=var_width, width=20)
    entry_width.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    square_base_widgets.extend([label_width, entry_width])
    row_index += 1

    label_height = ttk.Label(scrollable_frame, text="高(厘米)：", font=("kaiti", 12))
    label_height.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_height = ttk.Entry(scrollable_frame, textvariable=var_height, width=20)
    entry_height.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    square_base_widgets.extend([label_height, entry_height])
    row_index += 1

    # 龟趺碑座相关组件
    turtle_base_widgets = []

    label_turtle_length = ttk.Label(scrollable_frame, text="龟长(厘米)：", font=("kaiti", 12))
    label_turtle_length.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_turtle_length = ttk.Entry(scrollable_frame, textvariable=var_turtle_length, width=20)
    entry_turtle_length.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    turtle_base_widgets.extend([label_turtle_length, entry_turtle_length])
    row_index += 1

    label_turtle_width = ttk.Label(scrollable_frame, text="龟背宽(厘米)：", font=("kaiti", 12))
    label_turtle_width.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_turtle_width = ttk.Entry(scrollable_frame, textvariable=var_turtle_width, width=20)
    entry_turtle_width.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    turtle_base_widgets.extend([label_turtle_width, entry_turtle_width])
    row_index += 1

    label_turtle_height = ttk.Label(scrollable_frame, text="高(厘米)：", font=("kaiti", 12))
    label_turtle_height.grid(row=row_index, column=0, padx=5, pady=5, sticky="e")
    entry_turtle_height = ttk.Entry(scrollable_frame, textvariable=var_turtle_height, width=20)
    entry_turtle_height.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
    turtle_base_widgets.extend([label_turtle_height, entry_turtle_height])
    row_index += 1

    # 初始隐藏龟趺碑座相关组件
    for widget in turtle_base_widgets:
        widget.grid_remove()

    # 生成按钮
    btn_generate = ttk.Button(scrollable_frame, text="生成描述", command=generate_description)
    btn_generate.grid(row=row_index, column=0, columnspan=2, pady=20)
    row_index += 1

    # ----------------------------------------------------
    # 右侧：结果 & 复制 & 字数
    # ----------------------------------------------------
    label_result_title = ttk.Label(right_frame, text="生成结果：", font=("kaiti", 14), foreground="blue")
    label_result_title.pack(pady=5)

    label_result = ttk.Label(right_frame, textvariable=result_var, font=("kaiti", 12),
                            wraplength=280, foreground="blue")
    label_result.pack(pady=5, fill="x")

    copy_btn = ttk.Button(right_frame, text="复制到剪贴板", command=copy_result)
    copy_btn.pack(pady=5)

    label_count = ttk.Label(right_frame, textvariable=char_count_var, font=("kaiti", 12),
                           foreground="green")
    label_count.pack(pady=5)

    # ----------------------------------------------------
    # 最后添加滚动条和画布
    # ----------------------------------------------------
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ----------------------------------------------------
    # 启动主循环
    # ----------------------------------------------------
    root.mainloop()

if __name__ == "__main__":
    main() 