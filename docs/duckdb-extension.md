# DuckDB 分析扩展契约（规划）

本文对应主计划 32C、33B、34A+，规定可选分析扩展的交付边界和验收门禁。没有 CheeseWAF 阶段看板的可执行证据时，不得把任何能力写成已上线。

## 边界和默认值

- DuckDB 扩展采用 `host-provided` 的异步 `one-shot-job` 契约：宿主提供受控版本的 DuckDB，每个任务结束后退出。它不是常驻 sidecar，也不是供用户直接执行任意 SQL 的 CLI。当前只有 schema、descriptor、策略和 fixture；CheeseWAF 尚未接入作业启动器或审计导出器，也不随默认发行物提供。
- 不进入请求热路径，不写 PG、native-raft 或 Redis，不读取正在写入的共享 DuckDB 文件，也不提供常驻监听端口或远程数据库服务。
- 任务只读取受信导出器生成的脱敏 Parquet 快照，并使用仓库登记的参数化查询模板；不得执行用户提供的任意 SQL。输入验签、文件摘要与 schema 校验、OS 沙箱和资源监督都必须由宿主在启动 DuckDB 前后落实，目前尚无运行时证据。
- 唯一输出是 `analysis-record/v1`。`contain`、`isolate` 等 recommendation 只是分析标签，不能转换成 `risk-hint/v1`、候选策略、ACL、挑战、封禁或策略更新。
- DuckDB 任务禁止网络出站，不申请 Socket Lease，也不访问在线目录或资源服务。

## CRP v1 边界

当前 CheeseWAF 只执行 CRP v1 的三条目归档：`manifest.json`、一个
`artifact/<file>` 普通文件和 `signatures/manifest.json`。解析器会拒绝
未知条目、目录、符号链接、重复路径、路径穿越和大小超限。`provenance/`
不属于 v1，因此不能放进当前 Get Started 示例或当前 `.crp` 包。

v1 Manifest 只使用 CheeseWAF 当前解析器允许的字段：`api_version`、`kind`、
`name`、`plugin_id`、`version`、`namespace`、`publisher`、`source`、
`source_root`、`release_sequence`、`digests` 和 `artifact`（含可选的
`name`、`size`、`digests`）。解析器拒绝未知字段。三种摘要必须存在且匹配；
SHA-256 是内容身份，MD5/SHA-1 只用于传输完整性和断点续传。

最小的 v1 归档示例见 [`../examples/crp-v1/`](../examples/crp-v1/)。它包含两份可验证的官方 Ed25519 签名，可用于检查归档布局和签名门禁；它仍是契约样例，不代表插件运行时已接线，也不证明安装或激活流程可用。

## v2 和运行时边界

`package_id`、`class`、目标 CheeseWAF/扩展 API、平台/架构、最低审计事件版本、
权限声明和 `provenance/` 目录属于后续 v2 规划，不是当前 CRP v1 字段。DuckDB
扩展的 `one-shot-job` descriptor 和 `analysis-record/v1` schema 已在本仓库定义，
但 CheeseWAF 尚未接入执行运行时。SBOM、构建记录和正式宿主版本矩阵仍需新的 schema、
签名覆盖范围、迁移说明和回归测试。

扩展包不得携带 DuckDB 可执行文件、动态库、容器镜像、监听服务或生产密钥；
DuckDB 由宿主单独提供并登记版本。当前 CRP v1 解析器只校验归档结构和载荷摘要，
不会检查任意载荷的文件类型，因此该限制仍须由扩展发布门禁落实。

## 离线与在线安装

目标离线安装流程会从受信介质导入 .crp 与撤销快照，校验摘要、source root、签名阈值、信任根、兼容矩阵和审计策略后显示变更清单并确认；导入只写暂存区，验证成功才生成新控制面 revision，失败清理暂存内容。当前 CheeseWAF 仅提供本地 RuntimeStore contract，尚未接入这套控制面流程。独立 `cheesewaf-control` 的当前命令和启动边界见[独立控制面运行时文档](https://docs.cheesesec.com/zh/docs/cheesewaf/control-plane-runtime/)，该入口不提供插件安装或激活。撤销信息陈旧必须记录时间和风险；高风险或过期状态保持 pending，不能强制激活。

目标在线安装流程只从目录获取元数据、从不可变资源获取包，并绑定本地摘要；OTA 只能提出候选 revision，不能直接加载。下载使用短租约、限速和可恢复分片，完成后执行同样的全量验证。目录或镜像不得改变包身份、来源根、发布序号或权限。安装、升级、回滚保留摘要、操作者、确认、来源、审计事件和结果；回滚通过新 revision 指向已验证旧版本，不重放旧提交。当前二进制尚未接入目录、OTA、租约或控制面执行器；独立 `cheesewaf-control` 入口也不提供安装或激活接口。

## 签名根和轮换

在 v1 发布门禁中，官方与企业普通发布至少 2-of-3，严重操作至少 3-of-5；企业根独立且不能降低平台最低阈值。社区、个人、测试、开发根默认需管理员确认，密钥有效期上限分别为 1 年、1 年、30 天、7 天；官方/企业签名密钥上限为 3 年。签名条目必须携带 source root、trust level、release sequence、manifest 摘要和有效期，根公钥、用途和撤销状态由离线 trust-roots/revocations 输入提供。

根轮换是 v2/扩展规划：采用新旧根交叉签名窗口，先发布旧根签名的新信任元数据，再在窗口内接受新根签名包，最后撤销旧根；不得覆盖原根记录。离线站点通过签名根更新包和管理员确认导入；无法证明连续性时保持旧根并拒绝新包。撤销、紧急停发和泄露处置写入审计，并支持按规划中的 package_id、source root 和 key ID 精确阻断。

## 兼容矩阵和审计限制

| 维度 | 门禁 |
|---|---|
| CheeseWAF | 版本/提交范围；不兼容则拒绝暂存 |
| 扩展 API | duckdb-analysis/v1 等协议版本；只允许声明能力 |
| DuckDB | 宿主提供的版本范围；CRP 不携带二进制 |
| 平台 | OS、架构、运行时 ABI；未登记组合不得激活 |
| 数据 | Parquet schema、审计事件版本、时区和压缩约束 |
| 安全 | 能力、禁止出站、OS 沙箱、审计字段、回滚级别 |

扩展只能读取已验签、已校验的脱敏 Parquet 快照，不得读取原始请求体、Cookie、Authorization、Token、密钥、管理员会话或 PG/Redis/native-raft。查询必须使用固定模板，并受输入大小、时间、CPU、内存、临时空间和结果大小限制；OS 沙箱负责隔离文件、网络和进程资源。结果只能是带来源信息的 append-only `analysis-record/v1`，不能修改事实日志。分析标签、告警和风险排序不能放宽协议、安全底线、管理员硬规则或核心控制。

## 验收状态

本文件及英文对照描述的是扩展契约，不代表 DuckDB 作业运行时、审计导出器、安装器、OTA、CWEDP 拉取或热加载已经实现、发布或支持。当前门禁只验证 schema、descriptor、fixture 和静态契约，不证明输入签名、Parquet 内容、SQL 模板或 OS 沙箱已在运行时得到强制。接入前必须补齐这些运行时门禁、资源限制与隔离测试，并由 CheeseWAF 阶段看板单独记录。
