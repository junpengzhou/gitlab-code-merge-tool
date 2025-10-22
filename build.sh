#/bin/bash
echo "开始资源清理..."
rm -rf code-merge.tar.gz
rm -rf ./build/code-merge.tar.gz
echo "完成资源清理！"
echo "开始打包压缩..."
tar -zcvf code-merge.tar.gz static support templates *.py
echo "打包压缩成功！"
echo "开始目标目录..."
mkdir -p ./build
echo "build目录创建成功..."
echo "开始移动构建产物文件..."
mv code-merge.tar.gz ./build/
echo "构建完成！"