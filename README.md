# 01函数库1.0 · UTILS C 函数库

一个 **1110 个函数**的纯 C 函数库，覆盖数组、字符串、数学、数论、排序、查找、位运算、数据结构（链表/栈/队列/环形缓冲区/动态数组/优先级队列/二叉搜索树）、哈希、图算法、CRC 校验、进制转换、时间日期、随机、几何、矩阵、文件、内存、系统工具等领域，并附带**图形化查找工具**与**一键部署脚本**。

## 目录结构（按 库函数 / 程序 / 测试 分类）

```
01函数库1.0/
├── library/      库函数类
│   ├── utils.h / utils.c           核心函数库（手写区）
│   ├── utils_gen.h / utils_gen.c   自动生成的函数（扩充区）
│   ├── func_index.h                函数索引表（查找工具使用）
│   ├── multifunc.h / multifunc.c   多功能执行器（可选库）
│   └── gen_functions.py            函数批量生成器
├── programs/     程序类
│   ├── utils_gui.exe               图形化查找工具（双击即用）
│   ├── utils_gui.c / build_gui.bat 源码与编译脚本
│   └── main.c                      Hello World 示例
├── tests/        测试函数类
│   ├── test_lib.c                  库功能测试
│   ├── verify_install.c            部署验证程序
│   ├── uti-main.c                  utils 全部函数演示
│   └── mul-main.c                  multifunc 演示
├── install_my_lib.bat              一键部署到 MinGW
└── 函数一键调用步骤.txt             详细使用说明
```

## 快速开始

1. **一键部署**：双击 `01函数库1.0\install_my_lib.bat`，自动定位 MinGW、安装头文件、编译打包静态库 `libmylib.a`
2. **调用函数**：部署后任意目录写程序：
   ```c
   #include <utils.h>
   #include <multifunc.h>   // 可选
   ```
   编译链接：`gcc 你的程序.c -lmylib -o 程序`
3. **图形化查找**：双击 `01函数库1.0\programs\utils_gui.exe`，支持搜索、67 个分类筛选、排序、复制、跳转 VS Code

## 最近更新（2026-08-14）

- **修复乱码**：GUI 与脚本中文乱码（UTF-8↔GBK 编码方案统一）
- **utils_gui 升级 v2.1**：支持四文件索引、模糊查找（子序列匹配+匹配度排序）、多关键词搜索、分类带数量、排序、复制（函数名/示例/实现源码）、跳转 VS Code（直接调用 Code.exe）、VS Code Dark+ 风格源码语法高亮（配色可用 theme.ini 自定义）、列表斑马纹
- **修复索引 Bug**：func_index.h 分类解析错误（实际 67 个分类生效）
- **目录重组**：按 library / programs / tests 分类整理
- **修复隐藏编译错误**：multifunc.c 及测试文件中的 emoji 导致 GBK 编译失败，已替换为兼容字符
- 全量验证：1110 个函数 100% 可显示并跳转，全部测试程序编译运行通过

