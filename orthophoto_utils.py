"""
orthophoto_utils.py

封装了常用的正射影像读写与投影变换工具函数：
-   读取 DOM/DSM 数据集
-   将像素坐标转换为经纬度
-   十进制度数与度分秒格式的转换
-   从指定波段中提取海拔高程
-   将完整的坐标信息导出到 CSV
"""

import csv
import rasterio
from pyproj import Transformer

def read_orthophoto(file_path):
    """
    使用 rasterio 打开地理TIF文件，返回 dataset 和其像素值数组。
    """
    dataset = rasterio.open(file_path)
    image_array = dataset.read()  # 形状通常是 [波段数, 高度, 宽度]
    return dataset, image_array

def transform_coordinate(col, row, transform, src_crs="EPSG:4548", dst_crs="EPSG:4490"):
    """
    根据 transform (仿射变换参数) 和给定的源/目标CRS，
    将像素坐标 (col, row) 转化为地理坐标 (lon, lat)。
    """
    x, y = transform * (col, row)
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat

def decimal_degrees_to_dms(deg, is_lat=False):
    """
    将十进制度数转化为度分秒格式的字符串。
    形如 "113°30′06.2313″E" 或 "22°30′06.2313″N"
    """
    if is_lat:
        suffix = 'N' if deg >= 0 else 'S'
    else:
        suffix = 'E' if deg >= 0 else 'W'

    deg_abs = abs(deg)
    d = int(deg_abs)
    m_float = (deg_abs - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60

    return f"{d:02d}°{m:02d}′{s:.4f}″{suffix}"

def get_altitude(dataset, col, row):
    """
    尝试从给定 dataset 中读取海拔数值。如果 dataset 不包含有效高程数据，则返回0.0
    """
    if not dataset:
        return 0.0
    try:
        row_i = int(round(row))
        col_i = int(round(col))
        alt_value = dataset.read(1)[row_i, col_i]
        return float(alt_value)
    except:
        return 0.0

def get_altitude_dsm(dsm_dataset, col, row):
    """
    从 DSM 数据集读取海拔值。若无 dsm_dataset，则返回0.0
    """
    if not dsm_dataset:
        return 0.0
    try:
        row_i = int(round(row))
        col_i = int(round(col))
        alt_value = dsm_dataset.read(1)[row_i, col_i]
        return float(alt_value)
    except:
        return 0.0

def export_csv(coord_list, out_path):
    """
    将坐标列表 (每个元素都是包含以下键的字典：
      {
        "index": int,
        "type": str,    # 测点类型
        "lat": str,     # 纬度(度分秒或十进制)
        "lon": str,     # 经度(度分秒或十进制)
        "alt": float,   # 海拔高程
        "desc": str     # 测点说明
      }
    ) 输出到 CSV 文件。
    """
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "测点类型", "纬度", "经度", "海拔高程", "测点说明"])
        for item in coord_list:
            writer.writerow([
                item["index"],
                item["type"],
                item["lat"],
                item["lon"],
                item["alt"],
                item["desc"]
            ])
