"""生成 VisualDuipai 应用图标（二分叉再汇聚设计）"""

from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 260
MARGIN = 28

BLUE = (31, 111, 235, 255)       # #1f6feb
ORANGE = (219, 109, 40, 255)     # #db6d28
WHITE_BG = (255, 255, 255, 255)

CX = SIZE // 2                     # 130
CY = SIZE // 2
START = (MARGIN + 10, CY)         # 起点 (38, 130)
END = (SIZE - MARGIN - 10, CY)    # 终点 (222, 130)

DIAMOND_CX = CX + 14              # 菱形中心偏右 (144)
DIAMOND_R = 28                    # 菱形半对角线长
SPLIT_X = CX - 50                 # 分叉点 x (80)
SPLIT_Y_OFFSET = 42               # 分叉上下偏移
DOT_R = 10                        # 起点圆半径
ARROW_H = 16                      # 箭头高
ARROW_W = 10                      # 箭头宽

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 背景圆底衬
circle_r = 100
circle_bbox = (CX - circle_r, CY - circle_r, CX + circle_r, CY + circle_r)
draw.ellipse(circle_bbox, fill=(31, 111, 235, 25))

# 菱形四顶点
diamond_left   = (DIAMOND_CX - DIAMOND_R, CY)
diamond_top    = (DIAMOND_CX, CY - DIAMOND_R)
diamond_bottom = (DIAMOND_CX, CY + DIAMOND_R)
diamond_right  = (DIAMOND_CX + DIAMOND_R, CY)

# 分叉点
split_upper = (SPLIT_X, CY - SPLIT_Y_OFFSET)   # (80, 88)
split_lower = (SPLIT_X, CY + SPLIT_Y_OFFSET)   # (80, 172)

# 上路径：起点 → 上分叉 → 菱形左顶点
for i, (p1, p2) in enumerate([(START, split_upper), (split_upper, diamond_left)]):
    draw.line([p1, p2], fill=(*BLUE[:3], 220), width=6)

# 下路径：起点 → 下分叉 → 菱形左顶点
for p1, p2 in [(START, split_lower), (split_lower, diamond_left)]:
    draw.line([p1, p2], fill=(*BLUE[:3], 220), width=6)

# 起点圆
draw.ellipse(
    (START[0] - DOT_R, START[1] - DOT_R, START[0] + DOT_R, START[1] + DOT_R),
    fill=BLUE,
)

# 菱形判断节点
diamond_pts = [diamond_top, diamond_right, diamond_bottom, diamond_left]
draw.polygon(diamond_pts, fill=WHITE_BG, outline=ORANGE, width=4)

# 菱形内部 "?" 符号
bar_h = 14
dot_off = 8
draw.line(
    [(DIAMOND_CX, CY - bar_h), (DIAMOND_CX, CY + dot_off - 6)],
    fill=ORANGE, width=4,
)
draw.ellipse(
    (DIAMOND_CX - 3, CY + dot_off - 3, DIAMOND_CX + 3, CY + dot_off + 3),
    fill=ORANGE,
)

# 输出箭头
arrow_start = (diamond_right[0] + 2, CY)
arrow_body_end = (END[0] - ARROW_W, CY)
draw.line([arrow_start, arrow_body_end], fill=BLUE, width=6)

# 箭头尖
arrow_pts = [
    END,
    (END[0] - ARROW_W, END[1] - ARROW_H // 2),
    (END[0] - ARROW_W, END[1] + ARROW_H // 2),
]
draw.polygon(arrow_pts, fill=BLUE)

# 标签（无字体时跳过）
try:
    from PIL import ImageFont
    font = ImageFont.load_default()
    draw.text(
        (SPLIT_X + 8, CY - SPLIT_Y_OFFSET - 20),
        "brute", fill=(*BLUE[:3], 180), font=font,
    )
    draw.text(
        (SPLIT_X + 8, CY + SPLIT_Y_OFFSET + 6),
        "solve", fill=(*BLUE[:3], 180), font=font,
    )
except Exception:
    pass

# 保存
out_path = Path(__file__).resolve().parent / "VisualDuipai.png"
img.save(out_path, "PNG")
print(f"Icon saved: {out_path} ({img.size[0]}x{img.size[1]})")
