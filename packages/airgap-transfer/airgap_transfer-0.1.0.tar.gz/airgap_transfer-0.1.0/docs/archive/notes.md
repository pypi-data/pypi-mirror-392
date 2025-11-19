
适合气隙环境、无网络场景或需要物理隔离的数据传输场景。

## 文件通过视频传输方案设计

设计一个文件传输方案：发送端将文件编码成视频序列（二维码帧）在远程 VDI 屏幕播放，接收端使用录屏软件（如 OBS、Windows 录屏等）录制该视频文件，然后离线解析录制的视频文件逐帧解码并重组出完整文件。

发送端程序使用 Python 3.8 实现，已知安装了 qrcode。
接收端可以使用任意版本 Python，以及任何第三方库。

### VDI Python 环境

VDI_PY38_Installed.md 这是 VDI 桌面中 Python 环境情况。

## 最终方案

### 发送端
qrtest_pipe.py
qrtest_pipe_mini.py

### 接受端
qrdecode_video.py

### 通过模拟键盘输入传输文件到远程终端
transfer_file.py
transfer_file_v2.py

