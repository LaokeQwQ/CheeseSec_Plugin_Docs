# CRP 开发手册（契约版）

## 包结构

CRP 是可离线验证的 `.crp` 包，至少包含 `manifest.json`、`artifact/`、
`signatures/` 和 `provenance/`。Manifest 使用 `crp.cheesewaf.io/v1`，并
声明插件标识、SemVer、namespace、source root、发布序号、大小和三种摘要。

MD5 与 SHA-1 只用于传输完整性和断点续传；SHA-256 用作内容身份。摘要
缺失或不匹配时必须拒绝，管理员确认不能绕过。

## 命名空间和签名

- 官方：`official/<plugin>`；
- 企业：`enterprise/<org>/<plugin>`；
- 其他类别：`<class>/<publisher>/<plugin>`。

来源根、签名者和传输来源分别验证。官方和企业普通发布采用 2-of-3，
严重操作采用 3-of-5；企业使用独立根，阈值不能低于平台最低值。社区、
个人、测试和开发密钥分别受 1 年、1 年、30 天和 7 天有效期限制，并默认
需要管理员确认。

未知、社区、个人、测试或不可信签名不能自动获得高权限。允许继续时，系统先显示
风险告警并等待 10 秒，再完成密码、二次和三次确认；所有结果写入审计。

## 运行和发布

插件使用 sidecar 和异步接口，不阻塞 WAF 请求线程。默认拒绝外部出站；
联网必须通过短时 Socket Lease。发布顺序为：

`build → test → sign → publish → observe → staged → canary → promote`。

回滚生成新的控制面 revision，不重放旧包。安装、OTA、CWEDP 和热载在
CheeseWAF 阶段看板有独立证据前，不得写成已交付能力。
