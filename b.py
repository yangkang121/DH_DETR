import os
import cv2
import xml.etree.ElementTree as ET
import numpy as np

def draw_annotation_from_xml(xml_path, img_dir, save_dir, 
                             color=(0, 255, 0), line_width=2, font_scale=0.5):
    """
    从自定义XML标注文件读取segm分割点，在原图上绘制多边形+类别标签
    :param xml_path: 单个XML标注文件路径
    :param img_dir: 原图存放目录（与XML中filename对应）
    :param save_dir: 标注后图片的保存目录
    :param color: 绘制颜色，BGR格式（默认绿色(0,255,0)）
    :param line_width: 多边形线宽（默认2）
    :param font_scale: 标签字体缩放（默认0.5）
    """
    # 1. 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 2. 解析XML文件
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # 3. 获取图片名+清理路径+读取原图（核心修改：处理 ..\ 无效路径）
    raw_img_path = root.find('filename').text  # 读取XML中的原始路径（含 ..\）
    img_name = os.path.basename(raw_img_path)  # 提取纯文件名（忽略所有路径标识符）
    img_path = os.path.join(img_dir, img_name)  # 拼接有效绝对路径
    img = cv2.imread(img_path)
    if img is None:
        print(f"警告：未找到图片 {img_path}，跳过该标注")
        return
    
    # 4. 遍历所有object，绘制每个目标的分割多边形+标签
    for obj in root.findall('object'):
        # 获取类别名称
        cls_name = obj.find('name').text
        # 获取segm下的所有point节点
        point_nodes = obj.find('segm').findall('point')
        # 解析分割点坐标：转换为np.array([[x1,y1],[x2,y2],...])格式
        seg_pts = []
        for p in point_nodes:
            x, y = map(int, p.text.split(','))
            seg_pts.append([x, y])
        seg_pts = np.array(seg_pts, np.int32)
        
        # 5. 绘制分割多边形轮廓（OpenCV要求坐标为reshape(-1,1,2)）
        cv2.polylines(img, [seg_pts.reshape(-1, 1, 2)], 
                      isClosed=True, color=color, thickness=line_width)
        
        # 6. 绘制类别标签（放在多边形左上角）
        label_xy = (seg_pts[0][0], seg_pts[0][1]-10)  # 标签位置：第一个点左上10像素
        cv2.putText(img, cls_name, label_xy, 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, line_width)
    
    # 7. 保存标注后的图片
    save_path = os.path.join(save_dir, img_name)
    cv2.imwrite(save_path, img)
    print(f"标注完成：{save_path}")

def batch_draw_annotation(xml_dir, img_dir, save_dir, 
                          color=(0,255,0), line_width=2, font_scale=0.5):
    """
    批量处理目录下所有XML文件，在对应原图上绘制标注
    :param xml_dir: XML标注文件存放目录（即你生成的SAR-Ship/XML）
    :param img_dir: 原图目录（即JPEGImages）
    :param save_dir: 标注后图片保存目录
    """
    # 遍历目录下所有.xml文件
    for file_name in os.listdir(xml_dir):
        if file_name.endswith('.xml'):
            xml_path = os.path.join(xml_dir, file_name)
            draw_annotation_from_xml(xml_path, img_dir, save_dir, color, line_width, font_scale)

if __name__ == "__main__":
    # ************************ 配置路径（修改为你的实际路径） ************************
    XML_DIR = r"F:\SAR-Ship\XML"          # 生成的XML标注文件目录
    IMG_DIR = r"F:\SAR-Ship\images"   # 原图存放目录（与XML中filename对应）
    SAVE_DIR = r"F:\SAR-Ship\Annotated_Images"  # 标注后图片的保存目录（自动创建）
    # ************************ 自定义绘制样式（可选） ************************
    DRAW_COLOR = (0, 255, 0)    # 绘制颜色：BGR格式，绿色(0,255,0)、红色(0,0,255)、蓝色(255,0,0)
    LINE_WIDTH = 2              # 轮廓线宽
    FONT_SCALE = 0.6            # 标签字体大小
    # 执行批量绘制
    batch_draw_annotation(XML_DIR, IMG_DIR, SAVE_DIR, DRAW_COLOR, LINE_WIDTH, FONT_SCALE)