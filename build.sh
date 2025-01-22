#!/bin/bash

# 定义要操作的文件和目录（
FILES_AND_DIRS=("app.exe" "build" "dist" "FSDiary.spec" "app.dist" "app.build" "app.onefile-build")

# 定义清理方法
clean() {
    echo "开始清理FSDiary......"
    # 遍历所有文件和目录
    for TARGET in "${FILES_AND_DIRS[@]}"; do
        echo "正在删除: $TARGET"
        if [ -e "$TARGET" ]; then
            rm -rf "$TARGET"  # 使用 -rf 删除文件或目录
            echo "已删除: $TARGET"
        else
            echo "文件或目录不存在: $TARGET"
        fi
    done
}


build() {
    # 执行打包命令
    echo "正在打包FSDiary......"
    pyinstaller --name "FSDiary" --onefile  --window   --add-data "resources:resources"  --add-data "app.ini:." --icon=resources/images/app.ico ./app.py
}

# 主程序逻辑，根据传入的参数调用不同的方法
if [ $# -eq 0 ]; then
    echo "请提供一个操作参数，如 'clean' 或 'build'"
    exit 1
fi

case "$1" in
    clean)
        clean
        ;;
    build)
        build
        ;;
    *)
        echo "无效的操作: $1"
        echo "可用操作: clean，build"
        exit 1
        ;;
esac
