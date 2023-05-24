# 导入所需的库
from tkinter import filedialog
import pandas as pd
import tkinter as tk  # 导入tkinter库，用来创建图形界面
import os  # 导入os库，用来处理文件和目录
from PIL import Image, ImageTk  # 导入PIL库，用来处理图片

folder_path = "../datasets/1"  # 定义文件夹路径

window = tk.Tk()  # 创建一个窗口
window.title("图片查询")  # 设置窗口标题
window.geometry("800x600")  # 设置窗口大小
window.configure(bg="#F0F0F0")  # 设置窗口背景颜色为浅灰色

# 创建一个框架放在窗口中，用来放置输入框和按钮
frame_input = tk.Frame(window, bg="#F0F0F0")
frame_input.pack(pady=20)

# 创建两个标签显示开始日期和结束日期
label_start = tk.Label(frame_input, text="开始日期", font=("Arial", 16), bg="#F0F0F0")
label_start.grid(row=0, column=0, padx=10)
label_end = tk.Label(frame_input, text="结束日期", font=("Arial", 16), bg="#F0F0F0")
label_end.grid(row=1, column=0, padx=10)

# 创建两个输入框接收用户输入的日期范围
entry_start = tk.Entry(frame_input, font=("Arial", 16))
entry_start.grid(row=0, column=1, padx=10)
entry_end = tk.Entry(frame_input, font=("Arial", 16))
entry_end.grid(row=1, column=1, padx=10)


# 定义一个函数查询结果并显示在界面上
def query_result():
    global df  # 定义一个全局变量存储数据框
    df = pd.DataFrame(columns=["日期", "图片路径", "类别"])  # 创建一个空的数据框，有三列：日期，图片路径，类别
    for file in os.listdir(folder_path):  # 遍历文件夹中的每个文件
        ext = os.path.splitext(file)[1]  # 获取文件的扩展名
        if ext in [".jpg", ".png"]:  # 如果是图片文件
            date = pd.to_datetime(file.split("_")[0])  # 提取图片文件名中的日期部分，并转换成日期对象
            path = os.path.join(folder_path, file)  # 拼接图片文件的完整路径
            category = file.split("_")[-1].split(".")[0]  # 提取图片文件名中的类别部分，即ok或者ng
            df = pd.concat([df, pd.DataFrame({"日期": [date], "图片路径": [path], "类别": [category]})],
                           ignore_index=True)  # 将这一行数据添加到数据框中

    start_date = pd.to_datetime(entry_start.get())  # 获取输入框中的开始日期，并转换成日期对象
    end_date = pd.to_datetime(entry_end.get())  # 获取输入框中的结束日期，并转换成日期对象
    df = df[(df["日期"] >= start_date) & (df["日期"] <= end_date)]  # 筛选出在日期范围内的数据

    df = df.reindex(pd.date_range(start_date, end_date))  # 补全所有日期

    summary_df = df["类别"].value_counts(normalize=True).to_frame().T  # 对数据框按照类别进行分组统计，计算每个类别的占比，并转换成宽表形式
    summary_df["ok"] = summary_df["ok"].apply(lambda x: f"{x:.2%}")  # 将ok列的数值转换成百分比格式，保留两位小数
    summary_df["ng"] = summary_df["ng"].apply(lambda x: f"{x:.2%}")  # 将ng列的数值转换成百分比格式，保留两位小数

    label_result.config(text="查询结果如下：")  # 更新标签显示查询结果

    for widget in frame_result.winfo_children():  # 清空结果框架中的所有组件
        widget.destroy()

    dates = sorted(df["日期"].unique())  # 获取所有不重复的日期，并按照升序排序

    labels_date = [tk.Label(frame_result, text=date, font=("Arial", 16), bg="#F0F0F0") for date in
                   dates]  # 创建一个标签列表显示每个日期

    labels_ok_ratio = []  # 创建一个空列表存储每个标签显示每个日期对应的ok占比
    for date in dates:
        if summary_df.index.contains(date):
            labels_ok_ratio.append(
                tk.Label(frame_result, text=summary_df.loc[date]["ok"], font=("Arial", 16), bg="#F0F0F0"))
        else:
            labels_ok_ratio.append(tk.Label(frame_result, text="0%", font=("Arial", 16), bg="#F0F0F0"))

    labels_ng_ratio = []  # 创建一个空列表存储每个标签显示每个日期对应的ng占比
    for date in dates:
        if summary_df.index.contains(date):
            labels_ng_ratio.append(
                tk.Label(frame_result, text=summary_df.loc[date]["ng"], font=("Arial", 16), bg="#F0F0F0"))
        else:
            labels_ng_ratio.append(tk.Label(frame_result, text="0%", font=("Arial", 16), bg="#F0F0F0"))

    buttons_view = [tk.Button(frame_result, text="查看", font=("Arial", 16),
                              command=lambda: show_images(date)) for date in
                    dates]  # 创建一个按钮列表查看每个日期内的所有图片，点击时调用show_images函数，并传入当前日期作为参数

    for i in range(len(dates)):  # 遍历每个日期
        labels_date[i].grid(row=i, column=0)  # 将标签放在结果框架中的第i行第0列
        labels_ok_ratio[i].grid(row=i, column=1)  # 将标签放在结果框架中的第i行第1列
        labels_ng_ratio[i].grid(row=i, column=2)  # 将标签放在结果框架中的第i行第2列
        buttons_view[i].grid(row=i, column=3)  # 将按钮放在结果框架中的第i行第3列

    for widget in frame_images.winfo_children():  # 清空图片框架中的所有组件
        widget.destroy()

    global canvas, scrollbar  # 定义两个全局变量存储画布和滚动条

    canvas = tk.Canvas(frame_images)  # 创建一个画布放在图片框架中
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_images, orient=tk.VERTICAL, command=canvas.yview)  # 创建一个垂直滚动条放在图片框架中，并绑定画布的y轴滚动命令
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)  # 配置画布使用滚动条


def show_images(date): # 定义一个函数显示某个日期内的所有图片
    sub_df = df[df["日期"] == date] # 筛选出该日期对应的数据子集

    canvas.delete("all") # 清空画布中的所有内容

    global image_frame # 定义一个全局变量存储图片框架

    image_frame = tk.Frame(canvas) # 创建一个新的框架放在画布中

    canvas.create_window((0, 0), window=image_frame, anchor="nw") # 在画布上创建一个窗口，并将新的框架放入其中

    images = [Image.open(path) for path in sub_df["图片路径"]] # 打开每个图片文件并存入列表中
    images = [image.thumbnail((100, 100)) for image in images] # 缩放每个图片大小为100x100像素并存入列表中
    photos = [ImageTk.PhotoImage(image) for image in images] # 将每个图片转换成tkinter可用的格式并存入列表中
    labels_image = [tk.Label(image_frame, image=photo) for photo in photos] # 创建一个标签列表显示每个图片

    for label_image in labels_image:
        label_image.image = photos # 防止图片被垃圾回收机制回收

    if df["日期"].contains(date): # 如果存在这个日期
        for j in range(len(sub_df)):
            labels_image[j].grid(row=j // 5, column=j % 5) # 将标签放在新的框架中的第j//5行第j%5列（每行最多显示5张图片）
    else: # 如果不存在这个日期
        label_no_image = tk.Label(image_frame, text="没有图片", font=("Arial", 16)) # 创建一个标签显示没有图片
        label_no_image.grid(row=0, column=0) # 将标签放在新的框架中的第0行第0列

    canvas.update_idletasks() # 更新画布状态

    canvas.configure(scrollregion=canvas.bbox("all")) # 配置画布滚动区域为所有内容

# 创建一个按钮查询结果，点击时调用query_result函数
button_query = tk.Button(frame_input, text="查询", font=("Arial", 16), command=query_result)
button_query.grid(row=0, column=2, rowspan=2, padx=10)

# 创建一个标签显示查询结果
label_result = tk.Label(window, text="", font=("Arial", 16), bg="#F0F0F0")
label_result.pack(pady=20)

# 创建一个框架放在窗口中，用来放置结果表格
frame_result = tk.Frame(window, bg="#F0F0F0")
frame_result.pack()

# 创建一个框架放在窗口中，用来放置图片画布和滚动条
frame_images = tk.Frame(window)
frame_images.pack()

window.mainloop() # 进入窗口主循环
