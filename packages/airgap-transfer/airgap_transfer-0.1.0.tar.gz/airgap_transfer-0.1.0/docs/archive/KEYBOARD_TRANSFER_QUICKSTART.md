# 键盘输入文件传输 - 快速开始

> 通过模拟键盘输入将任意文件传输到远程终端

## 5 分钟快速上手

### 1. 安装依赖

```bash
pip install pynput
# 或
uv add pynput
```

### 2. 传输文件

```bash
python transfer_file.py yourfile.pdf
```

### 3. 远程端接收 (重要!)

⚠️ **关键步骤**: 在程序倒计时期间切换到远程终端并执行：

```bash
cat > receive.sh
```

执行后，终端会等待输入 (光标停在下一行)。**不要手动输入任何内容**,等待本地程序自动输入！

### 4. 保存并执行

等待传输完成后：

1. 按 `Ctrl+D` (不是 Ctrl+C!) 保存脚本
2. 执行脚本：
   ```bash
   bash receive.sh
   ```

完成！文件会自动解码并验证校验和。

### 常见错误提醒

❌ **不要**直接在终端等待输入 - 必须先执行 `cat > receive.sh`
❌ **不要**按 `Ctrl+C` - 应该按 `Ctrl+D` 保存
❌ **不要**在传输未完成时就按 `Ctrl+D`

✓ 正确流程请参考 `QUICK_REFERENCE.md`

## 交互式模式 (推荐新手)

```bash
python interactive_transfer.py
```

按提示操作，程序会：
- 显示文件信息和预估时间
- 让你选择传输速度
- 确认配置后开始传输

## 工具列表

| 工具 | 用途 |
|-----|------|
| `transfer_file.py` | 命令行传输工具 (完整参数) |
| `interactive_transfer.py` | 交互式界面 (推荐) |
| `demo_generated_script.py` | 预览生成的脚本 |
| `input_poem.py` | 原始示例程序 |

## 常用参数

```bash
# 指定远程输出路径
python transfer_file.py file.pdf -o /tmp/file.pdf

# 调整速度(慢速连接)
python transfer_file.py file.pdf --char-delay 0.01 --line-delay 0.05

# 调整速度(快速连接)
python transfer_file.py file.pdf --char-delay 0.001 --line-delay 0.01

# 增加倒计时
python transfer_file.py file.pdf --countdown 10
```

## 完整文档

- **TRANSFER_FILE_README.md** - 完整使用文档
- **example_usage.md** - 7 个实际场景示例
- **FILE_TRANSFER_SUMMARY.md** - 项目总览

## 适用场景

- ✓ 远程桌面 (RDP, VNC)
- ✓ 堡垒机/跳板机限制 scp
- ✓ 只允许终端访问的环境
- ✓ 需要绕过文件传输限制

## 文件大小建议

| 大小 | 传输时间 | 建议 |
|-----|---------|------|
| < 100 KB | < 10 分钟 | 推荐 |
| 100 KB - 1 MB | 10-60 分钟 | 可行 |
| > 1 MB | > 60 分钟 | 不推荐 |

## 故障排除

**字符丢失**: 增加延迟参数
```bash
python transfer_file.py file.pdf --char-delay 0.01 --line-delay 0.05
```

**校验和不匹配**: 重新传输，或检查终端编码 (需 UTF-8)

## 安全提示

1. 传输完成后删除脚本：`rm receive.sh`
2. 敏感文件建议先加密
3. 仅在可信网络环境使用

---

需要更多帮助？查看完整文档或运行：
```bash
python transfer_file.py --help
```
