#!/bin/bash
# test_video_pipeline.sh - 测试完整的 QR 编码->录屏->解码流程

set -e

echo "=========================================="
echo "QR 编码->录屏->解码 完整流程测试"
echo "=========================================="
echo ""

# 配置
INPUT_FILE="${1:-QR_FILES.md}"
CHUNK_SIZE="${2:-800}"
FIRST_FRAME_DURATION="${3:-40}"
SAMPLE_RATE="${4:-1}"

echo "配置："
echo "  输入文件: $INPUT_FILE"
echo "  块大小: $CHUNK_SIZE 字节"
echo "  第一帧持续时间: $FIRST_FRAME_DURATION 秒"
echo "  解码采样率: 每 $SAMPLE_RATE 帧"
echo ""

# 检查输入文件
if [ ! -f "$INPUT_FILE" ]; then
    echo "错误：输入文件不存在: $INPUT_FILE"
    exit 1
fi

# 步骤 1: 生成 QR 码并播放
echo "步骤 1: 生成 QR 码序列（管道模式）"
echo "提示：你应该手动录屏，然后按 Ctrl+C 停止"
echo "命令："
echo "  uv run python qrtest_pipe.py $INPUT_FILE $FIRST_FRAME_DURATION | ffplay -framerate 2 -f image2pipe -i -"
echo ""
echo "请按回车键继续（启动播放器）或 Ctrl+C 取消..."
read

uv run python qrtest_pipe.py "$INPUT_FILE" "$FIRST_FRAME_DURATION" | ffplay -framerate 2 -f image2pipe -i -

echo ""
echo "播放已停止。"
echo ""

# 步骤 2: 解码录屏视频
echo "步骤 2: 解码录屏视频"
echo "请输入录屏视频文件路径（默认: test_data/screen_1.mp4）："
read VIDEO_FILE
VIDEO_FILE="${VIDEO_FILE:-test_data/screen_1.mp4}"

if [ ! -f "$VIDEO_FILE" ]; then
    echo "错误：视频文件不存在: $VIDEO_FILE"
    exit 1
fi

OUTPUT_FILE="output_decoded_$(basename $INPUT_FILE)"
echo "输出文件: $OUTPUT_FILE"
echo ""

uv run python qrdecode_video.py "$VIDEO_FILE" "$OUTPUT_FILE" "$SAMPLE_RATE" "$INPUT_FILE"

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
