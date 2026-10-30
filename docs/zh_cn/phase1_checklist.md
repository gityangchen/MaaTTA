# 一期模板裁图清单

给安卓专家。流水线骨架已经接上，下面这些 PNG **都还没有**。缺图时对应节点匹配失败，任务会在主界面锚点或子界面超时，这是预期，不是脚本写坏了。

不要交纯色、空白或手画的假图。文件放进仓库后再跑调试任务。

`maatools.config.mts` 里暂时把 `unknown-image` 设成 `ignore`，否则 `npx @nekosu/maa-tools check` 会因为这些缺图失败。PNG 进仓库后删掉这条忽略，写错文件名才能再次被检查出来。

## 采集环境

1. Windows 上的 MuMu 12。ADB 默认 `127.0.0.1:16384`（多开时每个实例端口不同，以模拟器实例设置为准，本项目按 16384 写说明）。
2. 模拟器分辨率锁定 **1280×720**，DPI **240**。短边是 720。
3. `assets/interface.json` 里 Adb 控制器的 `display_short_side` 已是 **720**。裁图必须来自 MaaDebugger（或同一缩放）里的截图，也就是短边已经变成 720 之后的画面。不要拿模拟器相册原图再自己缩放。
4. PNG，无损。裁**控件本身**再留一圈窄背景，不要裁全屏。点击类节点会点中匹配到的矩形，所以领取、返回、关闭必须裁按钮，不要裁整页。
5. 维护弹窗例外：`maintenance.png` 裁弹窗主体，节点动作是停止任务，不会去点它。
6. 一张逻辑用一个文件。红点导致邮件图标对不上时，再追加 `phase1/mail/entry_dot.png`，并把 `MailEntry.template` 改成数组。七日如果是七个格子，`sevenday_claim.png` 只裁「可领取」那一格。
7. 未写 `threshold` 的模板匹配用框架默认 0.7。通用关闭叉写了 0.85。误识别再调高，漏识别再调低。
8. 路径相对于 `assets/resource/image/`。流水线里的 `template` 不要带 `image/` 前缀。

OCR 模型还要另外下，见 [how_to_develop.md](develop/how_to_develop.md) 第 2 步，解压到 `assets/resource/model/ocr/`。没有 `det.onnx` / `rec.onnx` / `keys.txt` 时，带 OCR 的节点不可用。模型不要提交。

## 还缺的模板

| 文件 | 节点 | 裁什么 |
| --- | --- | --- |
| `phase1/home/anchor.png` | `HomeGate`、`HomeAnchorProbe` | 主界面固定锚点。避开角色动画、红点和会滚动的公告。建议角落上的固定 UI |
| `phase1/mail/entry.png` | `MailEntry` | 主界面邮件入口图标 |
| `phase1/mail/claim.png` | `MailClaim` | 邮箱里的一键领取或单封领取按钮 |
| `phase1/mail/empty.png` | `MailEmpty` | 空邮箱空态（插画或固定空文案区域）。节点只识别，不点击 |
| `phase1/mail/back.png` | `MailBack` | 关闭邮箱或返回主界面的按钮 |
| `phase1/award/signin_entry.png` | `SignInEntry` | 签到入口。不在主界面就在入口和 `SignInBoard` 之间加中间节点 |
| `phase1/award/signin_claim.png` | `SignInClaim` | 签到面板上的签到/领取按钮 |
| `phase1/award/signin_back.png` | `SignInBack` | 离开签到面板 |
| `phase1/award/sevenday_entry.png` | `SevenDayEntry` | 七日入口 |
| `phase1/award/sevenday_claim.png` | `SevenDayClaim` | 当前可领的那一天，不要裁整页七格 |
| `phase1/award/sevenday_back.png` | `SevenDayBack` | 离开七日面板 |
| `phase1/award/activity_entry.png` | `ActivityAwardEntry` | 活动领奖入口（先一组）。在线奖励、通行证、限时活动页确认有独立图标后再拆新节点 |
| `phase1/award/activity_claim.png` | `ActivityAwardClaim` | 活动页上的领取按钮 |
| `phase1/award/activity_back.png` | `ActivityAwardBack` | 离开活动领奖页 |
| `phase1/marble/entry.png` | `MarbleAwardEntry` | 弹珠焚决入口。真机层级没确认，多出来的页面插在入口和 `MarbleAwardBoard` 之间 |
| `phase1/marble/claim.png` | `MarbleClaim` | 弹珠焚决领奖按钮 |
| `phase1/marble/back.png` | `MarbleBack` | 从焚决页回到主界面。多层返回就拆成多个节点，最后再接到 `Phase1Dispatch` |
| `phase1/popup/maintenance.png` | `PopupMaintenance` | 维护/停服弹窗主体。动作是 `StopTask`，不要裁确定按钮 |
| `phase1/popup/update_later.png` | `PopupUpdateLater` | 更新弹窗的「稍后」或关闭。不要裁「立即更新」 |
| `phase1/popup/network_confirm.png` | `PopupNetworkConfirm` | 网络异常弹窗的确定或重试按钮 |
| `phase1/popup/generic_close.png` | `PopupGenericClose` | 子界面右上角关闭叉，带一点弹窗边缘。不要挂到主界面那张分发上（流水线里已经没挂） |

可选、当前 JSON 还没引用：

- `phase1/mail/entry_dot.png`：邮件图标带红点的另一张。需要时把 `MailEntry` 的 `template` 改成 `["phase1/mail/entry.png", "phase1/mail/entry_dot.png"]`。

## 要在真机上核对的 OCR

这些句子是占位，和界面原文不一致就会漏判或误判。改的是 pipeline JSON 里的 `expected`，不是图片。

| 节点 | 现在写的句子 | 核对什么 |
| --- | --- | --- |
| `MailEmptyOcr` | 没有邮件 / 暂无邮件 / 邮箱为空 / 空空如也 | 空邮箱上的原文 |
| `SignInDoneOcr` | 已签到 / 明日再来 / 已领取 | 今天已经签过的提示 |
| `SevenDayDoneOcr` | 已领取 / 明日可领 / 全部领完 | 七日没有可领格子时的提示 |
| `ActivityAwardDoneOcr` | 已领取 / 明日再来 | 活动奖领完后的提示 |
| `MarbleDoneOcr` | 已领取 / 暂无奖励 | 弹珠焚决没有可领奖励时的提示 |
| `PopupBlockingOcr` | 服务器维护 / 停服维护 / 维护公告 / 立即更新 / 发现新版本 / 版本更新 / 网络异常 / 网络连接失败 / 请检查网络 | 弹窗上的整句。主界面普通文字如果被这张表命中，任务会直接停，把句子改长、改全 |

按钮模板已经能点掉弹窗时，OCR 兜底不会先被轮到。模板还没裁的时候，看到上表里的更新/网络/维护句子会 `StopTask`。

## 裁完怎么验

1. 把 PNG 放到上表路径，例如 `assets/resource/image/phase1/home/anchor.png`。
2. 游戏停在主界面，先跑任务「调试·主界面锚点」。只应该命中，不应该有点击。
3. 再跑「一期·领奖邮件」。某个子界面认不到，就只补那一行的图或在两个节点之间加一页，不要改 720 短边。

## 这期不做

- 二期每日任务、三期刷关：目录里只有说明，没有 JSON。
- 四期钓鱼赛跑，以及 MVP 礼盒（搜 UID、拜访家园、领盒、份数上限）：没有节点，授权档位预留 `activity`。
