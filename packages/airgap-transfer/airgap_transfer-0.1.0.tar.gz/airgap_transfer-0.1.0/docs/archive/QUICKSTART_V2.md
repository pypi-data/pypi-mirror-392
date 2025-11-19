# 文件传输 V2 - 超简单快速开始

> **零操作！** 只需保持远程终端聚焦，脚本自动执行

## 3 步完成传输

### 1. 安装依赖

```bash
pip install pynput
```

### 2. 运行传输程序

```bash
python transfer_file_v2.py yourfile.pdf
```

### 3. 等待自动完成

在远程终端：
- ✓ 确保终端显示干净的命令提示符 (如 `$` 或 `➜`)
- ✓ 保持终端聚焦 (激活状态)
- ✓ **什么都不要做**,等待自动执行

就这样！传输会自动完成并显示结果。

## 完整示例

```
┌─────────────────────────────────────┐
│          本地端 (你的电脑)          │
└─────────────────────────────────────┘

$ python transfer_file_v2.py test.pdf

输出:
======================================================================
文件传输程序 V2 - 自动执行版
======================================================================

源文件: test.pdf
文件大小: 1,234 字节

请在 5 秒内切换到远程终端窗口

======================================================================
重要提示!
======================================================================
在远程终端:

  1. 确保终端处于干净的命令提示符状态 (例如: $ 或 ➜)
  2. 不要输入任何命令,只需保持终端聚焦
  3. 等待本程序自动输入并执行

你什么都不需要做,只要等待即可!
======================================================================

倒计时: 5 秒...


┌─────────────────────────────────────┐
│      远程端 (远程终端/远程桌面)     │
└─────────────────────────────────────┘

$                           ← 保持这个状态
(等待...)

自动输入命令中...
bash << 'END_OF_SCRIPT'
OUTPUT_FILE="test.pdf"
...
END_OF_SCRIPT               ← 自动输入完成

自动执行中...              ← 自动按回车

========================================
开始解码文件: test.pdf
========================================

✓ 文件传输成功! 校验和匹配
文件已保存到: test.pdf
-rw-r--r-- 1 user user 1.2K test.pdf
========================================

$                           ← 自动完成,回到提示符
```

## 对比传统方法

### ❌ 传统方法 (V1)

```bash
# 远程端需要 4 步操作
$ cat > receive.sh        # 1. 输入命令
(等待传输...)
(按 Ctrl+D)               # 2. 保存文件
$ bash receive.sh         # 3. 执行脚本
$ rm receive.sh           # 4. 清理文件
```

### ✅ V2 方法

```bash
# 远程端需要 0 步操作
$                         # 只需保持终端聚焦
(自动完成!)
$
```

## 常用参数

```bash
# 基本用法
python transfer_file_v2.py myfile.pdf

# 指定远程输出路径
python transfer_file_v2.py myfile.pdf -o /tmp/output.pdf

# 慢速连接(字符丢失时)
python transfer_file_v2.py myfile.pdf --char-delay 0.01 --line-delay 0.05

# 快速连接(本地虚拟机)
python transfer_file_v2.py myfile.pdf --char-delay 0.001 --line-delay 0.01

# 不自动执行(需手动按回车)
python transfer_file_v2.py myfile.pdf --no-auto-execute

# 增加倒计时
python transfer_file_v2.py myfile.pdf --countdown 10
```

## 常见问题

### Q: 我需要在远程端输入什么命令吗？

A: **不需要！** 只要保持终端聚焦即可。

### Q: 如果我不小心输入了命令怎么办？

A: 没关系，程序会继续输入。但建议在倒计时结束前不要操作。

### Q: 会保留脚本文件吗？

A: 不会。V2 直接在终端执行，不创建文件，更干净。

### Q: 如果我想检查脚本内容怎么办？

A: 使用预览工具：
```bash
python demo_v2.py myfile.pdf
cat preview_v2_command.sh
```

### Q: 自动执行失败了怎么办？

A: 使用 `--no-auto-execute` 参数，然后手动按回车：
```bash
python transfer_file_v2.py myfile.pdf --no-auto-execute
```

### Q: 和 V1 有什么区别？

A: 查看详细对比：`V1_VS_V2.md`

简单来说：
- **V1**: 需要手动 `cat >`, `Ctrl+D`, `bash` 执行
- **V2**: 全自动，零操作

## 故障排除

| 问题       | 解决方案                                        |
| ---------- | ----------------------------------------------- |
| 字符丢失   | 增加延迟：`--char-delay 0.01 --line-delay 0.05` |
| 首字符丢失 | 增加倒计时：`--countdown 10`                    |
| 执行失败   | 使用 `--no-auto-execute`,手动按回车             |
| 终端不干净 | 确保提示符是 `$`, `➜` 等，不在其他命令中        |

## 文件大小建议

| 大小          | 时间       | 推荐  |
| ------------- | ---------- | ----- |
| < 10 KB       | < 1 分钟   | ⭐⭐⭐⭐⭐ |
| 10-100 KB     | 1-10 分钟  | ⭐⭐⭐⭐  |
| 100 KB - 1 MB | 10-60 分钟 | ⭐⭐⭐   |
| > 1 MB        | > 60 分钟  | ⭐     |

## 高级用法

### 预览命令 (不传输)

```bash
python demo_v2.py myfile.pdf
# 查看生成的命令
cat preview_v2_command.sh
# 本地测试
bash preview_v2_command.sh
```

### 批量传输

```bash
for file in *.txt; do
    python transfer_file_v2.py "$file"
    sleep 5  # 给你时间切换窗口
done
```

### 压缩后传输

```bash
# 压缩
gzip largefile.bin

# 传输
python transfer_file_v2.py largefile.bin.gz

# 远程端会自动解码得到 largefile.bin.gz
# 然后手动解压: gunzip largefile.bin.gz
```

## 完整文档

- `V1_VS_V2.md` - V1 和 V2 详细对比
- `TRANSFER_FILE_README.md` - V1 完整文档
- `FILE_TRANSFER_SUMMARY.md` - 项目总览

## 下一步

试试传输你的第一个文件：

```bash
# 创建测试文件
echo "Hello from local!" > test.txt

# 传输
python transfer_file_v2.py test.txt

# 在远程端等待自动完成
```

就这么简单！🎉
