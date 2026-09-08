# CRP 开发手册（契约版）

本文把当前 CheeseWAF 代码能执行的 CRP v1 格式，和后续规划的扩展格式分开说明。
没有对应的测试和阶段记录时，不要把规划内容写进 v1 包，也不要按规划内容验收当前安装流程。

## 当前 v1 的可执行格式

`CheeseWAF/internal/crp.ParseArchive` 当前只接受 ZIP 归档中的三类条目：

| 路径 | 要求 |
|---|---|
| `manifest.json` | 只能有一个，使用严格 JSON |
| `artifact/<file>` | 只能有一个普通文件，文件名可由 manifest 的 `artifact.name` 约束 |
| `signatures/manifest.json` | 只能有一个 JSON 数组 |

解析器会拒绝未知条目、`provenance/`、目录、符号链接、重复路径、路径穿越和超出大小限制的条目。
`provenance/` 不属于当前 v1；需要来源证明、SBOM 或构建记录时，应使用单独的外部证据，或等待 v2 契约。

### v1 Manifest 字段

Manifest 使用 `crp.cheesewaf.io/v1`。当前解析器允许的字段如下：

| 字段 | 规则 |
|---|---|
| `api_version` | 可选；填写时必须是 `crp.cheesewaf.io/v1` |
| `kind` | 可选；填写时必须是 `CheeseWAFResourcePackage` |
| `name`、`plugin_id` | 至少填写一个；两者都填时应指向同一插件 |
| `version` | 必填的 SemVer 文本 |
| `namespace` | 必须符合 `official/<plugin>`、`enterprise/<org>/<plugin>` 或其他受支持类别格式 |
| `publisher` | 可选发布者标识 |
| `source` | 可选语法字段；调用 `Import` 时必须命中 `SourceRegistry` 的来源白名单 |
| `source_root` | 必填的稳定来源根标识 |
| `release_sequence` | 数字；首次包可以是 `0`，已有非零序号时不能用 `0` 覆盖 |
| `digests` | 可放在顶层，或放在 `artifact.digests`；两处同时出现时必须完全一致 |
| `artifact` | 可选对象；存在时校验其中的 `name`、`size` 和 `digests`；摘要也可使用顶层 `digests` |
| `artifact.name` | 可选文件名约束 |
| `artifact.size` | 可选大小；归档解析时必须与实际大小一致 |
| `artifact.digests` | MD5、SHA-1、SHA-256 三个小写十六进制摘要 |

MD5 与 SHA-1 只用于传输完整性和断点续传。SHA-256 是内容身份。摘要缺失或不匹配时必须拒绝，管理员确认不能绕过。

`signatures/manifest.json` 的元素使用当前 `Signature` 字段：`key_id`、`algorithm`、`value` 和可选的 `signed_at`。示例中的空数组只用于验证归档布局，不表示签名通过；真正的 `Import` 仍需要满足信任根和阈值签名策略。

最小、可解析但不具备安装授权的示例见 [`examples/crp-v1/`](../examples/crp-v1/)。

## 命名空间和签名

- 官方：`official/<plugin>`；
- 企业：`enterprise/<org>/<plugin>`；
- 其他类别：`<class>/<publisher>/<plugin>`。

来源根、签名者和传输来源分别验证。官方和企业普通发布采用 2-of-3，
严重操作采用 3-of-5；企业使用独立根，阈值不能低于平台最低值。社区、
个人、测试和开发密钥分别受 1 年、1 年、30 天和 7 天有效期限制，并默认
需要管理员确认。

未知来源、未知 key、吊销 key、过期 key、错误签名和未达到阈值时，当前 v1
一律拒绝。已登记的社区、个人、测试、开发或不可信根会返回
`needs_confirmation`；上层 UI/CLI 如允许继续，必须先显示风险告警并等待
10 秒，再完成密码、二次和三次确认，最后写入审计。

## 运行和发布

插件使用 sidecar 和异步接口，不阻塞 WAF 请求线程。默认拒绝外部出站；
联网必须通过短时 Socket Lease。发布顺序为：

`build → test → sign → publish → observe → staged → canary → promote`。

回滚生成新的控制面 revision，不重放旧包。安装、OTA、CWEDP 和热载在
CheeseWAF 阶段看板有独立证据前，不得写成已交付能力。

## v2 和扩展规划

以下内容不属于当前 v1 Manifest，也不能出现在当前 Get Started 示例中：

- `package_id`、`class`、目标 CheeseWAF/扩展 API、平台/架构、最低审计事件版本和权限声明；
- `provenance/` 目录，以及 SBOM、构建记录和发布者声明；
- DuckDB 扩展专用字段、宿主版本矩阵和分析数据约束。

这些字段和目录需要新的 schema、解析器、签名覆盖范围、迁移说明和回归测试。完成这些工作前，
它们只能写在标为「规划」的 v2 或 DuckDB 契约中。
