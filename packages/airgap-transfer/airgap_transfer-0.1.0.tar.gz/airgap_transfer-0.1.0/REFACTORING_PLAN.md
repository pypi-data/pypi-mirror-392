# Airgap Transfer - 项目重构方案

> 将现有项目重构为专业的 Python 开源工具库

## 目录

- [项目命名](#项目命名)
- [项目结构](#项目结构)
- [命令行工具设计](#命令行工具设计)
- [Python API 设计](#python-api-设计)
- [安装部署方案](#安装部署方案)
- [配置文件](#配置文件)
- [迁移步骤](#迁移步骤)

---

## 项目命名

### 包名选择

推荐：**`airgap-transfer`**

理由：
- ✅ 在安全领域有明确含义（air-gapped network）
- ✅ 简洁易记
- ✅ 准确描述使用场景
- ✅ 符合 Python 包命名规范（小写+连字符）

备选方案：
- `isolated-transfer` - 强调隔离环境
- `gap-bridge` - 隐喻"桥接隔离"
- `secure-channel-transfer` - 强调安全通道

### PyPI 包名

- **PyPI**: `airgap-transfer`
- **Import**: `airgap_transfer`（Python 模块名使用下划线）

---

## 项目结构

```
airgap-transfer/
├── README.md                   # 主文档（英文）
├── README_CN.md                # 中文文档
├── LICENSE                     # MIT License
├── CHANGELOG.md                # 版本更新日志
├── CONTRIBUTING.md             # 贡献指南
├── pyproject.toml              # 项目配置（PEP 621）
├── setup.py                    # 向后兼容
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI/CD 自动测试
│       └── publish.yml         # 发布到 PyPI
│
├── src/
│   └── airgap_transfer/
│       ├── __init__.py         # 导出公共 API
│       ├── __version__.py      # 版本信息
│       │
│       ├── keyboard/           # 键盘传输模块
│       │   ├── __init__.py
│       │   ├── sender.py       # KeyboardTransfer 类
│       │   └── script_generator.py  # Bash 脚本生成器
│       │
│       ├── qrcode/             # 二维码传输模块
│       │   ├── __init__.py
│       │   ├── encoder.py      # QREncoder 类
│       │   └── decoder.py      # QRDecoder 类
│       │
│       ├── installer/          # 安装器模块 ⭐ 新增
│       │   ├── __init__.py
│       │   ├── packager.py     # 打包发送端代码
│       │   └── templates/      # 发送端代码模板
│       │       ├── qr_sender.py.tpl
│       │       └── bootstrap.sh.tpl
│       │
│       ├── cli/                # 命令行接口
│       │   ├── __init__.py
│       │   ├── main.py         # 主入口 `airgap`
│       │   ├── send.py         # `airgap send`
│       │   ├── qr_encode.py    # `airgap qr-encode`
│       │   ├── qr_decode.py    # `airgap qr-decode`
│       │   └── install.py      # `airgap install` ⭐ 新增
│       │
│       └── utils/              # 工具函数
│           ├── __init__.py
│           ├── checksum.py     # SHA256 校验
│           ├── encoding.py     # Base64 编码
│           └── constants.py    # 常量定义
│
├── tests/                      # 单元测试
│   ├── __init__.py
│   ├── test_keyboard_sender.py
│   ├── test_qr_encoder.py
│   ├── test_qr_decoder.py
│   ├── test_installer.py       # ⭐ 新增
│   ├── test_cli.py
│   └── fixtures/
│       ├── test_files/
│       │   ├── test.txt
│       │   ├── test.pdf
│       │   └── test.bin
│       └── test_videos/
│           └── sample_qr.mp4
│
├── examples/                   # 示例代码
│   ├── 01_keyboard_transfer.py
│   ├── 02_qr_transfer_encode.py
│   ├── 03_qr_transfer_decode.py
│   ├── 04_install_to_airgap.py  # ⭐ 新增
│   └── 05_batch_transfer.py
│
├── docs/                       # 详细文档
│   ├── index.md
│   ├── installation.md
│   ├── quickstart.md
│   ├── keyboard-transfer.md
│   ├── qrcode-transfer.md
│   ├── airgap-installation.md  # ⭐ 新增
│   ├── troubleshooting.md
│   ├── api-reference.md
│   └── architecture.md
│
├── scripts/                    # 开发/构建脚本
│   ├── test_pipeline.sh
│   ├── benchmark.py
│   └── build_standalone.py     # 构建独立发送端包
│
└── dist/                       # 构建输出（不纳入版本控制）
    └── sender-bundle/          # 可传输到隔离环境的包
        ├── airgap_qr_sender.py
        ├── install.sh
        └── README.txt
```

---

## 命令行工具设计

### 主命令：`airgap`

统一的入口点，支持子命令模式。

```bash
airgap --help
airgap --version
```

### 子命令列表

#### 1. `airgap send` - 键盘传输

```bash
# 基本用法
airgap send myfile.pdf

# 指定远程输出路径
airgap send myfile.pdf --output /tmp/output.pdf

# 调整速度参数
airgap send myfile.pdf --char-delay 0.01 --line-delay 0.05

# 不自动执行（手动按回车）
airgap send myfile.pdf --no-auto-execute

# 增加倒计时
airgap send myfile.pdf --countdown 10

# 快速模式（本地虚拟机）
airgap send myfile.pdf --fast

# 慢速模式（高延迟远程桌面）
airgap send myfile.pdf --slow
```

#### 2. `airgap qr-encode` - 生成二维码视频流

```bash
# 输出到管道（配合 ffplay 播放）
airgap qr-encode myfile.pdf | ffplay -framerate 1 -f image2pipe -i -

# 保存为视频文件
airgap qr-encode myfile.pdf | ffmpeg -framerate 1 -f image2pipe -i - output.mp4

# 指定首帧延迟
airgap qr-encode myfile.pdf --first-frame-delay 5

# 调整数据块大小
airgap qr-encode myfile.pdf --chunk-size 800

# 显示预览（不输出视频）
airgap qr-encode myfile.pdf --preview
```

#### 3. `airgap qr-decode` - 从视频解码文件

```bash
# 基本用法
airgap qr-decode recording.mp4 output.pdf

# 指定采样率（加速处理）
airgap qr-decode recording.mp4 output.pdf --sample-rate 2

# 验证与原文件一致性
airgap qr-decode recording.mp4 output.pdf --verify original.pdf

# 允许不完整数据（部分帧丢失）
airgap qr-decode recording.mp4 output.pdf --allow-incomplete

# 详细模式
airgap qr-decode recording.mp4 output.pdf --verbose
```

#### 4. `airgap install` - 安装发送端到隔离环境 ⭐ 核心新功能

```bash
# 生成可传输的发送端包
airgap install --generate

# 指定输出目录
airgap install --generate --output ./sender-bundle

# 生成自包含脚本（单文件，包含所有依赖）
airgap install --generate --standalone

# 查看安装包内容
airgap install --show

# 通过键盘传输安装脚本
airgap install --transfer
```

**工作流程**：

```bash
# === 外部环境 ===
# 1. 生成发送端安装包
$ airgap install --generate
生成的文件：
  ./sender-bundle/
    ├── airgap_qr_sender.py     # 独立的二维码发送端
    ├── install.sh              # 安装脚本
    └── README.txt              # 使用说明

# 2. 通过键盘传输安装到隔离环境
$ airgap install --transfer

提示：切换到远程终端...
（自动通过键盘传输安装脚本）

# === 隔离环境（VDI 内部）===
# 3. 运行安装脚本（已自动输入）
$ bash install.sh

安装完成！已创建：
  ~/airgap_tools/
    └── qr_sender.py

# 4. 在隔离环境中使用
$ python3 ~/airgap_tools/qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -
```

---

## Python API 设计

### 导入方式

```python
# 方式 1：导入主要类
from airgap_transfer import KeyboardTransfer, QREncoder, QRDecoder

# 方式 2：导入模块
from airgap_transfer.keyboard import KeyboardTransfer
from airgap_transfer.qrcode import QREncoder, QRDecoder
from airgap_transfer.installer import SenderPackager

# 方式 3：导入工具函数
from airgap_transfer.utils import calculate_checksum, encode_base64
```

### API 示例

#### 键盘传输

```python
from airgap_transfer import KeyboardTransfer

# 基本使用
transfer = KeyboardTransfer("myfile.pdf")
transfer.send(countdown=5, auto_execute=True)

# 自定义参数
transfer = KeyboardTransfer(
    file_path="myfile.pdf",
    output_path="/tmp/output.pdf",
    char_delay=0.005,
    line_delay=0.03
)
transfer.send(
    countdown=10,
    auto_execute=False
)

# 获取生成的脚本（不传输）
script = transfer.generate_script()
print(script)
```

#### 二维码编码

```python
from airgap_transfer.qrcode import QREncoder
import sys

# 基本使用
encoder = QREncoder("myfile.pdf")
encoder.encode_to_stream(sys.stdout.buffer)

# 自定义参数
encoder = QREncoder(
    file_path="myfile.pdf",
    chunk_size=800,
    first_frame_duration=5
)

# 编码到文件
with open("qr_frames.bin", "wb") as f:
    encoder.encode_to_stream(f)

# 获取统计信息
stats = encoder.get_stats()
print(f"总块数: {stats['total_chunks']}")
print(f"QR 版本: {stats['qr_version']}")
```

#### 二维码解码

```python
from airgap_transfer.qrcode import QRDecoder

# 基本使用
decoder = QRDecoder("recording.mp4")
success = decoder.decode_to_file("output.pdf")

# 自定义参数
decoder = QRDecoder(
    video_path="recording.mp4",
    sample_rate=2,
    verbose=True
)
success = decoder.decode_to_file(
    output_path="output.pdf",
    allow_incomplete=False
)

# 验证与原文件
decoder.verify_with_original("output.pdf", "original.pdf")

# 获取解码统计
stats = decoder.get_stats()
print(f"收集块数: {stats['collected_chunks']}/{stats['total_chunks']}")
```

#### 发送端打包器 ⭐ 新增

```python
from airgap_transfer.installer import SenderPackager

# 生成发送端包
packager = SenderPackager(output_dir="./sender-bundle")
packager.generate()

# 生成独立脚本（单文件）
packager.generate_standalone(output_file="airgap_sender_standalone.py")

# 通过键盘传输安装
packager.transfer_to_remote(countdown=5)
```

---

## 安装部署方案

### 1. 常规安装（外部环境）

```bash
# 从 PyPI 安装
pip install airgap-transfer

# 安装可选依赖
pip install airgap-transfer[qrcode]  # 二维码功能
pip install airgap-transfer[dev]     # 开发工具

# 从源码安装
git clone https://github.com/yourusername/airgap-transfer.git
cd airgap-transfer
pip install -e .
```

### 2. 隔离环境安装（VDI 内部）⭐ 核心场景

#### 方案 A：通过键盘传输安装脚本（推荐）

```bash
# 外部环境
$ airgap install --transfer

# 自动在远程终端执行：
# 1. 下载独立的发送端脚本
# 2. 保存到 ~/airgap_tools/qr_sender.py
# 3. 验证安装
```

#### 方案 B：单文件独立脚本

```bash
# 外部环境：生成单文件脚本
$ airgap install --generate --standalone --output qr_sender_standalone.py

# 通过键盘传输单个文件
$ airgap send qr_sender_standalone.py --output ~/qr_sender.py

# 隔离环境：直接使用
$ python3 ~/qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -
```

### 3. 发送端功能清单

隔离环境中的发送端需要支持：

✅ 必需功能：
- 文件编码为二维码序列
- 输出到 stdout（管道到 ffplay）
- Base64 编码
- 分块逻辑
- QR 码生成（使用 VDI 已有的 qrcode 库）

❌ 不需要的功能：
- 键盘传输（仅用于接收文件）
- 视频解码（仅用于外部环境）
- CLI 完整功能

### 4. 发送端模板文件

**`installer/templates/qr_sender.py.tpl`**

```python
#!/usr/bin/env python3
# Airgap Transfer - QR Code Sender (Standalone Version)
# Version: {version}
# Generated: {timestamp}
#
# Minimal QR code sender for air-gapped environments
# Dependencies: qrcode (Python 3.8+)

import qrcode
import base64
import math
import sys
from io import BytesIO

# ... 核心功能代码（精简版） ...

if __name__ == "__main__":
    # CLI 入口
    pass
```

**`installer/templates/install.sh.tpl`**

```bash
#!/bin/bash
# Airgap Transfer - Installation Script
# This script installs the QR sender tool in an air-gapped environment

set -e

INSTALL_DIR="$HOME/airgap_tools"

echo "Installing Airgap Transfer QR Sender..."

# 创建安装目录
mkdir -p "$INSTALL_DIR"

# 复制文件
cp qr_sender.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/qr_sender.py"

echo "Installation complete!"
echo ""
echo "Usage:"
echo "  python3 $INSTALL_DIR/qr_sender.py myfile.pdf 5 | ffplay -framerate 1 -f image2pipe -i -"
```

---

## 配置文件

### `pyproject.toml`

```toml
[project]
name = "airgap-transfer"
version = "0.1.0"
description = "Bi-directional file transfer tools for air-gapped and isolated environments"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = [
    "airgap",
    "air-gapped",
    "isolated",
    "vdi",
    "bastion",
    "file-transfer",
    "qrcode",
    "keyboard-input",
    "security"
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "Intended Audience :: Information Technology",
    "Topic :: System :: Networking",
    "Topic :: System :: Systems Administration",
    "Topic :: Security",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Operating System :: OS Independent",
]

dependencies = [
    "pynput>=1.7.0",
]

[project.optional-dependencies]
qrcode = [
    "qrcode[pil]>=7.0",
    "opencv-python>=4.5.0",
    "pyzbar>=0.1.9",
]
all = [
    "airgap-transfer[qrcode]",
]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/airgap-transfer"
Documentation = "https://airgap-transfer.readthedocs.io"
Repository = "https://github.com/yourusername/airgap-transfer.git"
Issues = "https://github.com/yourusername/airgap-transfer/issues"
Changelog = "https://github.com/yourusername/airgap-transfer/blob/main/CHANGELOG.md"

[project.scripts]
airgap = "airgap_transfer.cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatchling.build.targets.wheel]
packages = ["src/airgap_transfer"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=airgap_transfer --cov-report=html --cov-report=term"

[tool.black]
line-length = 100
target-version = ['py38']

[tool.ruff]
line-length = 100
target-version = "py38"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
sender-bundle/
*.mp4
*.avi
test_output/
```

---

## 迁移步骤

### Phase 1: 项目结构重组（第 1 周）

- [ ] 创建新的目录结构
- [ ] 移动现有文件到新位置
  - `transfer_file_v2.py` → `src/airgap_transfer/keyboard/sender.py`
  - `qrtest_pipe.py` → `src/airgap_transfer/qrcode/encoder.py`
  - `qrdecode_video.py` → `src/airgap_transfer/qrcode/decoder.py`
- [ ] 创建 `__init__.py` 文件并导出 API
- [ ] 重命名类和函数（符合 PEP 8）
- [ ] 拆分工具函数到 `utils/` 模块

### Phase 2: 重构代码（第 2 周）

- [ ] 重构 `KeyboardTransfer` 类
  - 拆分脚本生成逻辑到 `script_generator.py`
  - 添加类型注解
  - 改进错误处理
- [ ] 重构 `QREncoder` 类
  - 简化接口
  - 添加统计信息 API
- [ ] 重构 `QRDecoder` 类
  - 优化视频处理性能
  - 添加进度回调
- [ ] 创建 `SenderPackager` 类 ⭐ 新增
  - 生成独立发送端脚本
  - 打包安装器

### Phase 3: CLI 开发（第 3 周）

- [ ] 创建 `cli/main.py` 主入口
- [ ] 实现 `airgap send` 命令
- [ ] 实现 `airgap qr-encode` 命令
- [ ] 实现 `airgap qr-decode` 命令
- [ ] 实现 `airgap install` 命令 ⭐ 新增
- [ ] 添加参数解析和帮助信息
- [ ] 添加彩色输出和进度条

### Phase 4: 测试（第 4 周）

- [ ] 编写单元测试
  - `test_keyboard_sender.py`
  - `test_qr_encoder.py`
  - `test_qr_decoder.py`
  - `test_installer.py` ⭐ 新增
  - `test_cli.py`
- [ ] 准备测试固件（test files, test videos）
- [ ] 配置 pytest 和覆盖率
- [ ] 达到 >80% 代码覆盖率

### Phase 5: 文档（第 5 周）

- [ ] 编写 README.md（英文）
- [ ] 编写 README_CN.md（中文）
- [ ] 创建详细文档（docs/）
  - installation.md
  - quickstart.md
  - keyboard-transfer.md
  - qrcode-transfer.md
  - airgap-installation.md ⭐ 新增
  - troubleshooting.md
  - api-reference.md
- [ ] 编写示例代码（examples/）
- [ ] 创建 CONTRIBUTING.md
- [ ] 创建 CHANGELOG.md

### Phase 6: 打包发布（第 6 周）

- [ ] 完善 `pyproject.toml`
- [ ] 创建 LICENSE 文件（MIT）
- [ ] 配置 GitHub Actions CI/CD
  - 自动测试
  - 自动发布到 PyPI
- [ ] 本地构建测试
  ```bash
  python -m build
  twine check dist/*
  ```
- [ ] 发布到 TestPyPI（测试）
  ```bash
  twine upload --repository testpypi dist/*
  ```
- [ ] 发布到 PyPI（正式）
  ```bash
  twine upload dist/*
  ```

### Phase 7: 社区建设（持续）

- [ ] 创建 GitHub repository
- [ ] 编写详细的 README（带 badges）
- [ ] 添加 GitHub Issues 模板
- [ ] 添加 GitHub PR 模板
- [ ] 设置 ReadTheDocs 文档托管
- [ ] 推广到社区
  - Reddit (r/Python, r/netsec)
  - Hacker News
  - Python Weekly

---

## 关键改进点总结

### 1. ⭐ 发送端安装功能（核心创新）

**问题**：如何将发送端工具安装到无网络的隔离环境？

**解决方案**：
- `airgap install --generate` 生成独立的发送端脚本
- `airgap install --transfer` 通过键盘传输自动安装
- 发送端脚本无外部依赖（仅需 Python 3.8 + qrcode）

**价值**：
- 闭环解决方案：工具可以"自举"到隔离环境
- 降低使用门槛：一键安装，无需手动操作
- 实用性强：解决真实痛点

### 2. 统一的 CLI 设计

- 单一入口点 `airgap`
- 子命令模式（类似 git, docker）
- 一致的参数命名
- 友好的帮助信息

### 3. 清晰的 Python API

- 面向对象设计
- 类型注解完整
- 文档字符串规范
- 易于集成到其他项目

### 4. 专业的项目结构

- 符合 PEP 518（pyproject.toml）
- src-layout 布局
- 模块化设计
- 完整的测试覆盖

### 5. 完善的文档

- 多语言支持（英文 + 中文）
- 多层次文档（README, docs, examples）
- API 参考文档
- 故障排查指南

---

## 技术债务清理

在重构过程中需要解决的问题：

### 代码质量
- [ ] 添加类型注解（Type Hints）
- [ ] 统一代码风格（Black + Ruff）
- [ ] 改进错误处理（自定义异常类）
- [ ] 添加日志记录（logging 模块）
- [ ] 优化性能瓶颈

### 功能完善
- [ ] 添加进度条（tqdm 或自定义）
- [ ] 支持断点续传（键盘传输）
- [ ] 支持批量文件传输
- [ ] 添加配置文件支持（~/.airgap/config.yaml）
- [ ] 支持压缩传输（自动 gzip）

### 安全性
- [ ] 添加文件加密选项（GPG 集成）
- [ ] 校验和算法可配置（SHA256/SHA512）
- [ ] 文件大小限制保护
- [ ] 输入验证和清理

### 兼容性
- [ ] 测试多平台（Linux, macOS, Windows）
- [ ] 测试多 Python 版本（3.8-3.13）
- [ ] 测试多终端（bash, zsh, fish）
- [ ] 优雅降级（缺少依赖时）

---

## 发布清单

### 预发布检查

- [ ] 所有测试通过
- [ ] 代码覆盖率 > 80%
- [ ] 文档完整且准确
- [ ] CHANGELOG.md 更新
- [ ] 版本号更新（遵循语义化版本）
- [ ] LICENSE 文件存在
- [ ] README 徽章正常显示

### 发布流程

1. 更新版本号（`__version__.py`, `pyproject.toml`）
2. 更新 CHANGELOG.md
3. 提交并打 tag
   ```bash
   git commit -am "Release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```
4. 构建分发包
   ```bash
   python -m build
   ```
5. 上传到 PyPI
   ```bash
   twine upload dist/*
   ```
6. 创建 GitHub Release
7. 发布公告

### 版本规划

- **v0.1.0** - 初始版本
  - 基本键盘传输功能
  - 基本二维码传输功能
  - 基础 CLI

- **v0.2.0** - 安装器版本 ⭐
  - 添加 `airgap install` 命令
  - 发送端打包功能
  - 改进文档

- **v0.3.0** - 增强版本
  - 批量传输支持
  - 配置文件支持
  - 性能优化

- **v1.0.0** - 稳定版本
  - 完整测试覆盖
  - 生产环境验证
  - 完善文档

---

## 贡献指南预览

我们欢迎各种形式的贡献：

- 🐛 报告 bug
- 💡 提出新功能建议
- 📖 改进文档
- 🔧 提交代码修复
- 🌍 翻译文档

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 许可证

推荐使用 **MIT License**，理由：
- ✅ 宽松许可，易于采用
- ✅ 商业友好
- ✅ 社区认可度高
- ✅ 与大多数 Python 项目一致

---

## 总结

这个重构方案将项目从"个人脚本集合"提升为"专业开源工具库"，关键改进包括：

1. **清晰的项目结构**：模块化、可维护
2. **统一的 CLI 设计**：易用、专业
3. **完善的 Python API**：可集成、可扩展
4. **⭐ 发送端安装功能**：解决核心痛点，形成闭环
5. **完整的文档**：降低使用门槛
6. **规范的发布流程**：可持续发展

重构后的项目将更容易被社区采用和贡献，有望成为气隙环境文件传输的标准工具。
