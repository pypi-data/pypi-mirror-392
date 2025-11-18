#!/bin/bash

set -e

echo "========================================"
echo "  发布 glog 到 PyPI"
echo "========================================"
echo ""

# 检查必要工具
echo "检查必要工具..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

if ! python3 -c "import build" 2>/dev/null; then
    echo "⚠️  未安装 build，正在安装..."
    pip install build
fi

if ! python3 -c "import twine" 2>/dev/null; then
    echo "⚠️  未安装 twine，正在安装..."
    pip install twine
fi

echo "✅ 工具检查完成"
echo ""

# 清理旧文件
echo "1. 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info glog.egg-info
echo "✅ 清理完成"
echo ""

# 运行测试
echo "2. 运行测试..."
python3 glog/tests/test_logger.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 测试通过"
else
    echo "❌ 测试失败，请修复后再发布"
    exit 1
fi
echo ""

# 构建
echo "3. 构建分发包..."
python3 -m build
echo "✅ 构建完成"
echo ""

# 检查
echo "4. 检查包..."
twine check dist/*
if [ $? -eq 0 ]; then
    echo "✅ 包检查通过"
else
    echo "❌ 包检查失败"
    exit 1
fi
echo ""

# 显示构建的文件
echo "构建的文件:"
ls -lh dist/
echo ""

# 询问上传选项
echo "请选择上传目标:"
echo "  1) TestPyPI (测试环境)"
echo "  2) PyPI (正式环境)"
echo "  3) 两者都上传 (先测试后正式)"
echo "  0) 取消"
read -p "请输入选项 (0-3): " choice

case $choice in
    1)
        echo ""
        echo "5. 上传到 TestPyPI..."
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ 上传到 TestPyPI 成功！"
        echo ""
        echo "测试安装命令:"
        echo "  pip install --index-url https://test.pypi.org/simple/ glog-python"
        ;;
    2)
        echo ""
        read -p "确认上传到正式 PyPI? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "5. 上传到 PyPI..."
            twine upload dist/*
            echo ""
            echo "✅ 上传到 PyPI 成功！"
            echo ""
            echo "安装命令:"
            echo "  pip install glog-python"
        else
            echo "❌ 取消上传"
        fi
        ;;
    3)
        echo ""
        echo "5. 上传到 TestPyPI..."
        twine upload --repository testpypi dist/*
        echo "✅ 上传到 TestPyPI 成功！"
        echo ""
        read -p "测试通过后，是否继续上传到正式 PyPI? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "6. 上传到 PyPI..."
            twine upload dist/*
            echo ""
            echo "✅ 上传到 PyPI 成功！"
            echo ""
            echo "安装命令:"
            echo "  pip install glog-python"
        else
            echo "❌ 取消上传到正式 PyPI"
        fi
        ;;
    0)
        echo "❌ 取消发布"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "  发布完成！"
echo "========================================"
