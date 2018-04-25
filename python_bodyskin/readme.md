# Python人体肤色检测

## 概述
本文中的人体肤色检测功能采用 [OpenCV](https://opencv.org/) 库实现, OpenCV是一个基于BSD许可（开源）发行的跨平台计算机视觉库，可以运行在Linux、Windows、Android和Mac OS操作系统上. 它轻量级而且高效——由一系列 C 函数和少量 C++ 类构成，同时提供了Python、Ruby、MATLAB等语言的接口，实现了图像处理和计算机视觉方面的很多通用算法.

本文主要使用了OpenCV的图像色域转换, 颜色通道分割, 高斯滤波, OSTU自动阈值等功能.

## 参考资料

[OpenCV探索之路:皮肤检测技术](http://www.cnblogs.com/skyfsm/p/7868877.html)

[学习OpenCV—肤色检测](https://blog.csdn.net/yangtrees/article/details/7439625)

## 准备工作

### 安装 ***Python-OpenCV*** 库

```bash
pip install opencv-python -i https://mirrors.ustc.edu.cn/pypi/web/simple
```
> 利用 ***-i*** 为pip指令镜像源, 这里使用电子科技大学的源, 速度比官方源更快.

### 安装 ***Numpy*** 科学计算库
```bash
pip install numpy -i https://mirrors.ustc.edu.cn/pypi/web/simple
```
## 图像的基本操作
```py
import numpy as np
import cv2

imname =  "6358772.jpg"

# 读入图像
'''
使用函数 cv2.imread() 读入图像。这幅图像应该在此程序的工作路径，或者给函数提供完整路径.
警告：就算图像的路径是错的，OpenCV 也不会提醒你的，但是当你使用命令print(img)时得到的结果是None。
'''
img = cv2.imread(imname, cv2.IMREAD_COLOR)
'''
imread函数的第一个参数是要打开的图像的名称(带路径)
第二个参数是告诉函数应该如何读取这幅图片. 其中
	cv2.IMREAD_COLOR 表示读入一副彩色图像, alpha 通道被忽略, 默认值
	cv2.IMREAD_ANYCOLOR 表示读入一副彩色图像
	cv2.IMREAD_GRAYSCALE 表示读入一副灰度图像
	cv2.IMREAD_UNCHANGED 表示读入一幅图像，并且包括图像的 alpha 通道
'''

# 显示图像
'''
使用函数 cv2.imshow() 显示图像。窗口会自动调整为图像大小。第一个参数是窗口的名字，
其次才是我们的图像。你可以创建多个窗口，只要你喜欢，但是必须给他们不同的名字.
'''
cv2.imshow("image", img) # "image" 参数为图像显示窗口的标题, img是待显示的图像数据
cv2.waitKey(0) #等待键盘输入,参数表示等待时间,单位毫秒.0表示无限期等待
cv2.destroyAllWindows() # 销毁所有cv创建的窗口
# 也可以销毁指定窗口:
#cv2.destroyWindow("image") # 删除窗口标题为"image"的窗口

# 保存图像
'''
使用函数 cv2.imwrite() 来保存一个图像。首先需要一个文件名，之后才是你要保存的图像。
保存的图片的格式由后缀名决定.
'''
#cv2.imwrite(imname + "01.png", img) 
cv2.imwrite(imname + "01.jpg", img)
```
### 运行截图
![运行截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_bodyskin/base.jpg)


## 皮肤检测算法

### 基于YCrCb颜色空间的Cr分量+Otsu法阈值分割算法

***YCrCb*** 即 ***YUV*** ，其中 ***Y*** 表示明亮度 **Luminance** 或 **Luma** , 也就是灰阶值. 而 ***U*** 和 ***V*** 表示的则是色度 ***Chrominance*** 或 ***Chroma*** ,作用是描述影像色彩及饱和度, 用于指定像素的颜色. ***亮度*** 是透过RGB输入信号来建立的, 方法是将RGB信号的特定部分叠加到一起. ***色度*** 则定义了颜色的两个方面─色调与饱和度,分别用 ***Cr*** 和 ***Cb*** 来表示. 其中, ***Cr*** 反映了RGB输入信号红色部分与RGB信号亮度值之间的差异. 而 ***Cb*** 反映的是RGB输入信号蓝色部分与RGB信号亮度值之间的差异.

该方法的原理也很简单:
* 将RGB图像转换到 ***YCrCb*** 颜色空间，提取 ***Cr*** 分量图像
* 对 ***Cr*** 分量进行高斯滤波
* 对Cr做自二值化阈值分割处理 ***OSTU***  法

> ***关于高斯滤波***
> 使用低通滤波器可以达到图像模糊的目的。这对与去除噪音很有帮助。其实就是去除图像中的高频成分（比如：噪音，边界）。所以边界也会被模糊一点。（当然，也有一些模糊技术不会模糊掉边界）。OpenCV 提供了四种模糊技术。高斯滤波就是其中一种。实现的函数是 cv2.GaussianBlur()。我们需要指定高斯滤波器的宽和高（必须是奇数）。以及高斯函数沿 X，Y 方向的标准差。如果我们只指定了 X 方向的的标准差，Y 方向也会取相同值。如果两个标准差都是 0，那么函数会根据核函数的大小自己计算。高斯滤波可以有效的从图像中去除高斯噪音。如果你愿意的话，你也可以使用函数 cv2.getGaussianKernel() 自己构建一个高斯滤波器。

```py
# 肤色检测之一: YCrCb之Cr分量 + OTSU二值化
img = cv2.imread(imname, cv2.IMREAD_COLOR)
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb) # 把图像转换到YUV色域
(y, cr, cb) = cv2.split(ycrcb) # 图像分割, 分别获取y, cr, br通道图像


# 高斯滤波, cr 是待滤波的源图像数据, (5,5)是值窗口大小, 0 是指根据窗口大小来计算高斯函数标准差
cr1 = cv2.GaussianBlur(cr, (5, 5), 0) # 对cr通道分量进行高斯滤波
# 根据OTSU算法求图像阈值, 对图像进行二值化
_, skin1 = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 

cv2.imshow("image CR", cr1)
cv2.imshow("Skin Cr+OSTU", skin1 )
```
#### 检测效果
![运行截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_bodyskin/crostu.jpg)

### 基于YCrCb颜色空间Cr, Cb范围筛选法
这个方法跟法一其实大同小异，只是颜色空间不同而已。据资料显示，正常黄种人的Cr分量大约在140至175之间，Cb分量大约在100至120之间。大家可以根据自己项目需求放大或缩小这两个分量的范围，会有不同的效果。

```py
# 肤色检测之二: YCrCb中 140<=Cr<=175 100<=Cb<=120
img = cv2.imread(imname, cv2.IMREAD_COLOR)
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb) # 把图像转换到YUV色域
(y, cr, cb) = cv2.split(ycrcb) # 图像分割, 分别获取y, cr, br通道分量图像

skin2 = np.zeros(cr.shape, dtype=np.uint8) # 根据源图像的大小创建一个全0的矩阵,用于保存图像数据
(x, y) = cr.shape # 获取源图像数据的长和宽

# 遍历图像, 判断Cr和Br通道的数值, 如果在指定范围中, 则置把新图像的点设为255,否则设为0
for i in  range(0, x): 
	for j in  range(0, y):
		if (cr[i][j] >  140) and (cr[i][j] <  175) and (cb[i][j] >  100) and (cb[i][j] <  120):
			skin2[i][j] =  255
		else:
			skin2[i][j] =  0

cv2.imshow(imname, img)
cv2.imshow(imname +  " Skin2 Cr+Cb", skin2)
```
#### 检测效果
![运行截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_bodyskin/crbr.jpg)

### 基于HSV颜色空间H,S,V范围筛选法
这个方法跟上一方法类似，只是颜色空间不同而已。据资料显示，正常黄种人的H分量大约在7至20之间，S分量大约在28至256之间，V分量大约在50至256之间。大家可以根据自己项目需求放大或缩小这两个分量的范围，会有不同的效果。
```py
# 肤色检测之三: HSV中 7<H<20 28<S<256 50<V<256
img = cv2.imread(imname, cv2.IMREAD_COLOR) 
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # 把图像转换到HSV色域
(_h, _s, _v) = cv2.split(hsv) # 图像分割, 分别获取h, s, v 通道分量图像
skin3 = np.zeros(_h.shape, dtype=np.uint8)  # 根据源图像的大小创建一个全0的矩阵,用于保存图像数据
(x, y) = _h.shape # 获取源图像数据的长和宽

# 遍历图像, 判断HSV通道的数值, 如果在指定范围中, 则置把新图像的点设为255,否则设为0
for i in  range(0, x):
	for j in  range(0, y):
		if (_h[i][j] >  7) and (_h[i][j] <  20) and (_s[i][j] >  28) and (_s[i][j] <  255) and (_v[i][j] >  50) and (_v[i][j] <  255):
			skin3[i][j] =  255
		else:
			skin3[i][j] =  0

cv2.imshow(imname, img)
cv2.imshow(imname +  " Skin3 HSV", skin3)
```
#### 检测效果
![运行截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_bodyskin/hsv.jpg)

### 三种检测算法效果对比
![运行截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_bodyskin/BodySkinDetect.jpg)

## 项目内文件截图
![项目内文件截图](https://raw.githubusercontent.com/WHJWNAVY/myImage/master/python_bodyskin/project_file.jpg)

