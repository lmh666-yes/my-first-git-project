# 01函数库1.0 · UTILS C 函数库

一个 **1179 个函数/宏**的纯 C 函数库，覆盖数组、字符串、数学、数论、排序、查找、位运算、数据结构（链表/单循环链表/栈/队列/环形缓冲区/动态数组/优先级队列/二叉搜索树/并查集/双端队列/堆）、哈希、图算法（BFS/DFS/Dijkstra/拓扑排序/Prim 最小生成树）、回调函数、变参函数、复合函数、CRC 校验、进制转换、时间日期、随机、几何、矩阵、文件、内存、系统工具等领域，并附带**图形化查找工具**与**一键部署脚本**。

## 目录结构（按 库函数 / 程序 / 测试 分类）

```
01函数库1.0/
├── library/      库函数类
│   ├── utils.h / utils.c           核心函数库（手写区）
│   ├── utils_gen.h / utils_gen.c   自动生成的函数（扩充区）
│   ├── func_index.h                函数索引表（查找工具使用）
│   ├── multifunc.h / multifunc.c   多功能执行器（可选库）
│   ├── gen_functions.py            函数批量生成器
│   └── rebuild_index.py            重建 func_index.h（含手动扩展区）
├── programs/     程序类
│   ├── utils_gui.exe               图形化查找工具（双击即用）
│   ├── utils_gui.c / build_gui.bat 源码与编译脚本
│   └── main.c                      Hello World 示例
├── tests/        测试函数类
│   ├── test_lib.c                  库功能测试
│   ├── test_extra.c                新增数据结构/算法/宏测试
│   ├── test_list.c                 链表进阶/循环链表测试
│   ├── test_advanced.c             回调/变参/复合函数测试
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
3. **图形化查找**：双击 `01函数库1.0\programs\utils_gui.exe`，支持搜索、74 个分类筛选（数量显示在计数栏）、排序、复制、跳转 VS Code

## 最近更新（2026-08-14）

- **高级函数扩充**：新增 22 个函数，单开**回调函数 / 变参函数 / 复合函数** 三个分类（回调：array_map/array_filter/array_reduce/count_if/list_foreach/bubble_sort_cmp/binary_search_cmp/apply_to_range；变参：sum_variadic/max_variadic/min_variadic/avg_variadic/mul_variadic/str_concat_va；复合：unique_sorted/remove_duplicates_array/median_of_array/array_minmax/histogram/mode_of_array/merge_sorted_into/intersection_sorted），复合函数内部嵌套调用库内已有函数，配套 `tests/test_advanced.c` 33 项全部通过，全量 **1179 项**无重复
- **分类功能优化**：分类下拉框不再标注数量（避免遮挡），选中分类后计数栏显示“显示 X / Y 个函数 ｜ 分类名: N 个”
- **链表进阶扩充**：新增 13 个函数（快慢指针取中间节点/倒数第 k 个、有序链表去重、回文判断、指定位置插入/删除，以及单循环链表全套 7 个操作），配套 `tests/test_list.c` 全部测试通过
- **搜索优化**：修复搜索框过滤（悬挂指针导致不刷新）；模糊匹配仅对 ASCII 函数名生效，中文描述/分类只做精确子串匹配，消除 GBK 字节误匹配（搜 `list` 精确 62 项、`排序` 29 项）
- **全屏布局修复**：窗口最大化/全屏时功能列自动填满列表宽度（不再留白）；窄窗口下列宽按比例收缩不溢出
- **扩充函数库**：新增 33 个函数/宏（并查集、图拓扑排序/Prim 最小生成树/有向边、二分边界 lower/upper_bound、逆序对、滑动窗口最大值、两数之和、字母异位词、最长公共子序列、完全平方数/丑数/素数计数，以及 16 个 C 常用宏），全量经脚本检查**无重复、无错误、注释准确**
- **修复乱码**：GUI 与脚本中文乱码（UTF-8↔GBK 编码方案统一）
- **utils_gui 升级 v2.1**：支持四文件索引、模糊查找（子序列匹配+匹配度排序）、多关键词搜索、分类筛选（数量显示在计数栏）、排序、复制（函数名/示例/实现源码）、跳转 VS Code（直接调用 Code.exe）、Notepad++ 风格源码语法高亮（白底黑字，配色可用 theme.ini 自定义）、详情展示参数/返回值详细说明（位于实现源码下方绿色注释）、左侧列表三态高亮（悬停亮色/选中深色/白灰条纹）
- **准确性修复**：修正全部函数的分类与功能描述（desc 取自已校验的注释）、修复含花括号字符串函数的源码提取、核心算法函数关键步骤已添加注释
- **修复索引 Bug**：func_index.h 分类解析错误（实际 70 个分类生效）
- **目录重组**：按 library / programs / tests 分类整理
- **修复隐藏编译错误**：multifunc.c 及测试文件中的 emoji 导致 GBK 编译失败，已替换为兼容字符
- 全量验证：1179 项 100% 可显示并跳转，全部测试程序编译运行通过

