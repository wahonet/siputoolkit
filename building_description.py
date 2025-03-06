#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ----------------------------------------------------
# 数据选项
# ----------------------------------------------------
# 基础信息部分（原有数据选项）
eaves_layer_options = ["单檐", "重檐"]
roof_types = ["硬山", "悬山", "歇山", "庑殿", "攒尖"]
shape_options = ["矩形", "六边形", "八边形", "圆形", "其他"]
structure_options = [
    "三檩无廊", "四檩卷棚", "五檩无廊", "六檩前廊", "六檩卷棚无廊",
    "七檩无廊", "七檩前廊", "七檩前后廊",
    "八檩卷棚前后廊", "八檩前廊", "九檩前后廊"
]
width_options = [
    "1", "2", "3", "4", "5",
    "6", "7", "8", "9", "10",
    "太大啦！多到数不清"
]
depth_options = ["3", "4", "5", "6", "7", "8", "9"]
tile_materials = ["琉璃", "青瓦", "布瓦", "金瓦", "明瓦"]
tile_layouts = ["筒瓦", "合瓦", "仰瓦", "干槎瓦", "棋盘心"]

ceiling_options = ["彻上明造", "藻井", "平棋方格天花"]
wall_segment_options = ["不分段", "分段"]
wall_not_div_options = ["通体抹灰", "整砖砌筑", "整石砌筑"]
wall_up_options = ["通体抹灰", "整砖砌筑", "做墙心"]
wall_down_options = ["整砖砌筑", "整石砌筑", "做墙心"]
eave_exposed_options = ["前檐", "后檐", "封户檐"]
door_style_options = ["板门", "隔扇门"]
window_position_options = ["明间", "次间", "稍间", "尽间"]
window_style_options = [
    "直棂窗", "直棂一马三箭", "破子棂窗", "槛窗", "支摘窗",
    "圆形窗", "圆形木棂窗", "券窗"
]
floor_options = ["土作地面", "方砖地面", "条砖地面", "石作地面"]

base_options = ["无", "普通", "须弥座", "带栏杆", "组合"]
base_plan_options = ["矩形", "方形", "六边形", "八边形"]
step_style_options = ["无", "垂带踏跺", "御路踏跺", "如意踏跺", "云步踏跺", "礓䃰"]
step_arrange_num_options = ["单", "连三", "抄手", "垂手"]
drain_options = ["室外有散水", "室外无散水"]

# ----------------------------------------------------
# 回调函数
# ----------------------------------------------------
def generate_description():
    """
    生成的描述分为两部分：
      ① 描述栏部分（最上面），格式为：
         【文物名称】位于山东省嘉祥县【镇】镇【村】村【相对位置】，
         文物整体坐【文物整体坐】朝【文物整体朝】，
         现存【现存1】、【现存2】、【现存3】、【现存4】、【现存5】。
      ② 原有描述部分。
    """
    # ---------------- 描述栏部分 ----------------
    relic_name = var_relic_name.get().strip()
    town = var_town.get().strip()
    village = var_village.get().strip()
    rel_loc = var_relative_location.get().strip()
    rel_zuo = var_rel_zuo.get().strip()
    rel_chao = var_rel_chao.get().strip()
    yard_layout = var_yard_layout.get().strip()
    yard_length = var_yard_length.get().strip()
    yard_width = var_yard_width.get().strip()
    area = var_area.get().strip()
    existing1 = var_existing1.get().strip()
    existing2 = var_existing2.get().strip()
    existing3 = var_existing3.get().strip()
    existing4 = var_existing4.get().strip()
    existing5 = var_existing5.get().strip()

    if not relic_name:
        result_var.set("请输入文物名称（描述栏）！")
        return

    desc_header = (
        f"【{relic_name}】位于山东省嘉祥县{town}镇{village}村{rel_loc}，"
        f"文物整体坐{rel_zuo}朝{rel_chao}，"
    )

    if yard_layout or yard_length or yard_width or area:
        desc_header += f"{yard_layout}院落布局，院落长{yard_length}米，宽{yard_width}米，占地面积{area}平方米。"

    desc_header += f"现存{existing1}、{existing2}、{existing3}、{existing4}、{existing5}。"

    # ---------------- 原有描述部分 ----------------
    eaves_layer_val = var_eaves_layer.get()        # 单檐/重檐
    M = var_zuo.get().strip()                      # 坐
    N = var_chao.get().strip()                     # 朝
    O = var_length.get().strip()                   # 长
    P = var_width_val.get().strip()                # 宽
    Q = var_height.get().strip()                   # 高
    A = var_name.get().strip()                     # 建筑名称

    B = var_roof.get()                  # 房顶整体形制
    C = var_shape.get()                 # 平面形状
    E = var_tile_material.get()         # 瓦面材质
    F = var_tile_layout.get()           # 瓦作铺设
    D = var_structure.get()             # 正身构架
    G = var_width_int.get()             # 面阔(几间)
    H = var_depth_int.get()             # 进深(几椽)

    ceiling_val = var_ceiling.get()               # 天花
    seg_choice = var_wall_segment.get()           # 墙体是否分段
    if seg_choice == "不分段":
        wall_desc = var_wall_not_div.get()
        wall_desc_final = f"{wall_desc}"
    else:
        up_val = var_wall_up.get()
        down_val = var_wall_down.get()
        wall_desc_final = f"上身{up_val}，下碱{down_val}"

    eave_exposed_val = var_eave_exposed.get()  # 露檐
    door_val = var_door_style.get()            # 门形制
    window_pos_val = var_window_position.get() # 窗位置
    window_style_val = var_window_style.get()  # 窗形制
    floor_val = var_floor.get()                # 地面

    I = var_base.get()                 # 台基类别
    J = var_base_plan.get()            # 台基平面形状
    K = var_step_style.get()           # 台阶式样
    L = var_step_arrange_num.get()     # 台阶布置数量
    drain_val = var_drain.get()        # 散水

    line1 = (
        f"{A}为{eaves_layer_val}{B}顶建筑，"
        f"坐{M}朝{N}，{C}平面布局。"
    )
    line2 = f"长{O}米，宽{P}米，高（到正脊上皮）{Q}米。"
    line3 = f"{E}{F}铺设屋面。"
    line4 = f"{D}构架，面阔{G}间，进深{H}椽。"
    line5 = f"{ceiling_val}，墙体{wall_desc_final}，{eave_exposed_val}。"
    line6 = f"建筑正面明辟{door_val}，{window_pos_val}设{window_style_val}，{floor_val}。"
    line7 = ""
    if I != "无":
        if K != "无":
            line7 = f"{I}台基，{J}平面布局，{L}{K}，{drain_val}。"
        else:
            line7 = f"{I}台基，{J}平面布局，{drain_val}。"
    else:
        line7 = f"{drain_val}。"

    original_desc = "".join([line1, line2, line3, line4, line5, line6, line7]).strip()

    final_description = desc_header + "\n" + original_desc
    result_var.set(final_description)
    char_count_var.set(f"字数：{len(final_description)}")

def copy_result():
    content = result_var.get()
    if content.strip():
        root.clipboard_clear()
        root.clipboard_append(content)

# ----------------------------------------------------
# 滚动相关的辅助函数
# ----------------------------------------------------
def _on_mousewheel_windows(event):
    scrollable_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
def _on_mousewheel_other(event):
    if event.num == 4:
        scrollable_canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        scrollable_canvas.yview_scroll(1, "units")
def _bind_mousewheel(widget):
    if sys.platform.startswith('win'):
        widget.bind('<MouseWheel>', _on_mousewheel_windows)
    else:
        widget.bind('<Button-4>', _on_mousewheel_other)
        widget.bind('<Button-5>', _on_mousewheel_other)
def _unbind_mousewheel(widget):
    if sys.platform.startswith('win'):
        widget.unbind('<MouseWheel>')
    else:
        widget.unbind('<Button-4>')
        widget.unbind('<Button-5>')
def _bound_to_mousewheel(event):
    _bind_mousewheel(root)
def _unbound_to_mousewheel(event):
    _unbind_mousewheel(root)
def resize_image(image_path, width=80, height=80):
    """调整图片大小"""
    try:
        # 使用resource_path获取图片的绝对路径
        abs_path = resource_path(image_path)
        original_img = Image.open(abs_path)
        resized_img = original_img.resize((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized_img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

# ----------------------------------------------------
# 主窗口
# ----------------------------------------------------
def main():
    """程序入口点"""
    global root, scrollable_canvas, form_frame
    global char_count_var, result_var
    global var_relic_name, var_town, var_village, var_relative_location
    global var_rel_zuo, var_rel_chao, var_yard_layout, var_yard_length
    global var_yard_width, var_area, var_existing1, var_existing2
    global var_existing3, var_existing4, var_existing5
    global var_eaves_layer, var_zuo, var_chao, var_length, var_width_val
    global var_height, var_name, var_roof, var_shape, var_tile_material
    global var_tile_layout, var_structure, var_width_int, var_depth_int
    global var_ceiling, var_wall_segment, var_wall_not_div, var_wall_up
    global var_wall_down, var_eave_exposed, var_door_style
    global var_window_position, var_window_style, var_floor
    global var_base, var_base_plan, var_step_style
    global var_step_arrange_num, var_drain

    root = tk.Tk()
    root.title("古建筑描述生成器")
    root.geometry("1500x1000")

    # 初始化所有变量
    char_count_var = tk.StringVar(value="字数：0")
    result_var = tk.StringVar(value="")

    # 描述栏变量
    var_relic_name = tk.StringVar(value="")
    var_town = tk.StringVar(value="")
    var_village = tk.StringVar(value="")
    var_relative_location = tk.StringVar(value="")
    var_rel_zuo = tk.StringVar(value="")
    var_rel_chao = tk.StringVar(value="")
    var_yard_layout = tk.StringVar(value="")
    var_yard_length = tk.StringVar(value="")
    var_yard_width = tk.StringVar(value="")
    var_area = tk.StringVar(value="")
    var_existing1 = tk.StringVar(value="")
    var_existing2 = tk.StringVar(value="")
    var_existing3 = tk.StringVar(value="")
    var_existing4 = tk.StringVar(value="")
    var_existing5 = tk.StringVar(value="")

    # 基础信息变量
    var_eaves_layer = tk.StringVar(value=eaves_layer_options[0])
    var_zuo = tk.StringVar(value="")
    var_chao = tk.StringVar(value="")
    var_length = tk.StringVar(value="")
    var_width_val = tk.StringVar(value="")
    var_height = tk.StringVar(value="")
    var_name = tk.StringVar(value="")

    var_roof = tk.StringVar(value=roof_types[0])
    var_shape = tk.StringVar(value=shape_options[0])
    var_tile_material = tk.StringVar(value=tile_materials[0])
    var_tile_layout = tk.StringVar(value=tile_layouts[0])
    var_structure = tk.StringVar(value=structure_options[0])
    var_width_int = tk.StringVar(value=width_options[0])
    var_depth_int = tk.StringVar(value=depth_options[0])

    var_ceiling = tk.StringVar(value=ceiling_options[0])
    var_wall_segment = tk.StringVar(value=wall_segment_options[0])
    var_wall_not_div = tk.StringVar(value=wall_not_div_options[0])
    var_wall_up = tk.StringVar(value=wall_up_options[0])
    var_wall_down = tk.StringVar(value=wall_down_options[0])
    var_eave_exposed = tk.StringVar(value=eave_exposed_options[0])
    var_door_style = tk.StringVar(value=door_style_options[0])
    var_window_position = tk.StringVar(value=window_position_options[0])
    var_window_style = tk.StringVar(value=window_style_options[0])
    var_floor = tk.StringVar(value=floor_options[0])

    var_base = tk.StringVar(value=base_options[0])
    var_base_plan = tk.StringVar(value=base_plan_options[0])
    var_step_style = tk.StringVar(value=step_style_options[0])
    var_step_arrange_num = tk.StringVar(value=step_arrange_num_options[0])
    var_drain = tk.StringVar(value=drain_options[0])

    # 创建主框架
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # 左侧（带滚动表单）
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True)
    scrollable_canvas = tk.Canvas(left_frame)
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=scrollable_canvas.yview)
    scrollbar.pack(side="right", fill="y")
    scrollable_canvas.pack(side="left", fill="both", expand=True)
    scrollable_canvas.configure(yscrollcommand=scrollbar.set)
    form_frame = ttk.Frame(scrollable_canvas)
    scrollable_canvas.create_window((0, 0), window=form_frame, anchor="nw")

    def on_configure(event):
        scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all"))
    form_frame.bind("<Configure>", on_configure)
    form_frame.bind("<Enter>", _bound_to_mousewheel)
    form_frame.bind("<Leave>", _unbound_to_mousewheel)

    # 右侧：结果显示 + 按钮 + 字数
    right_frame = ttk.Frame(main_frame, width=300)
    right_frame.pack(side="right", fill="y", padx=10, pady=10)

    # 开始布局
    row_index = 0

    # ----------------- 新增：描述栏 -----------------
    label_desc_title = ttk.Label(form_frame, text="【描述栏】", font=("kaiti", 14), foreground="blue")
    label_desc_title.grid(row=row_index, column=0, padx=5, pady=10, sticky="W")
    row_index += 1

    # 文物名称
    label_relic_name = ttk.Label(form_frame, text="文物名称：", font=("kaiti", 12))
    label_relic_name.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_relic_name = ttk.Entry(form_frame, textvariable=var_relic_name, width=20, font=("Arial", 12))
    entry_relic_name.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 镇
    label_town = ttk.Label(form_frame, text="镇：", font=("kaiti", 12))
    label_town.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_town = ttk.Entry(form_frame, textvariable=var_town, width=20, font=("Arial", 12))
    entry_town.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 村
    label_village = ttk.Label(form_frame, text="村：", font=("kaiti", 12))
    label_village.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_village = ttk.Entry(form_frame, textvariable=var_village, width=20, font=("Arial", 12))
    entry_village.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 相对位置
    label_relative_location = ttk.Label(form_frame, text="相对位置：", font=("kaiti", 12))
    label_relative_location.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_relative_location = ttk.Entry(form_frame, textvariable=var_relative_location, width=40, font=("Arial", 12))
    entry_relative_location.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 文物整体坐
    label_rel_zuo = ttk.Label(form_frame, text="文物整体坐：", font=("kaiti", 12))
    label_rel_zuo.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_rel_zuo = ttk.Entry(form_frame, textvariable=var_rel_zuo, width=20, font=("Arial", 12))
    entry_rel_zuo.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 文物整体朝
    label_rel_chao = ttk.Label(form_frame, text="文物整体朝：", font=("kaiti", 12))
    label_rel_chao.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_rel_chao = ttk.Entry(form_frame, textvariable=var_rel_chao, width=20, font=("Arial", 12))
    entry_rel_chao.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 院落布局
    label_yard_layout = ttk.Label(form_frame, text="院落布局：", font=("kaiti", 12))
    label_yard_layout.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_yard_layout = ttk.Entry(form_frame, textvariable=var_yard_layout, width=20, font=("Arial", 12))
    entry_yard_layout.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 院落长
    label_yard_length = ttk.Label(form_frame, text="院落长(米)：", font=("kaiti", 12))
    label_yard_length.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_yard_length = ttk.Entry(form_frame, textvariable=var_yard_length, width=20, font=("Arial", 12))
    entry_yard_length.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 院落宽
    label_yard_width = ttk.Label(form_frame, text="院落宽(米)：", font=("kaiti", 12))
    label_yard_width.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_yard_width = ttk.Entry(form_frame, textvariable=var_yard_width, width=20, font=("Arial", 12))
    entry_yard_width.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 占地面积
    label_area = ttk.Label(form_frame, text="占地面积(平方米)：", font=("kaiti", 12))
    label_area.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_area = ttk.Entry(form_frame, textvariable=var_area, width=20, font=("Arial", 12))
    entry_area.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 现存1
    label_existing1 = ttk.Label(form_frame, text="现存1：", font=("kaiti", 12))
    label_existing1.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_existing1 = ttk.Entry(form_frame, textvariable=var_existing1, width=20, font=("Arial", 12))
    entry_existing1.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 现存2
    label_existing2 = ttk.Label(form_frame, text="现存2：", font=("kaiti", 12))
    label_existing2.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_existing2 = ttk.Entry(form_frame, textvariable=var_existing2, width=20, font=("Arial", 12))
    entry_existing2.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 现存3
    label_existing3 = ttk.Label(form_frame, text="现存3：", font=("kaiti", 12))
    label_existing3.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_existing3 = ttk.Entry(form_frame, textvariable=var_existing3, width=20, font=("Arial", 12))
    entry_existing3.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 现存4
    label_existing4 = ttk.Label(form_frame, text="现存4：", font=("kaiti", 12))
    label_existing4.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_existing4 = ttk.Entry(form_frame, textvariable=var_existing4, width=20, font=("Arial", 12))
    entry_existing4.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    # 现存5
    label_existing5 = ttk.Label(form_frame, text="现存5：", font=("kaiti", 12))
    label_existing5.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_existing5 = ttk.Entry(form_frame, textvariable=var_existing5, width=20, font=("Arial", 12))
    entry_existing5.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 2

    # ----------------- 原有：【基础信息】 -----------------
    label_info_title = ttk.Label(form_frame, text="【基础信息】", font=("kaiti", 14), foreground="blue")
    label_info_title.grid(row=row_index, column=0, padx=5, pady=10, sticky="W")
    row_index += 1

    label_name = ttk.Label(form_frame, text="建筑名称：", font=("kaiti", 12))
    label_name.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_name = ttk.Entry(form_frame, textvariable=var_name, width=20, font=("Arial", 12))
    entry_name.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    label_eaves_layer = ttk.Label(form_frame, text="层数：", font=("kaiti", 12))
    label_eaves_layer.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    frame_eaves_layer = ttk.Frame(form_frame)
    frame_eaves_layer.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(eaves_layer_options):
        rbtn = ttk.Radiobutton(frame_eaves_layer, text=option, variable=var_eaves_layer, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_zuo = ttk.Label(form_frame, text="坐：", font=("kaiti", 12))
    label_zuo.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_zuo = ttk.Entry(form_frame, textvariable=var_zuo, width=8, font=("Arial", 12))
    entry_zuo.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    label_chao = ttk.Label(form_frame, text="朝：", font=("kaiti", 12))
    label_chao.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_chao = ttk.Entry(form_frame, textvariable=var_chao, width=8, font=("Arial", 12))
    entry_chao.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    label_shape = ttk.Label(form_frame, text="平面形状：", font=("kaiti", 12))
    label_shape.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    frame_shape = ttk.Frame(form_frame)
    frame_shape.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(shape_options):
        rbtn = ttk.Radiobutton(frame_shape, text=option, variable=var_shape, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_length = ttk.Label(form_frame, text="长(米)：", font=("kaiti", 12))
    label_length.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_length = ttk.Entry(form_frame, textvariable=var_length, width=8, font=("Arial", 12))
    entry_length.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    label_width_val = ttk.Label(form_frame, text="宽(米)：", font=("kaiti", 12))
    label_width_val.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_width_val = ttk.Entry(form_frame, textvariable=var_width_val, width=8, font=("Arial", 12))
    entry_width_val.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 1

    label_height = ttk.Label(form_frame, text="高(到正脊上皮,米)：", font=("kaiti", 12))
    label_height.grid(row=row_index, column=0, padx=5, pady=5, sticky="E")
    entry_height = ttk.Entry(form_frame, textvariable=var_height, width=8, font=("Arial", 12))
    entry_height.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    row_index += 2

    # ----------------- 原有：【上分】 -----------------
    label_up_title = ttk.Label(form_frame, text="【上分】", font=("kaiti", 14), foreground="blue")
    label_up_title.grid(row=row_index, column=0, padx=5, pady=10, sticky="W")
    row_index += 1

    label_tile_material = ttk.Label(form_frame, text="瓦面材质：", font=("kaiti", 12))
    label_tile_material.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_tile_material = ttk.Frame(form_frame)
    frame_tile_material.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(tile_materials):
        rbtn = ttk.Radiobutton(frame_tile_material, text=option, variable=var_tile_material, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_tile_layout = ttk.Label(form_frame, text="瓦作铺设：", font=("kaiti", 12))
    label_tile_layout.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_tile_layout = ttk.Frame(form_frame)
    frame_tile_layout.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(tile_layouts):
        rbtn = ttk.Radiobutton(frame_tile_layout, text=option, variable=var_tile_layout, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
        img_path = os.path.join('pic', f'tile_{option}.png')
        img = resize_image(img_path)
        if img:
            label_img = ttk.Label(frame_tile_layout, image=img)
            label_img.image = img
            label_img.grid(row=1, column=i, padx=5, pady=3)
    row_index += 1

    label_roof = ttk.Label(form_frame, text="房顶整体形制：", font=("kaiti", 12))
    label_roof.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_roof = ttk.Frame(form_frame)
    frame_roof.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(roof_types):
        col_idx = i % 5
        rbtn = ttk.Radiobutton(frame_roof, text=option, variable=var_roof, value=option)
        rbtn.grid(row=0, column=col_idx, padx=5, pady=3, sticky="W")
        img_path = os.path.join('pic', f'roof_{option}.png')
        img = resize_image(img_path)
        if img:
            label_img = ttk.Label(frame_roof, image=img)
            label_img.image = img
            label_img.grid(row=1, column=col_idx, padx=5, pady=3)
    row_index += 1

    label_structure = ttk.Label(form_frame, text="正身构架：", font=("kaiti", 12))
    label_structure.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_structure = ttk.Frame(form_frame)
    frame_structure.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    max_columns = 6
    row_count = 0
    for i, option in enumerate(structure_options):
        col_idx = i % max_columns
        if col_idx == 0 and i != 0:
            row_count += 1
        rbtn = ttk.Radiobutton(frame_structure, text=option, variable=var_structure, value=option)
        rbtn.grid(row=row_count*2, column=col_idx, padx=5, pady=3, sticky="W")
        img_path = os.path.join('pic', f'structure_{option}.png')
        img = resize_image(img_path)
        if img:
            label_img = ttk.Label(frame_structure, image=img)
            label_img.image = img
            label_img.grid(row=row_count*2+1, column=col_idx, padx=5, pady=3)
    row_index += 1

    label_width_int = ttk.Label(form_frame, text="面阔(几间)：", font=("kaiti", 12))
    label_width_int.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_width_int = ttk.Frame(form_frame)
    frame_width_int.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(width_options):
        rbtn = ttk.Radiobutton(frame_width_int, text=option, variable=var_width_int, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_depth_int = ttk.Label(form_frame, text="进深(几椽)：", font=("kaiti", 12))
    label_depth_int.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_depth_int = ttk.Frame(form_frame)
    frame_depth_int.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(depth_options):
        rbtn = ttk.Radiobutton(frame_depth_int, text=option, variable=var_depth_int, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    # ----------------- 原有：【中分】 -----------------
    label_mid_title = ttk.Label(form_frame, text="【中分】", font=("kaiti", 14), foreground="blue")
    label_mid_title.grid(row=row_index, column=0, padx=5, pady=10, sticky="W")
    row_index += 1

    label_ceiling = ttk.Label(form_frame, text="天花：", font=("kaiti", 12))
    label_ceiling.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_ceiling = ttk.Frame(form_frame)
    frame_ceiling.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(ceiling_options):
        rbtn = ttk.Radiobutton(frame_ceiling, text=option, variable=var_ceiling, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_wall_segment = ttk.Label(form_frame, text="墙体是否分段：", font=("kaiti", 12))
    label_wall_segment.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_wall_segment = ttk.Frame(form_frame)
    frame_wall_segment.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(wall_segment_options):
        rbtn = ttk.Radiobutton(frame_wall_segment, text=option, variable=var_wall_segment, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_wall_not_div = ttk.Label(form_frame, text="(不分段)墙体：", font=("kaiti", 12))
    label_wall_not_div.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_wall_not_div = ttk.Frame(form_frame)
    frame_wall_not_div.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(wall_not_div_options):
        rbtn = ttk.Radiobutton(frame_wall_not_div, text=option, variable=var_wall_not_div, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_wall_up = ttk.Label(form_frame, text="(分段)上身：", font=("kaiti", 12))
    label_wall_up.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_wall_up = ttk.Frame(form_frame)
    frame_wall_up.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(wall_up_options):
        rbtn = ttk.Radiobutton(frame_wall_up, text=option, variable=var_wall_up, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_wall_down = ttk.Label(form_frame, text="(分段)下碱：", font=("kaiti", 12))
    label_wall_down.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_wall_down = ttk.Frame(form_frame)
    frame_wall_down.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(wall_down_options):
        rbtn = ttk.Radiobutton(frame_wall_down, text=option, variable=var_wall_down, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_eave_exposed = ttk.Label(form_frame, text="露檐：", font=("kaiti", 12))
    label_eave_exposed.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_eave_exposed = ttk.Frame(form_frame)
    frame_eave_exposed.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(eave_exposed_options):
        rbtn = ttk.Radiobutton(frame_eave_exposed, text=option, variable=var_eave_exposed, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_door_style = ttk.Label(form_frame, text="门形制：", font=("kaiti", 12))
    label_door_style.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_door_style = ttk.Frame(form_frame)
    frame_door_style.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(door_style_options):
        rbtn = ttk.Radiobutton(frame_door_style, text=option, variable=var_door_style, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_window_position = ttk.Label(form_frame, text="窗位置：", font=("kaiti", 12))
    label_window_position.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_window_position = ttk.Frame(form_frame)
    frame_window_position.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(window_position_options):
        rbtn = ttk.Radiobutton(frame_window_position, text=option, variable=var_window_position, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_window_style = ttk.Label(form_frame, text="窗形制：", font=("kaiti", 12))
    label_window_style.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_window_style = ttk.Frame(form_frame)
    frame_window_style.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(window_style_options):
        rbtn = ttk.Radiobutton(frame_window_style, text=option, variable=var_window_style, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_floor = ttk.Label(form_frame, text="地面：", font=("kaiti", 12))
    label_floor.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_floor = ttk.Frame(form_frame)
    frame_floor.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(floor_options):
        rbtn = ttk.Radiobutton(frame_floor, text=option, variable=var_floor, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 2

    # ----------------- 原有：【下分】 -----------------
    label_down_title = ttk.Label(form_frame, text="【下分】", font=("kaiti", 14), foreground="blue")
    label_down_title.grid(row=row_index, column=0, padx=5, pady=10, sticky="W")
    row_index += 1

    label_base = ttk.Label(form_frame, text="台基类别：", font=("kaiti", 12))
    label_base.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_base = ttk.Frame(form_frame)
    frame_base.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(base_options):
        rbtn = ttk.Radiobutton(frame_base, text=option, variable=var_base, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_base_plan = ttk.Label(form_frame, text="台基平面形状：", font=("kaiti", 12))
    label_base_plan.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_base_plan = ttk.Frame(form_frame)
    frame_base_plan.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(base_plan_options):
        rbtn = ttk.Radiobutton(frame_base_plan, text=option, variable=var_base_plan, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_step_style = ttk.Label(form_frame, text="台阶式样：", font=("kaiti", 12))
    label_step_style.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_step_style = ttk.Frame(form_frame)
    frame_step_style.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(step_style_options):
        rbtn = ttk.Radiobutton(frame_step_style, text=option, variable=var_step_style, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
        img_path = os.path.join('pic', f'step_{option}.png')
        img = resize_image(img_path)
        if img:
            label_img = ttk.Label(frame_step_style, image=img)
            label_img.image = img
            label_img.grid(row=1, column=i, padx=5, pady=3)
    row_index += 1

    label_step_arrange_num = ttk.Label(form_frame, text="台阶布置(数量)：", font=("kaiti", 12))
    label_step_arrange_num.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_step_arrange_num = ttk.Frame(form_frame)
    frame_step_arrange_num.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(step_arrange_num_options):
        rbtn = ttk.Radiobutton(frame_step_arrange_num, text=option, variable=var_step_arrange_num, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 1

    label_drain = ttk.Label(form_frame, text="散水：", font=("kaiti", 12))
    label_drain.grid(row=row_index, column=0, padx=5, pady=5, sticky="NE")
    frame_drain = ttk.Frame(form_frame)
    frame_drain.grid(row=row_index, column=1, padx=5, pady=5, sticky="W")
    for i, option in enumerate(drain_options):
        rbtn = ttk.Radiobutton(frame_drain, text=option, variable=var_drain, value=option)
        rbtn.grid(row=0, column=i, padx=5, pady=3, sticky="W")
    row_index += 2

    btn_generate = ttk.Button(form_frame, text="生成描述", command=generate_description)
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
    label_count = ttk.Label(right_frame, textvariable=char_count_var, font=("kaiti", 12), foreground="green")
    label_count.pack(pady=5)

    # ----------------------------------------------------
    # 启动主循环
    # ----------------------------------------------------
    root.mainloop()

if __name__ == "__main__":
    main()