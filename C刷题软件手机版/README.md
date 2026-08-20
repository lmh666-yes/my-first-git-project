# 刷题软件 · 手机版

> 基于桌面版「C刷题软件」制作的**手机端应用**。当前内置题库：**嵌入式软件开发工程师（中级）** 单选 80 题 + 判断 50 题，共 130 题。
> 本版为固定题库（不做题库切换），单文件、离线可用。

## 两种使用方式

### 方式一：手机浏览器直接使用（免安装）

把 **`www/index.html`** 这个单文件发到手机（微信/网盘/数据线拷贝均可），用手机浏览器打开即可刷题。
无需安装、无需联网，进度与笔记自动保存在手机本地（localStorage）。

### 方式二：打包成 APK 安装（推荐）

用 **Android Studio** 打开 `android` 文件夹，一键构建 APK：

1. 电脑安装 [Android Studio](https://developer.android.com/studio)（免费）
2. Android Studio 打开项目：`File → Open` → 选择 **`android`** 文件夹
3. 首次打开等待 **Gradle Sync** 完成（自动下载依赖，需联网，约几分钟）
4. 菜单 `Build → Build Bundle(s) / APK(s) → Build APK(s)`
5. 构建完成在 `android/app/build/outputs/apk/debug/`（或 release/）得到 **`app-debug.apk`**
6. 把 APK 发到手机安装即可（安装时允许“未知来源”）

> 提示：如果 Gradle Sync 报错，先确认电脑已安装 Android Studio 且已下载 SDK；
> 若提示缺 `local.properties`（SDK 路径），Android Studio 会自动生成。

## 功能

- **四种模式**：顺序 / 随机 / 错题 / 模拟考试（20 分钟 / 20 题 / 每题 5 分，可暂停/退出、交卷后错题号回顾）
- **单选**：点选项整行变蓝高亮 → **点「确认答案」** 判分 + 解析
- **判断**：先点 ✔正确 / ✘错误 高亮选中 → **点「确认答案」** 判分（不直接锁定）
- **错题本**：答错自动进错题库，每题累计错误次数
- **📝 笔记**：确认答案后显示，可写可改，自动保存，下次打开自动显示
- **⭐ 收藏 / 🗑 重置进度（3 次确认）**
- **进度与笔记**：自动保存到本机（localStorage），关闭/重开不丢失
- **答案保密**：作答前界面绝不显示答案；题目内容与原始题库 100% 一致（已逐题核对）

## 重新生成（题库更新后）

若桌面版 `C刷题软件/题库.json` 更新了，重新生成手机版：

```bash
python build_web.py
```

会同时更新：
- `www/index.html`（浏览器版）
- `android/app/src/main/assets/index.html`（APK 版）

重新生成后，用 Android Studio 重新 Build APK 即可。

## 文件结构

```
C刷题软件手机版/
├── build_web.py             从桌面版题库生成手机版 index.html
├── www/                     浏览器版（单文件离线应用）
│   ├── template.html        模板（含功能代码，题库为占位符）
│   └── index.html           最终生成版（题库内嵌，直接可用）
└── android/                 Android 工程（Android Studio 打开构建 APK）
    ├── build.gradle
    ├── settings.gradle
    ├── gradle.properties
    ├── gradle/wrapper/gradle-wrapper.properties
    └── app/
        ├── build.gradle
        └── src/main/
            ├── AndroidManifest.xml
            ├── java/com/cquiz/app/MainActivity.java   WebView 壳
            ├── res/values/styles.xml
            └── assets/index.html                      内嵌题库的应用
```

## 说明

- 纯 HTML/CSS/JS 单文件实现，无任何外部依赖，离线可用
- WebView 已启用 JavaScript 与 localStorage（进度/笔记持久化）
- **系统要求**：Android 7.0（minSdk 24）及以上——其 WebView 完整支持应用所用语法，兼容稳定
- 应用图标/名称可在 Android Studio 中按需修改
