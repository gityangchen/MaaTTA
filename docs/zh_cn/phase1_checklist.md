# 一期模板裁图清单

给安卓专家。流水线骨架已经接上。表里多数 PNG 还没有；已经裁进仓库的不要用假图覆盖。缺图时对应节点匹配失败，任务会在主界面锚点或子界面超时，这是预期，不是脚本写坏了。

不要交纯色、空白或手画的假图。文件放进仓库后再跑调试任务。

`maatools.config.mts` 里暂时把 `unknown-image` 设成 `ignore`，否则 `npx @nekosu/maa-tools check` 会因为这些缺图失败。PNG 进仓库后删掉这条忽略，写错文件名才能再次被检查出来。

## 采集环境

1. Windows 上的 MuMu 12。ADB 默认 `127.0.0.1:16384`（多开时每个实例端口不同，以模拟器实例设置为准，本项目按 16384 写说明）。
2. 模拟器分辨率锁定 **1280×720**，DPI **240**。短边是 720。国服 MuMu（`com.lilithgame.pgame.android.cn`）已接受竖屏 **720×1280**（短边 720）作为裁图分辨率，不要求横屏游戏画面。
3. `assets/interface.json` 里 Adb 控制器的 `display_short_side` 已是 **720**。裁图必须来自 MaaDebugger（或同一缩放）里的截图，也就是短边已经变成 720 之后的画面。不要拿模拟器相册原图再自己缩放。
4. **MuMu 必须用 AdbShell 点击。** 默认的 Maatouch / minitouch / EmulatorExtras 会报点击成功，但触摸坐标和短边 720 的画面对不上，邮件入口点了邮箱也不开。`adb shell input tap` 才和这张 720×1280 截图一致。官方 Project Interface v2 **没有** Adb 的 input 字段（写明自动检测），不要自己编 `adb.input: "AdbShell"` 这种字符串。打包用的通用 UI（MFAAvalonia）会读 `controller.adb.input` 的**整数**位掩码：`1` = AdbShell，`2` = MinitouchAndAdbKey，`4` = Maatouch，`8` = EmulatorExtras。本仓库已经写成 `1`。MaaDebugger 的 Connect **不读**这个字段，仍用 AdbController 默认输入；用 Python 连模拟器时调用 `agent/mumu_adb.py` 的 `connect_adb`，它只传 `MaaAdbInputMethodEnum.AdbShell`。
5. PNG，无损。裁**控件本身**再留一圈窄背景，不要裁全屏。点击类节点会点中匹配到的矩形，所以领取、返回、关闭必须裁按钮，不要裁整页。
6. 维护弹窗例外：`maintenance.png` 裁弹窗主体，节点动作是停止任务，不会去点它。
7. 一张逻辑用一个文件。红点导致邮件图标对不上时，再追加 `phase1/mail/entry_dot.png`，并把 `MailEntry.template` 改成数组。七日如果是七个格子，`sevenday_claim.png` 只裁「可领取」那一格。
8. 未写 `threshold` 的模板匹配用框架默认 0.7。通用关闭叉写了 0.85。误识别再调高，漏识别再调低。结果默认按 `Horizontal` 取最左边，不是最高分，所以中部的中等分数也会抢走底部的真按钮。
9. 路径相对于 `assets/resource/image/`。流水线里的 `template` 不要带 `image/` 前缀。
10. `roi` 是 `[x, y, w, h]`，坐标在短边 720 缩放后的截图上。竖屏就是 **720×1280**。`[0, 0, 0, 0]` 才是全屏。模板匹配只在这块矩形里做，模板必须比矩形小，命中框也必须整块落在矩形里。

OCR 模型还要另外下，见 [how_to_develop.md](develop/how_to_develop.md) 第 2 步，解压到 `assets/resource/model/ocr/`。没有 `det.onnx` / `rec.onnx` / `keys.txt` 时，带 OCR 的节点不可用。模型不要提交。

## 还缺的模板

| 文件 | 节点 | 裁什么 |
| --- | --- | --- |
| `phase1/home/anchor.png` | `HomeGate`、`HomeAnchorProbe` | 主界面固定锚点。避开角色动画、红点和会滚动的公告。建议角落上的固定 UI |
| `phase1/friends/entry.png` | `FriendsEntry` | 已裁。主界面右侧「好友」入口，约 105×100，含红色通知点。无红点对不上时再追加第二张，不要覆盖原图 |
| `phase1/friends/back.png` | `FriendsBack` | 已裁。好友页（找朋友）底部居中白色关闭 X，100×100 RGBA。`roi` 为 `[250, 1120, 220, 160]`，只认这块底部。不限区域时中部有过 0.7 的误匹配。点它回到主界面 |
| `phase1/mail/entry.png` | `MailEntry` | 好友页右上角信封（设置齿轮右侧）。不是主界面图标 |
| `phase1/mail/claim.png` | `MailClaim` | 邮箱里的一键领取或单封领取按钮 |
| `phase1/mail/empty.png` | `MailEmpty` | 空邮箱空态（插画或固定空文案区域）。节点只识别，不点击 |
| `phase1/mail/back.png` | `MailBack` | 已裁。邮箱页底部关闭。`roi` 为 `[250, 1100, 220, 180]`。这张白 X 在好友页底部也会打到 1.0，不限区域会点到好友页的关闭。只回到好友页，不是回主界面 |
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

## 邮件路径

主界面 → 好友 → 邮件。竖屏裁图仍是 **720×1280**（短边 720）。

`HomeGate` 先点 `FriendsEntry`（`phase1/friends/entry.png` 已在仓库里），好友页打开后 `MailEntry` 用已经裁好的 `phase1/mail/entry.png`（右上角信封）。邮箱里的领取、空态和弹窗节点不变。`MailBack` 仍接到 `FriendsBack`，再接到 `Phase1Dispatch`。签到、七日、活动领奖、弹珠焚决仍排在同一轮 `HomeGate` 后面。`FriendsEntry` 的 `max_hit` 是 1，回到主界面后不会再次点进好友。

`phase1/mail/back.png` 只关掉邮箱，回到好友页。`FriendsBack`（TemplateMatch + Click）使用已裁的 `phase1/friends/back.png`（好友页底部居中白色关闭 X，100×100），插在 `MailBack` 和 `Phase1Dispatch` 之间，关掉好友层回到主界面。认不到这张关闭图时，`HomeGate` 认不到主界面锚点，`Phase1Dispatch` 大约 20 秒超时结束，不会死循环。

两个返回都限制在底部，坐标系是缩放后的 720×1280：

| 节点 | roi `[x, y, w, h]` | 为什么 |
| --- | --- | --- |
| `MailBack` | `[250, 1100, 220, 180]` | 模板 110×85。好友页上同一张图在底部白 X 打到 1.0，框是 `[305, 1185, 110, 85]`，整块落在这个 roi 里。不限区域时会把好友页的关闭当成邮箱关闭 |
| `FriendsBack` | `[250, 1120, 220, 160]` | 模板 100×100。限制在底部后探针命中 `[310, 1140, 100, 100]`。不限区域时中部有不少过了默认 0.7 的误匹配，又按从左到右取结果 |

`claim.png`、`empty.png`，以及 `maintenance.png` / `update_later.png` / `network_confirm.png` 仍然没有，不要补假图。邮箱非空、空态没出现、维护/更新/网络弹窗没出现，这几张就继续缺着。

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
