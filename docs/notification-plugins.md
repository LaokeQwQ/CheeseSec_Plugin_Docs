# 通知提供商包契约（规划）

本页说明通知提供商包（notifier provider pack）的边界。先说结论：它是纯契约，只描述
CheeseWAF 核心通知器如何把告警投递到某个目的地。它不可安装、不可执行，也不给插件任何
网络出口。当前 CRP v1 和规划中的 v1.1 sidecar 都不支持通知 egress。

## 和 sidecar 的区别

| 维度 | v1/v1.1 sidecar descriptor | notifier provider pack |
|---|---|---|
| 执行体 | 异步 sidecar，运行可执行代码 | 没有可执行文件、镜像、WASM 或进程内模块 |
| 能力 | `observe`、`candidate_snapshot`、`hint`、`health` | `alert_delivery`、`test_delivery`，只是契约标签 |
| 网络 | `egress` 固定为 `deny`，联网必须走短租约（当前未开放） | 没有网络栈，目标由 core notifier 解析 |
| 凭据 | 插件不持有 | `secret_fields` 只写引用名，值在核心 |
| 安装 | 由 CWEDP/CRP 流程处理（尚未上线） | `installable=false`，不能进入 CRP |
| 格式 | CRP manifest 加 sidecar descriptor | 独立 JSON 契约 `crp.cheesewaf.io/notifier/v1` |

v1.1 仍是在 sidecar 能力上做扩展的规划版本，没有 `notify` 权限。看到 provider pack 时，
不要推断「插件可以发通知」。在当前契约里，能发通知的只有 CheeseWAF 核心。

## 为什么由核心发送

通知会向外部发起网络请求。目标地址、重定向、私网访问、超时、重试、凭据使用和审计都必须
由同一层控制，否则插件可以绕过核心的 SSRF 与私网策略。

- 插件拿不到宿主凭据，也不需要网络栈；provider pack 只提供字段形状。
- 投递必须以异步方式执行，不能阻塞 WAF 请求线程。
- 离线模式仍然零网络请求；通知不会在离线时自行重试。
- 失败、超时和重试必须由核心写入审计；pack 本身不携带重试逻辑。

## 契约字段

`schema/extensions-v1/notifier-provider.schema.json` 使用
`additionalProperties: false`，字符串、数组和模板大小都有上限。

| 字段 | 规则 |
|---|---|
| `api_version` | 固定为 `crp.cheesewaf.io/notifier/v1` |
| `provider_id` | 1 到 128 个字符，以字母或数字开头 |
| `type` | 只能取下文列出的六种类型 |
| `version` | SemVer 文本 |
| `namespace` | `official/<plugin>`、`enterprise/<org>/<plugin>` 或其他受支持类别 |
| `source`、`source_root` | 来源标识，最长 128 个字符，不允许 `..` |
| `config_schema.dialect` | 固定为 `cheesewaf-notifier-config/v1` |
| `config_schema.fields` | 最多 24 个字段；每项包含 `name`、`kind`、`required`，可选 `max_length`（不超过 2048） |
| `secret_fields` | 最多 16 个引用名，必须以 `_ref` 结尾；只写引用，不允许出现凭据值 |
| `endpoint_templates` | 最多 4 个模板；每个包含 `name`、`url_template`、`method`、`egress_owner`、`variables` |
| `capabilities` | 1 到 2 项，只能取 `alert_delivery`、`test_delivery` |
| `publication` | 固定为 `status=planned`、`installable=false`、`crp_binding=descriptor-only` |

`endpoint_templates` 的约束：

- `url_template` 必须以 `https://` 开头，长度不超过 512 个字符。
- `method` 固定为 `POST`，`egress_owner` 固定为 `cheesewaf-core`。
- 模板变量写成 `{name}`，名字必须已在 `config_schema.fields` 或 `secret_fields` 中声明。
- 模板里不允许写 Token、密钥或其他凭据值，也不允许出现 32 个字符以上的连续字母或
  数字，避免把高熵值直接塞进 URL。
- `email` 类型可以声明空的 `endpoint_templates`，由核心邮件通道处理；其他类型必须有一个
  `notify` 模板。

## 允许的类型

| 类型 | 用途 |
|---|---|
| `webhook` | 通用 JSON webhook |
| `dingtalk` | 钉钉群机器人 |
| `feishu` | 飞书自定义机器人 |
| `wecom` | 企业微信群机器人 |
| `telegram` | Telegram Bot API |
| `email` | 核心邮件通道 |

类型只是契约分类，不代表 provider pack 已经可以加载。发布仓库不提供 pack 的运行时加载器；
具体投递适配由 CheeseWAF 核心维护，是否可用以核心的阶段验收为准。

## 示例

`examples/extensions/notifier-provider.json` 是 Feishu 的契约样例。它固定了机器人地址模板
和 `webhook_ref` 字段名，但没有凭据值，也没有可执行内容。

这个示例只用于校验字段和边界。它不是可安装包，不会被 CRP 解析，也不表示该 pack 已经可以
加载或发布。

## 自动检查

发布仓库的 `scripts/validate_notifier_contracts.py` 会检查：

- schema、策略和示例能被严格解析，没有重复键；
- 示例满足 schema，`publication` 固定为 planned 且不可安装；
- 类型、能力、字段名和模板变量都在允许范围内；
- 模板使用 HTTPS，出口归核心所有；
- 策略没有授予运行时能力、出站能力或可执行权限。

这些检查只证明契约字段和边界一致，不证明投递、凭据存储、重试或审计已经实现。

## 当前限制与后续工作

- provider pack 没有 CRP 绑定，不能进入安装、升级或回滚流程。
- 没有 catalog 或 OTA 条目；发布索引仍然为空。
- schema 按 `store.cheesesec.com/schema/extensions/v1/` 的公开地址登记，实际部署状态以
  商店发布记录为准。
- 要让 provider pack 真正生效，还需要核心加载器、秘密引用解析、模板变量替换、投递审计
  事件、重试与 SSRF 测试，以及管理员配置界面。
- 如果以后要让插件参与通知，必须先设计新的能力、权限和审计模型；当前 v1/v1.1 不支持，
  不能提前写成已支持。

## 相关页面

- [CRP 开发手册](crp-development.md)
- [商店与 OTA 契约](store-ota.md)
- [DuckDB 扩展契约](duckdb-extension.md)
