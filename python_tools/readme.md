# python 趣味实用小工具

## 概述
用python实现的三个趣味实用小工具: **图片转Execl工具** , **图片转TXT工具** , **二维码生成工具** .

## 准备工作

### 系统需求
所有的代码都是基于 **python3** 的, 所以需要事先安装好 **python3** ,并设置好环境.
安装方法详见:
 [廖雪峰Python3教程-安装Python3](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014316090478912dab2a3a9e8f4ed49d28854b292f85bb000) 
[官方安装教程-英文](https://docs.python.org/3/using/windows.html#installing-python)

### 安装必备库
> 注意: 安装过程中建议以管理员权限运行执行以下命令.

* 安装PIL图片处理库
```bash
pip install pillow
```
* 安装qrcode二维码处理工具
```bash
pip install qrcode
```
* 安装openpyxl Execl表格处理工具
```bash
pip install openpyxl
```
### 右键菜单添加"复制文件路径"功能
#### Win7系统
如果使用的是Win7系统, 可以把以下代码保存为 **复制文件路径.reg** 文件, 双击运行添加注册表, 就可以实现一键复制文件路径功能.

> 复制文件路径.reg

```bash
Windows Registry Editor Version 5.00
;文件
[HKEY_CLASSES_ROOT\*\shell\copypath]
@="复制文件路径"
[HKEY_CLASSES_ROOT\*\shell\copypath\command]
;@="mshta vbscript:clipboarddata.setdata(\"text\",\"%1\")(close)"
;带引号
;@="cmd.exe /c echo \"%1\"|clip"
;不带引号
@="cmd.exe /c echo %1|clip"

;文件夹
[HKEY_CLASSES_ROOT\Directory\shell\copypath]
@="复制文件夹路径"
[HKEY_CLASSES_ROOT\Directory\shell\copypath\command]
;@="mshta vbscript:clipboarddata.setdata(\"text\",\"%1\")(close)"
;带引号
;@="cmd.exe /c echo \"%1\"|clip"
;不带引号
@="cmd.exe /c echo %1|clip"
```
**使用方法:** 在任意文件或文件夹上单击鼠标右键选择 **复制文件路径** ,就可以很方便的把文件或文件夹的路径复制到剪切板中. 如下图:

![邮件复制文件路径功能](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/copy_file_path.jpg)

#### Win10系统
Win10系统自带了 **复制路径功能** .
**使用方法:** 先按住 *Shift* 键, 然后在任意文件或文件夹上单击鼠标右键选择 **复制路径** ,就可以很方便的把文件或文件夹的路径复制到剪切板中. 不过Win10自带的  **复制路径** 功能复制的结果包含引号,需要自己根据需要手动删除.

## 图片转Execl工具

### 概述
这是一个用于把图片转换成Execl表格的Python小工具, 用到了pillow、openpyxl、等第三方库。 
原理是打开一幅图片, 先对图片进行格式转换个缩放, 然后依次读取图片每个像素的RGB值, 然后把该值作为Excel表格中对应单元格的背景色.最后再把每个单元格设置为高度与宽度相等的小正方形. 详见代码注释.

### 源代码

> py_img_to_excel.py

```py
from openpyxl.workbook import Workbook#导入Workbook库用与操作Execl工作簿
from openpyxl.styles import PatternFill, Color#导入PatternFill,Color库用与操作Execl单元格
from PIL import Image#导入Image库用与操作图片文件
import datetime

#把一个整数值转换成26进制字符串
#因为execl单元格的行坐标是26进制的, 比如"A", "Z", "AA", "AZ"
def dec_to_base26(d):
    s = ""
    m = 0
    while d > 0:
        m = d % 26
        if m == 0:
            m = 26
        s = "{0:c}{1:s}".format(m+64, s)
        d = (d - m) // 26
    return s

#把一个26进制字符串转换成整数值
def base26_to_dec(s):
    d = 0
    j = 1
    st = s.upper()
    for x in range(0, len(st))[::-1]:
        c = ord(st[x])
        if c < 65 and c > 90:
            return 0
        d += (c - 64) * j
        j *= 26
    return d

#把一个整数坐标转换成Execl坐标
#Execl坐标的行坐标是26进制的, 列坐标是10进制的,比如(AA, 100)
def decxy_to_excelxy(x, y):
    return("{0:s}{1:d}".format(dec_to_base26(x), y))

#把像素点的rgb值转换成Execl支持的十六进制字符串, 形如 "AARRGGBB",
#其中AA表示透明度,这里设置为0, 比如 "00FF55FF"
def pixel_to_xrgbstr(pix):
    return ("00{0:02X}{1:02X}{2:02X}".format(pix[0], pix[1], pix[2]))

#图片转Execl函数, imgName 表示带全路径的图片名
def image_to_excel(imgName):

    #创建一个 excel 工作簿
    wb = Workbook()
    ws = wb.active

    #打开图片文件文件
    print("Open Image File [{0}]".format(imgName))
    try:
        img = Image.open(imgName)
    except:
        print("Error to Open [{0}]!!!".format(imgName))

    #判断图片文件的格式, 这里必须为"RGB"格式, 如果不是"RGB"格式, 
    #则用convert函数转换成"RGB"格式.
    if "RGB" == img.mode:
        print("Size{0},Format({1}),Color({2})".format(img.size, img.format, img.mode))
    else:
        print("Not a RGB image file!!!")
        img = img.convert("RGB")
        print("Convert to RGB Success!!!")

    #获取图片文件宽和高
    width = img.size[0]#宽度
    height = img.size[1]#高度

    zoom = 0

    #如果图片文件大于 400*400像素,则对图片进行缩放,缩放比例依照宽度和高度中的最大值
    if width >= height:
        maxsize = width
    else:
        maxsize = height

    if maxsize >= 400:
        zoom = maxsize / 400
        width = int(width / zoom)
        height = int(height / zoom)
        img = img.resize((width, height))
        print("Image Size too large, Resize to", img.size)

    index = 0

    print("Start Process!")
    for w in range(width):#遍历图片的宽度,[0, width)
        #显示处理进度
        index += 1
        print("#", end="")
        if index >= 60:#大于60换行
            index = 0
            print("")

        for h in range(height):#遍历图片的高度[0, height)
            pixel = img.getpixel((w, h))#获取图片当前坐标点的像素值
            loc = decxy_to_excelxy(w+1, h+1)#把整数坐标转换成Execl坐标(字符串)
            #print("LOC", loc)
            c = ws[loc]#选中当前图片像素点坐标对应的Execl单元格
            col = pixel_to_xrgbstr(pixel)#把当前图片像素点的颜色转换成Execl单元格的颜色(字符串)
            #print("COL", col)
            #用当前图片像素点的颜色填充单元格底色
            cfill = PatternFill(fill_type="solid", start_color=col)
            c.fill = cfill
            #把单元格的宽设置为1,高设置为6, 这样单元格看上去就是一个(小)正方形
            ws.column_dimensions[dec_to_base26(w+1)].width = 1
            ws.row_dimensions[h+1].height = 6

    print("\nProcess Done!")
    #获取当前时间,转换成字符串
    timenow = datetime.datetime.now()
    timestr = timenow.strftime("%Y-%m-%d-%H-%M-%S")
    #生成的Execl文件名用<原图片文件名+ 当前时间字符串+ "..xlsx"后缀>作为文件名
    namestr = "{0}-{1}.xlsx".format(imgName, timestr)
    print("Save File As [{0}]".format(namestr))
    #保存新生成的Execl文件
    wb.save(namestr)
    print("Save Done!")

name = input("Please Input Image File Name:")
print("Start......")
try:
    image_to_excel(name)
except:
    print("Error!!!!!!")
print("Over......")
```
为了方便使用这个工具, 而不需要每次都打开cmd手动执行 **python py_img_to_excel.py**命令, 可以新建一个 **Img2Excel.bat** 脚本文件, 脚本内容如下. 把这个脚本文件和 **py_img_to_excel.py** 文件放在同一文件夹下, 然后把该脚本文件发送到桌面快捷方式, 以后直接双节这个脚本文件就可以直接运行 **py_img_to_excel.py** 了

> Img2Excel.bat

```bash
@echo off
set cur_path="%cd%\py_img_to_excel.py"
python %cur_path%
pause
```


### 运行方法
直接双击桌面 **Img2Excel.bat** 快捷方式就可以运行本工具, 然后程序等待用户输入一个带全路径的图片文件名, 这里可以使用刚才的 **复制文件路径** 工具直接复制图片路径粘贴过来即可.

![图片文件](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/huaji.jpg)

![执行过程|](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/img2excel_bat.jpg)

![执行结果](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/img2excel_xls.jpg)


## 图片转TxT工具

### 概述
这是一个用于把图片转换成TXT文件的Python小工具, 用到了pillow等第三方库.
原理是打开一幅图片, 先对图片进行格式转换个缩放, 然后对图像二值化, 转换成纯黑白的图像, 接着依次读取图片每个像素的值写入到文本文件中, 如果该值不为0则写入 **@** ,否则写入 **空格** , 详见代码注释.

### 源代码

> py_img_to_txt.py

```py
from PIL import Image#导入Image库用与操作图片文件
import datetime

def image_to_txt(imgName):
    #获取当前时间,转换成字符串
    timenow = datetime.datetime.now()
    timestr = timenow.strftime("%Y-%m-%d-%H-%M-%S")
    #生成的Txt文件用<原图片文件名+ 当前时间字符串+ ".txt"后缀>作为文件名
    namestr = "{0}-{1}.txt".format(imgName, timestr)
    
    #打开或创建一个TxT文件文件
    txt = open(namestr, "w+")
    
    #打开图片文件文件
    print("Open Image File [{0}]".format(imgName))
    try:
        img = Image.open(imgName)
    except:
        print("Error to Open [{0}]!!!".format(imgName))

    #判断图片文件的格式, 这里必须为"RGB"格式, 如果不是"RGB"格式, 
    #则用convert函数转换成"RGB"格式.
    if "RGB" == img.mode:
        print("Size{0},Format({1}),Color({2})".format(img.size, img.format, img.mode))
    else:
        print("Not a RGB image file!!!")
        img = img.convert("RGB")
        print("Convert to RGB Success!!!")

    #获取图片文件宽和高
    width = img.size[0]
    height = img.size[1]

    zoom = 0

    #如果图片文件大于 400*400像素,则对图片进行缩放,缩放比例依照宽度和高度中的最大值
    if width >= height:
        maxsize = width
    else:
        maxsize = height
    if maxsize >= 400:
        zoom = maxsize / 400
        width = int(width / zoom)
        height = int(height / zoom)
        img = img.resize((width, height))
        print("Image Size too large, Resize to", img.size)
    
    #把图片文件转换成纯黑白的图片
    img = img.convert("1")
    index = 0

    print("Start Process!")
    for w in range(width):#遍历图片的宽度,[0, width)
        #显示处理进度
        index += 1
        print("#", end="")
        txt.write("/*")
        if index >= 60:#大于60换行
            index = 0
            print("")

        for h in range(height):#遍历图片的高度[0, height)
            pixel = img.getpixel((w, h))#获取图片当前坐标点的像素值
            #print("w=", w, "h=", h, "pixel=", pixel)
            if pixel != 0:#因为是纯黑白图像,所以像素颜色只有0或255两种值
                txt.write("_")#非0则往txt中写入"_"表示白色
                #print("w=", w, "h=", h, "pixel=", pixel)
            else:
                txt.write("@")#0则往txt中写入"@"表示黑色
                #print("w=", w, "h=", h, "pixel=", pixel)
        txt.write("*/")
        txt.write("\n")

    #保存新生成的TXT文件
    print("\nProcess Done!")
    print("Save File As [{0}]".format(namestr))
    txt.close()
    print("Save Done!")

name = input("Please Input Image File Name:")
print("Start......")
try:
    image_to_txt(name)
except:
    print("Error!!!!!!")
print("Over......")


```
为了方便使用这个工具, 而不需要每次都打开cmd手动执行 **python py_img_to_txt.py**命令, 可以新建一个 **Img2Txt.bat** 脚本文件, 脚本内容如下. 把这个脚本文件和 **py_img_to_txt.py** 文件放在同一文件夹下, 然后把该脚本文件发送到桌面快捷方式, 以后直接双节这个脚本文件就可以直接运行 **py_img_to_txt.py** 了

> Img2Txt.bat

```bash
@echo off
set cur_path="%cd%\py_img_to_txt.py"
python %cur_path%
pause
```

### 运行方法
直接双击桌面 **Img2Txt.bat** 快捷方式就可以运行本工具, 然后程序等待用户输入一个带全路径的图片文件名, 这里可以使用刚才的 **复制文件路径** 工具直接复制图片路径粘贴过来即可.

![图片文件](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/zhebizhuangdebuxing.png)

![执行过程|](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/img2txt_bat.jpg)

![执行结果](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/img2txt_txt.jpg)

> 关于运行结果中的 *图片* 相对与原图片反转了的问题, 可能与系统有关, 有待进一步验证, 同一份代码, 我在家里的Win10上运行就是正常的, 但是在公司的Win7上运行就反转了.

## 图片转TxT工具

### 概述
这是一个用于快速生成二维码的Python小工具, 用到了qrcode等第三方库.
qrcode库提供了非常方便快捷的生成二维码的接口, 这里使用了默认的方式, 把输入的文本转化成二维码图片保存在桌面上. 详见代码注释.

### 源代码

> py-get-qrcode.py

```py
import qrcode#导入qrcode库, 用于生成二维码
import datetime#导入datetime库用于生成带时间的图片名
import os,getpass#导入getpass库用于获取系统的用户名

#输入待转换的字符串
qrstr = input("Enter the string to be converted:")
print("Input :"+qrstr)

#采用默认方式生成二维码
qrimg = qrcode.make(qrstr)

#获取当前时间,转化成字符串
timenow = datetime.datetime.now()
timestr = timenow.strftime("%Y-%m-%d-%H-%M-%S")

#生成带时间的二维码图片名,图片保存在桌面上
qrname = "C:\\Users\\{0}\\Desktop\\{1}.png".format(getpass.getuser(), timestr)
print("Save as :", qrname)

#保存二维码图片
qrimg.save(qrname)
print("Success!")
```
为了方便使用这个工具, 而不需要每次都打开cmd手动执行 **python py-get-qrcode.py**命令, 可以新建一个 **GetQRcode.bat** 脚本文件, 脚本内容如下. 把这个脚本文件和 **py-get-qrcode.py** 文件放在同一文件夹下, 然后把该脚本文件发送到桌面快捷方式, 以后直接双节这个脚本文件就可以直接运行 **py-get-qrcode.py** 了

> GetQRcode.bat

```bash
@echo off
set cur_path="%cd%\py-get-qrcode.py"
echo %cur_path%
python %cur_path%
pause
```

### 运行方法
直接双击桌面 **GetQRcode.bat** 快捷方式就可以运行本工具, 然后程序等待用户输入待转换的文本

![执行过程|](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/getqrcode_bat.jpg)

![执行结果](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/wnavy.com.png)


## 项目内文件截图

![程序文件截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/project_tree0.jpg)

![结果文件截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_tools/project_tree.jpg)
