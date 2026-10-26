# 通知提供商包契约

本页说明通知提供商包（notifier provider pack）的边界。先说结论：它是纯声明式描述文件，
只描述 CheeseWAF 核心通知器如何把告警投递到某个目的地。核心从本地插件索引加载它，但
pack 仍然没有可执行体、没有网络栈、拿不到凭据，也不能进入 CRP 安装流程。能发通知的
只有 CheeseWAF 核心。

## 和 sidecar 的区别

| 维度 | v1/v1.1 sidecar descriptor | notifier provider pack |
|---|---|---|
| 执行体 | 异步 sidecar，运行可执行代码 | 没有可执行文件、镜像、WASM 或进程内模块 |
| 能力 | `observe`、`candidate_snapshot`、`hint`、`health` | `alert_delivery`、`test_delivery`，只是契约标签 |
| 网络 | `egress` 固定为 `deny`，联网必须走短租约（当前未开放） | 没有网络栈，目标由 core notifier 解析 |
| 凭据 | 插件不持有 | `secret_fields` 只写引用名，值在核心 |
| 安装 | 由 CWEDP/CRP 流程处理（尚未上线） | 由核心从本地插件索引读取描述文件；不可执行，不能进入 CRP |
| 格式 | CRP manifest 加 sidecar descriptor | 独立 JSON 契约 `crp.cheesewaf.io/notifier/v1` |

v1.1 仍是在 sidecar 能力上做扩展的规划版本，没有 `notify` 权限。看到 provider pack 时，
不要推断「插件可以发通知」或「插件获得执行权」。pack 由核心加载，投递仍由核心完成。

## 加载方式

- 核心扫描 `plugins.index_dir`（相对路径按数据目录解析，默认 `<data-dir>/plugins`），
  读取目录下的 `*.json`。目录不存在时不报错，服务照常启动。
- `plugins.watch_interval` 控制目录指纹的轮询间隔（默认 2s，最小 100ms，最大 1h）。
  文件新增、删除或修改后，核心重建索引并原子替换，不需要重启。
- 单个文件损坏只影响该条目：它会被记录并跳过，其余文件继续加载。
- 宿主版本不满足 `host_compatibility` 的 pack 不会被注册，原因会写入日志。
- pack 不能覆盖六种内置类型：同一个配置项在有无某个 pack 时不能产生不同语义。

## 为什么由核心发送

通知会向外部发起网络请求。目标地址、重定向、私网访问、超时、重试、凭据使用和审计都必须
由同一层控制，否则插件可以绕过核心的 SSRF 与私网策略。

- 插件拿不到宿主凭据，也不需要网络栈；provider pack 只提供字段形状。
- 投递必须以异步方式执行，不能阻塞 WAF 请求线程。
- 离线模式仍然零网络请求；通知不会在离线时自行重试。
- 失败、超时和重试必须由核心写入审计；pack 本身不携带重试逻辑。

## 契约字段

`schema/extensions-v1/notifier-provider.schema.json` 使用
`additionalProperties: false`，字符串、数组和模板大小都有上限。含可执行内容
（`executable`、`entrypoint`、`artifact`、`command`、`wasm` 等）或自行声明出口
（`egress`、`egress_hosts` 等）的字段会被按名拒绝，而不是被忽略。

| 字段 | 规则 |
|---|---|
| `api_version` | 固定为 `crp.cheesewaf.io/notifier/v1` |
| `provider_id` | 1 到 128 个字符，以字母或数字开头 |
| `type` | 必须是新类型；六种内置类型由核心实现，pack 不可声明 |
| `version` | SemVer 文本 |
| `host_compatibility` | 可选，宿主版本闭区间 `min`/`max`；点数版本，预发布后缀不参与比较，空边界表示不限 |
| `namespace` | `official/<plugin>`、`enterprise/<org>/<plugin>` 或其他受支持类别 |
| `source`、`source_root` | 来源标识，最长 128 个字符，不允许 `..` |
| `config_schema.dialect` | 固定为 `cheesewaf-notifier-config/v1` |
| `config_schema.fields` | 最多 24 个字段；每项包含 `name`、`kind`、`required`，可选 `max_length`（不超过 2048） |
| `secret_fields` | 最多 16 个引用名，必须以 `_ref` 结尾；只写引用，不允许出现凭据值 |
| `endpoint_templates` | 最多 4 个模板；每个包含 `name`、`url_template`、`method`、`egress_owner`、`variables` |
| `capabilities` | 1 到 2 项，只能取 `alert_delivery`、`test_delivery` |
| `publication` | 固定为 `status=loadable`、`installable=false`、`crp_binding=descriptor-only` |

`endpoint_templates` 的约束：

- `url_template` 必须以 `https://` 开头，长度不超过 512 个字符。
- `method` 固定为 `POST`，`egress_owner` 固定为 `cheesewaf-core`。
- 模板变量写成 `{name}`，名字必须已在 `config_schema.fields` 或 `secret_fields` 中声明。
- 渲染后的 URL 必须仍指向模板里的同一个 host，防止变量值改写目标。
- 模板里不允许写 Token、密钥或其他凭据值，也不允许出现 32 个字符以上的连续字母或
  数字，避免把高熵值直接塞进 URL。
- `secret_fields` 只作为引用名存在；核心把凭据放在请求头里注入，不拼进 URL。

## 内置类型与 pack 类型

| 内置类型 | 用途 |
|---|---|
| `webhook` | 通用 JSON webhook |
| `dingtalk` | 钉钉群机器人 |
| `feishu` | 飞书自定义机器人 |
| `wecom` | 企业微信群机器人 |
| `telegram` | Telegram Bot API |
| `email` | 核心邮件通道 |

这六种是编译进核心的实现，pack 不能声明也不能替换它们。需要新的目的地时，pack 声明一个
新的 `type`，核心从索引里解析并在配置里按该类型使用。

## 示例

`examples/extensions/notifier-provider.json` 是一个 `teams_webhook` 类型的契约样例。它固定了
通知地址模板和 `webhook_ref` 引用名，声明了 `host_compatibility`，但没有凭据值，也没有
可执行内容。

这个示例只用于校验字段和边界。它不是可安装包，不会被 CRP 解析。

## 自动检查

发布仓库的 `scripts/validate_notifier_contracts.py` 会检查：

- schema、示例能被严格解析，没有重复键；
- 示例满足 schema，`publication` 固定为 loadable、不可安装、仅描述符绑定；
- `type` 不是六种内置类型之一；
- `host_compatibility` 边界是点数版本；
- 模板使用 HTTPS，出口归核心所有；
- `secret_fields` 合规，模板不含高熵值；
- 文件里没有可执行或自行声明出口的字段。

这些检查只证明契约字段和边界一致，不证明投递、凭据存储、重试或审计已经实现。

## 当前限制与后续工作

- pack 没有 CRP 绑定，不能进入安装、升级或回滚流程。
- 没有 catalog 或 OTA 条目；发布索引仍然为空。
- 秘密引用解析、投递审计事件、重试与 SSRF 的系统性测试、管理员配置界面仍待补齐。
- 如果以后要让插件参与通知，必须先设计新的能力、权限和审计模型；当前 v1/v1.1 不支持，
  不能提前写成已支持。

## 相关页面

- [CRP 开发手册](crp-development.md)
- [商店与 OTA 契约](store-ota.md)
- [DuckDB 扩展契约](duckdb-extension.md)
