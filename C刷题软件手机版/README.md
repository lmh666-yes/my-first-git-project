# 刷题软件 · 手机版

> 基于桌面版「C刷题软件」制作的**手机端应用**。当前内置题库：**嵌入式软件开发工程师（中级）** 单选 80 题 + 判断 50 题，共 130 题。
> 本版为固定题库（不做题库切换），单文件、离线可用。

## 两种使用方式

### 方式一：手机浏览器直接使用（免安装）

把 **`www/index.html`** 这个单文件发到手机（微信/网盘/数据线拷贝均可），用手机浏览器打开即可刷题。
无需安装、无需联网，进度与笔记自动保存在手机本地（localStorage）。

### 方式二：打包成 APK 安装（推荐）

把本文件夹打包转移到另一台电脑（装有 Android Studio）上构建 APK。下面按 **5 步** 完整说明。

#### 第 1 步：打包并转移到目标电脑

1. 右键整个 **`C刷题软件手机版`** 文件夹 →「压缩为 zip」（或 7z/rar）
2. 把压缩包发到目标电脑（U 盘 / 微信 / 网盘均可），解压到任意位置

> 已确认：文件夹内**不含任何本机残留配置**（`local.properties`、`.gradle`、`build/`、`.idea` 均不存在，
> 且已被 `.gitignore` 排除），可直接打包移植；全部路径均为相对路径，换电脑无需改任何文件。
> 建议解压到**英文路径**（如 `D:\cquiz`），可避免个别电脑中文路径的兼容问题（非必须）。

#### 第 2 步：目标电脑环境要求（仅首次需要准备）

| 项目 | 要求 | 说明 |
|---|---|---|
| Android Studio | 需安装（免费） | 自带 **JDK 17**（本工程 AGP 8.2.2 要求），无需单独装 Java |
| 网络 | 首次构建需联网 | 自动下载 **Gradle 8.2 + AGP 8.2.2 + appcompat 1.6.1**，约 5–15 分钟 |
| Android SDK | 需 **API 34** 平台 | 首次 Sync 会提示，点「下载」自动安装 |

下载地址：https://developer.android.com/studio

#### 第 3 步：用 Android Studio 打开项目

1. 打开 Android Studio → 启动界面点 **`Open`**（或菜单 `File → Open`）
2. 选择解压出来的 **`android`** 文件夹（注意：是 `android` 子文件夹，不是整个手机版文件夹，也不是 `www`）
3. 点 OK，Android Studio 开始 **Gradle Sync**（右下角进度条，首次会下载依赖，耐心等待完成，界面会提示 `Sync finished`）

> 提示：项目未内置 Gradle Wrapper，Android Studio 会**自动使用内置 Gradle** 完成同步与构建，无需额外配置。
> 若提示缺 `local.properties`（SDK 路径）——正常现象，Android Studio 会自动生成，无需手动创建。

#### 第 4 步：构建 APK

1. 顶部菜单：**`Build → Build Bundle(s) / APK(s) → Build APK(s)`**
2. 左下角 Build 面板出现 `BUILD SUCCESSFUL` 即构建成功
3. 生成的 APK 在：
   - 调试版：`android\app\build\outputs\apk\debug\app-debug.apk`（默认构建这个）
   - 发布版：`android\app\build\outputs\apk\release\app-release.apk`（需配置签名后才建议使用）

> 更省事的方法：构建成功后 Android Studio 右下角会弹出通知「APK(s) generated successfully」，
> 点 **`locate`**（或 **`Show in Explorer`**）可直接打开 APK 所在文件夹。

#### 第 5 步：安装到手机

1. 把 **`app-debug.apk`** 发到手机（微信文件 / 网盘 / 数据线拷贝均可）
2. 手机上点击该文件 → 按提示**允许“安装未知来源应用”**（不同手机设置入口不同，一般为安装时的弹窗开关，或「设置 → 安全 → 未知来源」）
3. 安装完成，桌面出现「刷题软件」图标，点击即可离线刷题

#### 常见问题排查

| 现象 | 原因与解决 |
|---|---|
| 报错 `Unable to find Gradle tasks to build` | **打开错了文件夹**——要打开的是 **`android`** 子文件夹（含 `settings.gradle`/`build.gradle`/`app`），不是整个手机版文件夹，也不是 `www`；先 `File → Close Project` 再重新 `Open` 正确文件夹 |
| 打开项目提示缺 SDK / `local.properties` | 正常，Android Studio 会自动生成并提示下载 SDK，点下载即可 |
| Sync 报错 `Could not find com.android.application:8.2.2` 等 | 网络问题或未完成依赖下载 → 检查网络后点菜单 `File → Sync Project with Gradle Files` 重试 |
| Sync 很慢 / 下载失败（国内网络） | 可给 `android/build.gradle` 与 `settings.gradle` 配置国内镜像仓库（如阿里云 `maven.aliyun.com`），或用网络代理后重试 |
| 构建报错 `requires JDK 17` | 说明 Android Studio 版本过旧 → 升级 Android Studio（新版内置 JDK 17） |
| 构建报错 `Android SDK 34 not found` | 打开 SDK Manager（`Tools → SDK Manager`）勾选安装 **Android 14 (API 34)** |
| 构建后手机上打不开 / 白屏 | 确认安装的是**刚构建的 APK**；本应用需 Android 7.0（API 24）及以上系统 |

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
