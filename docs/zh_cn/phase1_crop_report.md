# MaaTTA phase1 裁图进度报告（给父代理）
时间：2026-10-30 18:35 Asia/Shanghai
仓库：C:\Users\lenovo\TTWORK\MaaTTA（main @ ad132e1，已 pull；未 commit/push）
清单：docs/zh_cn/phase1_checklist.md 存在

## 分辨率（重要）
- MuMuManager 已锁定：custom **1280×720**，DPI **240**，window_auto_rotate=false
- 国服包 com.lilithgame.pgame.android.cn 为**竖屏游戏**（SplashActivity / 主界面均为竖屏布局）
- 实机 ADB screencap 稳定为 **720×1280**，短边=720，与 display_short_side=720 一致
- 无法在不把 UI 拧成横置的前提下产出「游戏画面像素 1280×720」的横屏截图；竖屏 720×1280 即本游戏在 1280×720 面板设定下的自然短边 720 画面
- 本次模板均来自 720×1280 真机截图裁切（短边 720），**未伪造**弹窗图

## 已完成（本地路径，相对 assets/resource/image/）
| 文件 | 状态 | 说明 |
| --- | --- | --- |
| phase1/home/anchor.png | 已裁 | 主界面「建筑商店」固定角标（避开动画/红点/公告） |
| phase1/friends/entry.png | 已裁 | 主界面右侧好友入口，约 105×100，含红色通知点。流水线 `FriendsEntry` 使用这张图 |
| phase1/mail/entry.png | 已裁 | 信封图标；**不在主界面**，在「好友」页右上角（设置齿轮右侧）。流水线 `MailEntry` 仍用这张图 |
| phase1/mail/claim.png | 缺 | 列表附件多为已领绿勾；独立领取按钮未出现，已删除错误 claim.png |
| phase1/mail/back.png | 已裁 | 邮箱页底部关闭 X |
| phase1/popup/generic_close.png | 已裁 | 饲养礼包弹窗右上角关闭 X（带一点弹窗边缘） |

绝对路径根：C:\Users\lenovo\TTWORK\MaaTTA\assets\resource\image\

## 缺项 / 未出现（不伪造）
| 文件 | 状态 | 原因 |
| --- | --- | --- |
| phase1/mail/empty.png | 缺 | 当前邮箱非空（多封未删邮件），**空邮箱态未出现** |
| phase1/award/signin_entry.png 及 claim/back | 缺 | 主界面右侧勾选图标进的是「任务」非签到；独立签到入口本轮未找到 |
| phase1/award/sevenday_* | 缺 | 七日入口本轮未出现（公测 TapTap 七日或已过期/外链） |
| phase1/award/activity_* | 缺 | 活动领奖独立入口未稳定裁到（联赛「奖励」、福利助手等需再探并加中间页） |
| phase1/marble/* | 缺 | 弹珠焚决入口本轮未确认 |
| phase1/popup/maintenance.png | **未出现** | 无维护弹窗 |
| phase1/popup/update_later.png | **未出现** | 无更新弹窗 |
| phase1/popup/network_confirm.png | **未出现** | 无网络异常弹窗 |

## 流水线需知（避免卡死）
1. **邮件链路**已改成 主界面 → 好友 → 邮件：`HomeGate` → `FriendsEntry`（已有 `phase1/friends/entry.png`，含红点）→ `FriendsBoard` → `MailEntry`（已有 `phase1/mail/entry.png`）→ `MailBoard` → `MailBack` → `Phase1Dispatch`。竖屏仍是 720×1280。
2. `phase1/mail/back.png` 只关邮箱，回到好友页。回到主界面还要好友页返回/关闭。没有这张图，因此没有添加 `FriendsBack` 节点，也不要造 `phase1/friends/back.png`。真图裁到后再把 `FriendsBack` 插在 `MailBack` 和 `Phase1Dispatch` 之间。在此之前邮件关完停在好友页，分发认不到主界面锚点，约 20 秒超时结束，不会死循环。
3. 弹窗模板缺图时，依赖 PopupBlockingOcr + 已有 generic_close；维护/更新/网络按钮图未采到，OCR 兜底仍可 StopTask，避免空转卡死。好友页 `FriendsBoard` 与邮箱 `MailBoard` 都会先看这些弹窗。
4. 未跑 MaaDebugger 缩放校验；源图短边已是 720。建议父代理用「调试·主界面锚点」验 anchor。
5. **未 git commit / push**（必填模板未齐）。

## git
working tree 仅有未跟踪：phase1/home/、mail/、popup/ 下新 PNG。

## 追加
- `phase1/friends/entry.png` 已加入（主界面右侧好友入口）。裁图约 105×100，含红色通知点，红点可能变化，按原图保留。邮件路径需要 主界面 → 好友 → 邮件；`mail/entry` 在好友页，不在主界面。
