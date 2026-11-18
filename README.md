# iPhone 双账号微信实验记录与消息提醒方案

本文记录一次在 iPhone 上尝试同时使用两个微信账号的过程，涵盖实验版应用、通过安卓手机转发通知，以及 SideStore 续签。测试时间为 2026 年 11 月。此方案包含第三方修改包，属于**实验方案**：不同设备、微信版本或账号状态下可能无法复现，也可能触发微信的登录安全验证。

可下载版本：[PDF 版操作指南](iPhone微信双账号实验操作指南.pdf)。

## 结果与适用范围

| 项目 | 本次观察 |
| --- | --- |
| 测试设备 | iPhone 17 Pro Max，iOS 27.2；红米 K60；Windows 电脑 |
| 微信客户端 | 官方微信与基于 FChat 8.0.71 的独立实验版；安卓端使用微信 |
| 同时在线 | 实验版登录后，红米上的同一账号仍在线；iPhone 实验版可进入聊天并查看消息 |
| 界面 | 部分小程序顶部按钮放大并遮挡标题，部分小程序显示正常，原因未确定 |
| 消息提醒 | 红米微信通知经短信转发器和 Bark 在 iPhone 上收到；锁屏后台的长期稳定性未验证 |
| 签名 | SideStore 中能看到 FChat，导入后聊天记录保留；长期自动续签尚未验证 |

这个方案把第二账号放在独立的实验客户端里。Bark 提供的是由安卓设备**转发的通知**，并非实验客户端获得官方微信的原生推送能力；通知内容和微信内消息也未必完全一致。安卓设备需要在线并产生微信系统通知，iPhone 的 Bark 才有机会收到转发提醒。

> **阅读前请注意：**本项目包含第三方修改客户端，其安全性、微信服务端兼容性和账号安全均无法保证；请先保存重要聊天记录。不要在来源或行为未核实的第三方客户端中输入敏感密码，涉及学校、银行等重要服务时建议使用官方客户端或官方网页。不要公开自己的证书、账号和推送地址。

## 下载和致谢

本实验版基于 **FChat 8.0.71** 调整构建，感谢 FChat 原作者、团队及上游发布者 [Taosky](https://github.com/Taosky/unsigned-ipa-cn/releases/tag/fchat) 的工作，同时感谢 wechat-ipad-login、ElleKit 和 splice 项目。本版是独立的第三方实验修改，不代表腾讯或上游项目官方发布、背书或支持。

安装包作为 [GitHub Releases 附件](https://github.com/lilikurong/iphone-wechat-dual-account-guide-public/releases/latest)提供。文件 SHA-256：

```text
FE0F665C66DC7A6A7F21886CF5BD03C1211636CF0CBA65C056BB414504583B44
```

该包需要自行签名和安装；更改下载文件名不会改变包内应用名称，安装后可能显示 **FChat Test2**。本次测试能够启动并查看聊天，不代表所有设备、小程序、推送或长期自动续签均已验证。

## 需要准备什么

- 一部 iPhone：已有官方微信；开启开发者模式并设置锁屏密码。
- 一部备用安卓手机：登录需要同步提醒的微信账号，确保微信能产生系统通知。
- Windows 电脑：安装 iLoader 和苹果设备驱动，首次安装应用时用数据线连接 iPhone。
- iPhone 安装 SideStore、LocalDevVPN 与 Bark；安卓安装短信转发器 SmsForwarder。
- 如果所在地区的 App Store 无法下载 LocalDevVPN，准备一个可下载该应用的外区 Apple 账号；本次使用外区账号获取 LocalDevVPN。
- 可从 Releases 获取本次实验 IPA；若自行重建，需要准备来源和授权可核实的 FChat 8.0.71 IPA 与构建依赖。

免费 Apple 账号的个人开发签名通常只有 7 天有效期，SideStore 也会占用一个侧载应用名额。Apple 对免费个人团队还限制每台设备 3 个应用及一周内 10 个 App ID，详见 [Apple 开发者账号说明](https://developer.apple.com/help/account/basics/about-your-developer-account)。

## 一、准备独立实验版微信

### 实验使用的组件

本次测试的诊断包是由以下组件**另外组合并修改**得到，不能直接将上游插件当作最终实验包：

1. [FChat 8.0.71 上游发布页](https://github.com/Taosky/unsigned-ipa-cn/releases/tag/fchat)提供的 IPA。它属于第三方包，并非腾讯官方渠道。
2. [wechat-ipad-login](https://github.com/cjq6525/wechat-ipad-login) 项目编译出的插件。其上游文档记录的是越狱环境，未声明兼容本次非越狱设备。
3. 注入工具 [splice](https://github.com/franklintra/splice) 与 ElleKit 的 CydiaSubstrate 兼容框架。实验中所用的框架文件来自 [Impactor 仓库的 ellekit.deb](https://github.com/xweiba/Impactor/blob/main/crates/plume_utils/src/ellekit.deb)。
4. 针对启动崩溃制作的本地诊断改动：在 ARM64 和 ARM64e 两个切片中，分别禁用对 `sysctlbyname`、`sysctl` 和 `uname` 的三处底层函数钩子调用；保留 `UIDevice.model` 的消息钩子。

### 本次诊断插件的构建记录

下列步骤供有 iOS 重签名经验的读者核查和自行研究。**它不是完整的一键复现教程**：本仓库中的脚本只修改并验证特定版本的插件；整个 IPA 的拼装、重签名和安装流程尚未用公开材料独立重建。上游构建产物可能过期、需要 GitHub 登录或不可用，上游项目未提供明确的代码许可证，使用前请自行核实授权。

1. 此次曾使用 FChat 8.0.71 IPA。本次发布整理时原始 IPA 不在工作目录中，无法重新核验其完整性或独立重建整个应用；与本次实验不同的文件不可假定有相同行为。
2. 本次使用的插件来源于 [wechat-ipad-login 的 Actions 构建运行 36117366255](https://github.com/cjq6525/wechat-ipad-login/actions/runs/36117366255)，从产物的 `.deb` 中提取 `var/jb/Library/MobileSubstrate/DynamicLibraries/WeChatIPadLogin.dylib`。原始插件 SHA-256 为：

   ```text
   D9B688C98C514C48289E46C3E633919646622D26C59D9B975C02A8DEEC991F73
   ```

3. 在本仓库目录运行下面的命令，输入文件必须是该哈希对应的原始插件，输出必须是**不存在的新文件**。脚本只接受这一份特定二进制，先验证哈希和六条原始指令，然后分别将 ARM64 / ARM64e 切片中的三处底层 `MSHookFunction` 调用改为 NOP；它不会改动输入，也不会下载或打包微信。

   ```bash
   python tools/prepare_dylib.py original.dylib patched.dylib
   ```

   应输出下列 SHA-256；只验证了插件补丁的字节变化，不代表签名、应用运行或兼容性已经得到验证：

   ```text
   BCC373DB0BAA95AEDE5AA23930478EF00942C173F0A5BBB91EDA7E53870B2B7C
   ```

4. 将生成的插件命名为 `WeChatIPadLogin.dylib`，用 [splice](https://github.com/franklintra/splice) 的 `tweak` 功能注入到自行取得的 IPA。该次所用命令的形式如下；Windows 版本及运行所需依赖请以项目说明为准：

   ```bash
   splice-cli tweak input.ipa --inject WeChatIPadLogin.dylib --output injected.ipa
   ```

5. 此次插件依赖 `@rpath/CydiaSubstrate.framework/CydiaSubstrate`。实验包还将从 [Impactor 的 ellekit.deb](https://github.com/xweiba/Impactor/blob/main/crates/plume_utils/src/ellekit.deb) 提取的 `CydiaSubstrate.framework` 放入 `Payload/WeChat.app/Frameworks/`，包含框架可执行文件及 `Info.plist`。请自行验证组件来源、架构、框架加载路径及授权，不能省略依赖就假定能运行。
6. 确认实验包的 `Info.plist` 中 `CFBundleIdentifier` 与已安装的官方微信不同，使用可由自己的签名账号管理的独立标识；本次实验使用的独立标识为 `com.tencent.fchatipadtest`。重新打包时保留 IPA 的 `Payload/WeChat.app/` 结构；修改 IPA 会使原签名失效，需要使用 iLoader 或其他签名工具重新签名安装。签名工具还可能改写标识和权限，安装前必须核对，不能保证数据保留或原生推送可用。

插件测试使用本地原始二进制与脚本生成结果逐字节比较；由于本次整理缺少原始 IPA，**没有重新构建或验证整个安装包**。自行实践时，应先使用非重要账号和已备份数据测试，不要以此作为运行或安全保证。

最初注入完整插件的实验版在启动时闪退。设备报告显示系统库代码页执行权限异常，调用栈包含插件初始化；底层钩子是重点怀疑方向，但日志本身不能证明唯一根因。禁用上述三个函数钩子的诊断包在本次设备上可以打开并登录；**这不能证明所有设备都适用，也不保证 iPad 登录入口、微信后台推送或所有小程序正常。**

诊断包设置了与官方微信不同的 Bundle ID，并通过 iLoader 重新签名安装。它不是上游的原版 FChat，也不是原版 `wechat-ipad-login` 插件。上游代码和组件来源见本节；自行构建前应核实来源、完整性及相关授权，并先确认可以备份和恢复原有应用数据。

### 安装和登录

1. 保存重要聊天记录，先保留 iPhone 上的官方微信和安卓上的微信。
2. iPhone 用数据线连接 Windows，在手机上解锁并信任电脑；在 iLoader 中选择设备与用于签名的 Apple 账号。
3. 通过 iLoader 的**导入 IPA**选择已下载或自行准备的诊断包。签名器可能改写应用标识；若出现替换应用提示，先核对目标，不要覆盖官方微信。
4. 在 iPhone 按系统提示信任开发者证书并启用开发者模式；打开实验版，确认可以启动后再按微信界面提示登录自己的账号。
5. 登录后检查安卓微信是否仍在线，以及 iPhone 是否能打开聊天、联系人和所需小程序。出现掉线或体验资格限制时，恢复原先可用的官方微信登录，不要反复切换账号。

本次也测试过让客户端显示“微信 for iPad”入口的另一实验版本：可以同时登录，但聊天、联系人等页面无法正常点击；之后采用的诊断包行为不同。不能把前者的 iPad 入口与后者的登录机制直接画等号。

## 二、通过安卓和 Bark 转发微信通知

### 1. 在 iPhone 上设置 Bark

1. 从 [Bark 项目](https://github.com/Finb/Bark)提供的 App Store 入口安装 Bark，并允许通知。
2. 打开 Bark 首页，找到该设备的推送地址。地址包含设备专属密钥，应当像密码一样保管；不要将真实地址放进截图、帖子或仓库。
3. 建议在“加密设置”中配置加密，并在安卓发送端使用完全一致的算法、模式、填充和密钥。Bark 的设备推送地址与内容加密密钥是两种不同的信息。加密用法见 [Bark 加密文档](https://github.com/Finb/Bark/blob/master/docs/en-us/encryption.md)。

### 2. 在安卓上设置发送通道

1. 从 [SmsForwarder 官方仓库](https://github.com/pppscn/SmsForwarder)选择适用于设备的发布版本，安装并打开。
2. 打开“发送通道”，点“＋”，选择 **Bark**。
3. 填写通道名称，并将 iPhone Bark 首页提供的**服务器地址及设备密钥部分**填入 `Bark-Server`。按当前应用界面要求保留末尾 `/`；不要把示例里的 `title/body` 追加到基础地址。
4. 若 Bark 端已启用 AES 加密，在发送通道中选对应的加密算法并填写同一个密钥。两侧模式、填充等参数须一致；不确定时对照双方界面，不要把密钥发给他人。
5. 点击“测试”，**确认 iPhone 实际收到可读的通知**，再保存通道。若 iPhone 显示 `Decryption Failed`，表示通知已抵达但解密没有成功，应先检查双方加密设置。

### 3. 只转发微信通知

1. 在安卓短信转发器“通用设置”中，开启**转发应用通知**，按系统提示允许该应用读取通知。通知使用权可能使它看到其他应用的通知，因此只授予可信应用。
2. 进入“转发规则”，添加**应用通知**规则，选择刚才的 Bark 发送通道。
3. 匹配字段选 **APP 包名**，匹配方式选“是／等于”，填写安卓微信实际包名。常见官方包名为 `com.tencent.mm`；如果使用分身或定制版本，先在安卓应用信息中确认实际包名。
4. 启用并保存规则。不要为了测试把“全部通知”长期转发，以免把其他应用的验证码或敏感通知一并发出。
5. 保持安卓微信在线，退出当前聊天，让另一个账号发送测试消息。先确认安卓上出现微信系统通知，再看短信转发器的“转发日志 → 应用”和 iPhone Bark 通知。

短信转发器规则和通道的具体字段可能随版本变化，可参考 [官方常见问题](https://github.com/pppscn/SmsForwarder/wiki/%E3%80%90%E5%BF%85%E8%AF%BB%E3%80%91%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)。不要启用短信、通话记录等与目标无关的转发或权限。

### 4. 红米后台设置

在“设置 → 应用管理 → 短信转发器”的应用信息中，查找省电策略或电池设置，选择**无限制**；如系统提供“后台自启动”，可为该应用开启。界面名称取决于 MIUI / 澎湃 OS 版本。保留短信转发器用于前台服务的常驻通知，避免从最近任务中强制停止应用。小米对后台限制的说明见 [Powerkeeper 文档](https://dev.mi.com/distribute/doc/details?pId=1628)。

做锁屏对照测试：让安卓锁屏且 iPhone 保持亮屏，发一条新消息并等待；若没有收到，仅解锁安卓但不打开转发器再等；仍没有时再打开转发器。根据哪个步骤触发通知，进一步排查安卓锁屏网络、后台调度或发送队列。应用保持后台并不保证实时可靠。

## 三、安装 SideStore 并管理续签

### 1. 安装和初始化

**准备 LocalDevVPN 的商店账号：**本次通过外区 App Store 下载 LocalDevVPN。先尝试在当前 App Store 搜索；如果无法获取，可使用能下载该应用的外区 Apple 账号，例如查看 [LocalDevVPN 美国区页面](https://apps.apple.com/us/app/localdevvpn/id6755608044)。不同地区的上架情况可能变化；已有应用时不必重复下载。Bark 在[中国大陆 App Store](https://apps.apple.com/cn/app/id1403753865)有页面，并非本方案中必须通过外区下载的应用。

切换时，在 iPhone 的“设置 → 你的姓名 → 媒体与购买项目”中退出当前商店账号，再登录自己的外区账号并安装 LocalDevVPN；安装后可切回原商店账号。这里只切换“媒体与购买项目”，不需要退出 iCloud，见 [Apple 的账号切换说明](https://support.apple.com/zh-cn/108911)。以后更新 LocalDevVPN 可能需要重新登录下载时使用的账号，见 [Apple 的更新说明](https://support.apple.com/zh-cn/111001)；不要使用来历不明的共享账号。若要更改现有账号地区，先阅读 [Apple 的地区更改说明](https://support.apple.com/zh-cn/118283)，其中涉及余额、订阅和付款信息。

外区**商店账号**用于下载 LocalDevVPN，可以与 iLoader 和 SideStore 使用的**签名账号**不同；本次为了管理同一个实验版，iLoader 与 SideStore 使用同一个签名账号。使用外区账号下载 LocalDevVPN 本身不延长签名有效期。

1. 用 iLoader 选择 iPhone 和原先用于签名的 Apple 账号，选择 **SideStore（稳定版）**，按照系统提示完成安装与信任。
2. iPhone 连接 Wi‑Fi，安装并连接 [LocalDevVPN](https://apps.apple.com/app/id6755608044)。这是供 SideStore 与设备本地安装服务通信的工具，不是用于访问国外网站的代理；SideStore 续签还需要网络访问苹果服务。
3. 打开 SideStore，用与 iLoader 安装实验版时**同一 Apple 账号**登录。密码及验证码只应在应用内自行输入，不要提交到 GitHub 或聊天记录。
4. 在 SideStore 的 **My Apps** 中点击 SideStore 右侧天数，执行首次刷新。刷新自身时可能暂时返回桌面，随后重新打开。完整步骤见 [SideStore 官方安装说明](https://docs.sidestore.io/docs/installation/install)。

如果出现撤销或重新创建证书的提示，请先了解它可能影响同账号已签名的侧载应用，再决定如何处理；不要为了清理名额删除有重要数据的应用。更换 Apple 账号或应用标识可能造成重新安装、登录状态或本地数据变化。

### 2. 让 SideStore 管理现有实验版

1. 先备份重要聊天记录，**不要先卸载 FChat**。
2. 把自行准备的同一份诊断版 IPA 安全地传到 iPhone 的“文件”App。
3. 保持 Wi‑Fi 和 LocalDevVPN 连接，在 SideStore → **My Apps** 左上角点“＋”，选择该 IPA。
4. 核对应用标识和安装器提示，确认目标是独立的实验版，而非官方微信。SideStore 可能重新签名或改写标识；同名不一定代表是同一个应用，也不能保证保留数据。
5. 完成后确认 SideStore 的 My Apps 中出现 FChat，再打开 FChat 检查登录状态、聊天记录以及安卓端是否仍在线。本次测试中数据保留，但不代表其他环境一定如此。

SideStore 的 7 天计数是签名到期倒计时，不表示应用获得永久签名。它会尝试在后台刷新，但运行时机受系统、Wi‑Fi、VPN 和账号状态影响；请定期核对倒计时是否回升。官方说明见 [SideStore FAQ](https://docs.sidestore.io/docs/faq)。

### 3. 可选：快捷指令定时尝试刷新

1. iPhone 打开“快捷指令 → 自动化”，创建按**特定时间**每天运行的自动化。选择通常有 Wi‑Fi、手机近期已解锁的时间；若界面有“立即运行”，可按个人需要选择。
2. 添加 LocalDevVPN 的 **Enable LocalDevVPN** 动作，然后添加 SideStore 的 **Refresh All Apps** 动作。LocalDevVPN 的 Tunnel IP 和 Device IP 不必凭空填写：它们是可选项，留空时使用应用内配置。详见 [LocalDevVPN 源码](https://github.com/jkcoxson/LocalDevVPN/blob/main/LocalDevVPN/VPNShortcuts.swift)。
3. 先在连接 Wi‑Fi 且手机解锁的情况下手动运行一次，处理系统提示，检查错误；之后留意定时执行和 FChat 过期时间。**触发通知或手动执行成功都不等于锁屏定时续签成功。**

iOS 27.2 有用户报告设备长期锁屏时自动刷新失败，解锁手动运行又成功，详见 [SideStore issue #1723](https://github.com/SideStore/SideStore/issues/1723)。如果天数持续下降，应在到期前连接 Wi‑Fi 和 LocalDevVPN，进入 SideStore 手动刷新并排查；自动化不是永久可用的保证。

## 常见问题

### iLoader 提示 `Failed to list developer devices`

这表示它在向 Apple 开发者服务查询设备列表时请求失败，**不能仅凭外层错误判断是 IPA 损坏、账号问题还是网络问题**。保持 iPhone 解锁连接，稍后重试一次；如仍失败，可切换电脑网络后重试，并查看错误详情。相似的间歇性请求失败见 [iLoader issue #851](https://github.com/nab138/iloader/issues/851)。

### SideStore 登录出现 `-80045` 或 `-23782`

`-80045` 有公开的认证兼容性报告，部分用户通过切换 Anisette 配置解决，见 [SideStore issue #1675](https://github.com/SideStore/SideStore/issues/1675)。本次尝试的步骤是：SideStore 的 **Settings → User Customizations** 中关闭 `On-Device Anisette`；在 **Anisette Servers** 选择 `SideStore (New)` 并关闭自动轮换；在 **Anisette Client Configuration → Remote Server Sync** 点击 `Fetch` 和 `Save as Overrides`；返回自定义设置，点击 `Reset adi.pb` 后重试。它只是社区提供的临时方法，可能因版本和服务器变化而失效。

本次遇到 `-23782` 时，**Anisette Client Configuration** 的 Client Info 显示 macOS 10.12.6，低于提示要求的 10.13。随后在 **Interactive** 页将两个字段改为以下值，点 `Save Overrides`，完全关闭并重新打开 SideStore，然后成功登录。下列值是客户端标识字符串，不是 Apple 账号、密码或配对文件：

Client Info：

```text
<MacBookPro18,3> <macOS;26.6;25F84> <com.apple.AuthKit/1 (com.apple.akd/1.0)>
```

User Agent：

```text
AuthKit/1 (Macintosh; OS X 26.6) (com.apple.akd/1.0)
```

错误提示并不意味着用户一定需要实体 Mac；也不能单凭错误码断定同一个原因或保证这些值适用于所有账号。参考 [AltStore issue #1852](https://github.com/altstoreio/AltStore/issues/1852) 与 [SideStore issue #1606](https://github.com/SideStore/SideStore/issues/1606)。避免反复提交登录请求，切勿公开 Apple 账号密码、验证码或配对文件。

### 点开应用立即闪退

先区分普通签名到期、安装时的错误和应用启动崩溃。此次诊断包由完整插件去除三个底层函数钩子后在测试设备上能够启动；原始插件或其他组合可能仍会闪退。若要分析，可在 iPhone 的“设置 → 隐私与安全性 → 分析与改进 → 分析数据”查找对应崩溃记录。分享记录前移除设备标识、路径和其他个人数据。

### Bark 通道测试成功，但收不到微信通知

按顺序核对：

1. 安卓微信是否在线、新消息是否真正产生系统通知；当前聊天正在打开时，可能不产生预期通知。
2. 短信转发器的通知使用权、转发应用通知总开关、微信包名匹配规则和 Bark 发送通道是否都已启用。
3. 转发日志“应用”是否出现该消息，发送结果是什么。
4. Bark 通道的测试是否送达；如果显示 `Decryption Failed`，检查两端加密配置。
5. 仅锁屏时失败或打开转发器后才收到时，检查安卓后台限制和锁屏网络，做上一节的分段测试。

### 部分小程序顶部按钮过大

本次实验中有小程序的关闭按钮明显放大，有的则正常。设备信息伪装可能影响布局，但因果关系尚未验证。可在官方微信中打开同一个页面对照；涉及敏感账户时优先使用官方客户端或已核实的官方网站。不要为排查而直接删除实验版，以免丢失本地数据。

## 项目来源

- [Apple Developer 个人团队及签名限制](https://developer.apple.com/help/account/basics/about-your-developer-account)
- [iLoader](https://github.com/nab138/iloader) · [SideStore 文档](https://docs.sidestore.io/) · [LocalDevVPN](https://github.com/jkcoxson/LocalDevVPN)
- [Bark](https://github.com/Finb/Bark) · [SmsForwarder](https://github.com/pppscn/SmsForwarder)
- [FChat 上游发布页](https://github.com/Taosky/unsigned-ipa-cn/releases/tag/fchat) · [wechat-ipad-login](https://github.com/cjq6525/wechat-ipad-login) · [splice](https://github.com/franklintra/splice)

本文是个人实验记录，不代表腾讯、苹果或上述项目的官方支持。项目和接口可能变更，请以各上游当前文档为准。
