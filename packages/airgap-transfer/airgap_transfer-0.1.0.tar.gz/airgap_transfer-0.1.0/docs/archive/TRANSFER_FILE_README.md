# 文件传输工具 - 通过键盘输入

通过模拟键盘输入，将任意文件传输到远程终端 (支持远程桌面、SSH 终端等场景)。

## 工作原理

1. **本地端**:
   - 读取源文件并计算 SHA256 校验和
   - 将文件内容进行 Base64 编码
   - 生成一个自解压的 Bash 脚本
   - 通过模拟键盘输入将脚本传输到远程终端

2. **远程端**:
   - 接收脚本内容 (通过 `cat > receive.sh` 或直接粘贴到编辑器)
   - 执行脚本：`bash receive.sh`
   - 脚本自动解码 Base64 数据并验证校验和
   - 输出原始文件

## 安装依赖

```bash
pip install pynput
# 或
uv add pynput
```

## 使用方法

### 基本用法

```bash
# 传输文件
python transfer_file.py myfile.pdf
```

### 高级用法

```bash
# 指定远程端输出文件名
python transfer_file.py myfile.pdf -o /tmp/received.pdf

# 调整输入速度(适用于快速连接)
python transfer_file.py myfile.pdf --char-delay 0.001 --line-delay 0.01

# 调整输入速度(适用于慢速/不稳定连接)
python transfer_file.py myfile.pdf --char-delay 0.01 --line-delay 0.05

# 自定义倒计时
python transfer_file.py myfile.pdf --countdown 10
```

## 完整操作流程

### 方法一：使用 cat 命令 (推荐)

1. **本地端**: 运行传输程序
   ```bash
   python transfer_file.py myfile.pdf
   ```

2. **切换到远程终端**, 在倒计时结束前输入：
   ```bash
   cat > receive.sh
   ```

3. **等待脚本输入完成** (本地程序会自动输入所有内容)

4. **保存文件**: 按 `Ctrl+D`

5. **执行脚本**:
   ```bash
   bash receive.sh
   ```

6. **验证**: 脚本会自动验证校验和并显示结果

### 方法二：使用文本编辑器

1. **本地端**: 运行传输程序
   ```bash
   python transfer_file.py myfile.pdf
   ```

2. **远程端**: 打开文本编辑器
   ```bash
   vim receive.sh
   # 或
   nano receive.sh
   ```

3. **进入插入模式** (vim: 按 `i`, nano: 直接输入)

4. **等待脚本输入完成**

5. **保存退出**:
   - vim: 按 `Esc`, 输入 `:wq`
   - nano: 按 `Ctrl+X`, 按 `Y`, 按 `Enter`

6. **执行脚本**:
   ```bash
   bash receive.sh
   ```

## 性能参数调优

根据你的网络和远程环境，可能需要调整延迟参数：

| 场景 | char-delay | line-delay | 说明 |
|------|-----------|-----------|------|
| 本地虚拟机 | 0.001 | 0.01 | 非常快速 |
| 快速局域网 | 0.003 | 0.02 | 快速 |
| 默认配置 | 0.005 | 0.03 | 平衡 |
| 远程桌面 | 0.005 | 0.03 | 默认适用 |
| 慢速 VPN | 0.01 | 0.05 | 较慢但稳定 |
| 高延迟连接 | 0.02 | 0.1 | 很慢但可靠 |

## 适用场景

- 远程桌面 (RDP, VNC)
- 跳板机/堡垒机限制 scp/sftp
- 只允许终端访问的环境
- 需要绕过文件传输限制的场景
- 嵌入式设备或特殊终端

## 限制和注意事项

1. **文件大小**: 适用于中小型文件 (< 10MB),大文件传输时间较长
2. **Base64 膨胀**: 编码后文件大小约为原文件的 133%
3. **输入速度**: 受限于键盘输入速度，通常 100-500 字符/秒
4. **终端缓冲**: 某些终端可能有输入缓冲限制
5. **安全性**: 明文传输，建议仅用于可信环境

## 文件大小估算

传输时间估算 (假设 200 字符/秒):

| 原始大小 | Base64 大小 | 脚本总大小 | 预计时间 |
|---------|-----------|-----------|---------|
| 10 KB | 13 KB | ~14 KB | ~70 秒 |
| 100 KB | 133 KB | ~134 KB | ~670 秒 (11 分钟) |
| 1 MB | 1.33 MB | ~1.34 MB | ~6700 秒 (112 分钟) |

## 故障排除

### 问题：字符丢失或乱序

**解决方案**: 增加延迟参数
```bash
python transfer_file.py myfile.pdf --char-delay 0.01 --line-delay 0.05
```

### 问题：校验和不匹配

**可能原因**:
- 传输过程中丢失字符
- 终端编码问题
- 脚本未完整保存

**解决方案**:
1. 增加延迟重试
2. 检查远程终端编码设置 (应为 UTF-8)
3. 确保使用 `cat > file.sh` 并正确按 Ctrl+D 保存

### 问题：远程终端无法执行脚本

**解决方案**:
```bash
# 添加执行权限
chmod +x receive.sh

# 或直接用 bash 执行
bash receive.sh
```

## 安全建议

1. 仅在可信网络环境使用
2. 传输敏感文件前可先加密
3. 传输完成后删除脚本文件：
   ```bash
   rm receive.sh
   ```
4. 对于重要文件，建议二次验证校验和

## 示例：加密传输

```bash
# 本地端: 先加密文件
openssl enc -aes-256-cbc -salt -in secret.pdf -out secret.pdf.enc

# 传输加密文件
python transfer_file.py secret.pdf.enc -o /tmp/secret.pdf.enc

# 远程端: 解密
openssl enc -aes-256-cbc -d -in /tmp/secret.pdf.enc -out secret.pdf
```

## 技术细节

- **编码**: Base64 (RFC 4648)
- **校验**: SHA256
- **键盘库**: pynput
- **脚本格式**: POSIX shell (兼容 bash/sh)
- **换行符处理**: 自动兼容 Windows (CRLF), Unix (LF), Mac (CR)

## License

MIT
