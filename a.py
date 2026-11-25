import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def labelme_json_to_custom_xml(json_path, save_dir=None, image_dir=None):
    """
    将单个 LabelMe JSON 文件转换为你需要的自定义 XML 格式（包含 <segm> 节点）
    :param json_path: LabelMe 生成的 JSON 文件路径
    :param save_dir: XML 文件保存目录（默认与 JSON 文件同目录）
    :param image_dir: 图片所在目录（若 JSON 中图片路径无效，可指定该目录）
    """
    # 1. 配置默认路径
    if save_dir is None:
        save_dir = os.path.dirname(json_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 2. 读取 JSON 文件
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # 3. 提取核心信息
    json_filename = os.path.basename(json_path)
    xml_filename = os.path.splitext(json_filename)[0] + '.xml'
    xml_save_path = os.path.join(save_dir, xml_filename)
    
    # 图片信息
    image_filename = json_data['imagePath']
    image_width = json_data['imageWidth']
    image_height = json_data['imageHeight']
    image_depth = 3  # 默认为 3 通道（RGB），灰度图可改为 1
    folder_name = "JPEGImages"  # 匹配你示例中的 <folder> 内容
    
    # 验证并补充图片路径（可选，不影响核心格式）
    if image_dir is not None:
        full_image_path = os.path.join(image_dir, image_filename)
        if os.path.exists(full_image_path):
            # 若需通过图片获取真实尺寸，可安装 opencv-python 后启用以下代码
            # import cv2
            # img = cv2.imread(full_image_path)
            # if img is not None:
            #     image_height, image_width, image_depth = img.shape
            pass
    
    # 4. 构建 XML 根节点
    root = ET.Element("annotation")
    
    # 4.1 添加基本信息节点（严格匹配你的示例格式）
    ET.SubElement(root, "folder").text = folder_name
    ET.SubElement(root, "filename").text = image_filename
    ET.SubElement(root, "path").text = folder_name  # 匹配你示例中的 <path> 内容
    
    # 4.2 添加图片尺寸节点
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(image_width)
    ET.SubElement(size, "height").text = str(image_height)
    ET.SubElement(size, "depth").text = str(image_depth)
    
    # 4.3 遍历每个实例，添加 object 节点
    for shape in json_data['shapes']:
        # 提取实例信息
        class_name = shape['label']
        points = shape['points']  # 多边形坐标列表，格式：[[x1,y1], [x2,y2], ...]
        
        # 跳过无有效坐标的实例
        if len(points) < 2:
            continue
        
        # 4.4 构建 object 节点（严格匹配你的示例）
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = class_name
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"
        
        # 4.5 构建 <segm> 节点（核心需求：内部直接罗列 <point> 标签）
        segm = ET.SubElement(obj, "segm")
        for (x, y) in points:
            # 格式化坐标为 int 类型，拼接为 "x,y" 格式
            point_text = f"{int(x)},{int(y)}"
            ET.SubElement(segm, "point").text = point_text
    
    # 5. 格式化 XML 并保存（保持代码整洁，匹配你的示例格式）
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    # 去除多余空行和默认的 xml 声明行（严格匹配你的示例）
    xml_lines = [line for line in xml_str.split('\n') if line.strip()]
    final_xml_str = '\n'.join(xml_lines[1:])  # 去除第一行的 <?xml ...?> 声明
    
    with open(xml_save_path, 'w', encoding='utf-8') as f:
        f.write(final_xml_str)
    
    print(f"转换完成：{xml_save_path}")

def batch_convert_json_to_xml(json_dir, save_dir=None, image_dir=None):
    """
    批量转换指定目录下所有 LabelMe JSON 文件为自定义 XML 文件
    :param json_dir: 存放 JSON 文件的目录
    :param save_dir: XML 文件保存目录（默认与 JSON 目录同目录）
    :param image_dir: 图片所在目录（可选）
    """
    if save_dir is None:
        save_dir = json_dir
    
    # 遍历目录下所有 .json 文件
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            json_path = os.path.join(json_dir, filename)
            labelme_json_to_custom_xml(json_path, save_dir, image_dir)

if __name__ == "__main__":
    # ************************ 配置参数 ************************
    # 批量转换示例（推荐，匹配你之前的目录结构）
    JSON_DIRECTORY = r"F:\SAR-Ship\Anno"  # 你的 JSON 文件存放目录
    XML_SAVE_DIRECTORY = r"F:\SAR-Ship\XML"  # 转换后 XML 保存目录（对应 F:\SAR-Ship\XML）
    IMAGE_DIRECTORY = r"F:\SAR-Ship\images"  # 图片存放目录（可选，无需 cv2 依赖）
    # **********************************************************
    
    # 执行批量转换
    batch_convert_json_to_xml(JSON_DIRECTORY, XML_SAVE_DIRECTORY, IMAGE_DIRECTORY)
