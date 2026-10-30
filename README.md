# MaaTTA

塔塔冒险队自动挂机。基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) / [MaaPracticeBoilerplate](https://github.com/MaaXYZ/MaaPracticeBoilerplate)。

当前仓库是 **一期骨架：领奖 / 邮件**。流水线节点和空的图片路径已经接上，真机裁图还没有。二期到四期只有目录说明。

## 运行环境

- Windows
- MuMu 12，ADB `127.0.0.1:16384`
- 模拟器分辨率锁定 1280×720，DPI 240（短边 720）
- Python 3.12，`python` 在 PATH 里
- [MaaDebugger](https://github.com/MaaXYZ/MaaDebugger) 或打包后的通用 UI

`assets/interface.json` 里的控制器是 Adb，`display_short_side` 为 720。截图会缩放到短边 720，模板图按这个尺寸裁。

## 路线图

| 期 | 内容 | 授权档 | 状态 |
| --- | --- | --- | --- |
| 1 | 领奖 / 邮件（主界面锚点、邮箱、签到、七日、活动领奖、弹珠焚决、维护/更新/网络弹窗） | `base` | 骨架，缺模板图 |
| 2 | 每日任务 | `base` | 未写 pipeline |
| 3 | 刷关 | `base` | 未写 pipeline |
| 4 | 钓鱼赛跑 | `activity` | 未写 pipeline |

四期还有一个附属 MVP 礼盒，现在只有说明、没有节点：搜 UID → 拜访家园 → 领盒，并加上份数上限。档位同样是 `activity`。见 [assets/resource/pipeline/phase4/README.md](assets/resource/pipeline/phase4/README.md)。

## 安装

```bash
python -m pip install -r requirements.txt
```

依赖是 `maafw>=5,<6`。PyPI 包名是 `maafw`，代码里 `import maa`。不要装别的同名包。

文字识别模型不进 git。按 [docs/zh_cn/develop/how_to_develop.md](docs/zh_cn/develop/how_to_develop.md) 第 2 步下载 `ppocr_v6`，解压到 `assets/resource/model/ocr/`，目录里要有 `det.onnx`、`rec.onnx`、`keys.txt`。那篇文档开头仍是上游模板的创建说明，克隆地址忽略即可，OCR 那一步仍然适用。

MuMu 里打开 ADB，然后：

```bash
adb connect 127.0.0.1:16384
```

## 用 MaaDebugger 跑

1. 用 MaaDebugger 打开本仓库的 `assets/interface.json`。
2. 控制器选「MuMu 12」，资源选「默认」。
3. 启动时会拉起 Agent：`python ../agent/main.py`。工作目录是 `assets/`，所以上面这个相对路径指向仓库根的 `agent/main.py`。
4. 打包后的目录里，`interface.json` 和 `agent/` 同级。`tools/install.py` 会把参数改成 `./agent/main.py`。
5. 先跑「调试·主界面锚点」，再跑「一期·领奖邮件」。

`python` 找不到时，把 `interface.json` 的 `agent.child_exec` 改成你机器上的解释器。

通用 UI 里的任务：

- **一期·领奖邮件**（默认勾选）：CDK `base` 通过后，确认主界面，再依次尝试好友（邮件在好友页）、签到、七日、活动领奖、弹珠焚决。
- **调试·主界面锚点**：只做模板匹配，不点击。
- **CDK 校验(开发)**：连续检查 `base` 和 `activity`。

模板图还没放进 `assets/resource/image/phase1/` 时，主界面锚点匹配不到，任务大约 20 秒后超时。这是骨架的预期，不是连接失败。

## 下一步裁哪些图

清单在 [docs/zh_cn/phase1_checklist.md](docs/zh_cn/phase1_checklist.md)。里面按文件名写了节点、该裁按钮还是弹窗主体，以及要改的 OCR 占位句。

裁图规则摘要：

- 从短边已经是 720 的截图上裁 PNG
- 点击类节点裁按钮本身；维护弹窗裁主体（节点会停止任务）
- 不要提交假图。检查配置暂时忽略缺图（`unknown-image`），图进仓库后要删掉这条忽略，见清单开头

## CDK 桩

实现在 [agent/cdk_auth.py](agent/cdk_auth.py)，流水线通过自定义识别 `cdk_gate` 和自定义动作 `check_cdk` 调用。

| 档位 | 含义 |
| --- | --- |
| `base` | 长期核心：领奖/邮件、以后的每日任务和刷关 |
| `activity` | 钓鱼、围猎、MVP 礼盒，以及四期钓鱼赛跑 |

默认**开发放行**，方便没接服务器时先对模板。

- 不设置 `MAATTA_DEV_SKIP_CDK`，或设为 `1` / `true` / `yes` / `on`：两档都通过
- 设为 `0` / `false` / `no` / `off`：要求 `MAATTA_CDK` 非空。非空也只是本地占位，不会发到服务器，没有签名和防破解
- 写成别的值：仍按放行，避免拼错把联调卡住
- 未知档位：返回失败

本地看结果：

```bash
python agent/cdk_auth.py
```

关掉放行再看失败：

```bash
# Windows PowerShell
$env:MAATTA_DEV_SKIP_CDK = "0"
$env:MAATTA_CDK = ""
python agent/cdk_auth.py
```

不要把 CDK 写进仓库或日志。动作日志只打印「有没有串」，不打印内容。

发码服务和防篡改以后再做。在那之前，这个桩不能当成已经授权。

## 目录

```text
assets/interface.json                 项目名、MuMu 控制器、一期任务、Agent
assets/resource/pipeline/phase1/      一期流水线
assets/resource/pipeline/phase2/      空说明
assets/resource/pipeline/phase3/      空说明
assets/resource/pipeline/phase4/      空说明（含 MVP 礼盒 TODO）
assets/resource/image/phase1/         裁图落点，目前没有 PNG
agent/main.py                         Agent 入口
agent/cdk_auth.py                     check_license
agent/cdk_action.py                   custom action check_cdk
agent/cdk_reco.py                     custom recognition cdk_gate
docs/zh_cn/phase1_checklist.md        裁图清单
```

一期 JSON 用 v1 写法（`recognition` / `action` 为字符串），和原来的 boilerplate 示例一致。弹窗用节点上的 `jump_back` 处理完跳回调用方。

## 开发文档

- [Agent 写法](docs/zh_cn/develop/agent.md)（示例已换成 CDK 桩；文中旧的最小数字示例只说明 API）
- [如何开发](docs/zh_cn/develop/how_to_develop.md)（OCR 与发版 CI）
- [PR 规范](docs/zh_cn/develop/pull_request_guidelines.md)

本模板附带的 CI 会在打 `v*` tag 时打包通用 UI。资源检查见 `.github/workflows/check.yml`。

## 鸣谢

本项目由 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 驱动。
