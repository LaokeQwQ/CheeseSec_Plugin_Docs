# Cloudflare 边缘路由契约（v1）

本文固定 CheeseSec 公开读取面与 CheeseWAF 服务器之间的分工。它是发布元数据和路由的契约，不代表生产域名、R2 桶、Cloudflare Tunnel 或 Access 策略已经配置完成。

## 请求分工

以下三个域名只提供公开读取。它们只接受 `GET` 和 `HEAD`，不接收插件凭证，不把未知路径转发到服务器。

| 域名 | 允许的路径 | R2 对象前缀 | 缓存类别 |
|---|---|---|---|
| `store.cheesesec.com` | `/v1/catalog/index.json`、`/v1/policy/*.json`、`/v1/schema/{store,crp}/*.schema.json` | `catalog/`、`policy/`、`schema/` | 短时重新验证 |
| `ota.cheesesec.com` | `/v1/channels/{stable,canary,dev}/index.json` | `ota/channels/` | 短时重新验证 |
| `res.cheesesec.com` | `/sha256/{64 位小写 SHA-256}/{文件名}` | `resources/sha256/` | 长期不可变 |

Worker 只按固定的 Host、路径和对象键读取 R2。未知 Host 返回 `421`，已知公开 Host 的未知路径返回 `404`，不产生重定向。公开端点收到 `POST`、`PUT`、`PATCH`、`DELETE` 或 `OPTIONS` 时返回 `405`，并带有 `Allow: GET, HEAD`。

`res.cheesesec.com` 支持单个字节范围请求。Worker 传递合法的 `Range`，返回 `206` 或 `416`，不会把整个 CRP 读入内存，也不会在边缘重新计算大文件摘要。

## 服务器请求

以下请求固定回到 `origin-admin.cheesesec.com`：

- `console.cheesesec.com` 的控制台页面、登录、初始化和静态控制台资源。
- `api.cheesesec.com` 的 `/api/...`、`/health/ready`、`/health/cluster` 和其它已登记管理接口。
- 认证、Session、CSRF、RBAC、审批、CRP 导入与激活、CWEDP 协商、诊断上传、SSE 和 WebSocket。

Worker 只能使用配置中的 `ORIGIN_BASE_URL` 生成上游地址。它会删除客户端提交的 `X-Forwarded-*`、`X-CheeseSec-Edge-*`、`CF-Access-*` 和逐跳请求头，再加入请求 ID、UTC 时间戳、策略版本和 HMAC 信封。Cloudflare Access 服务身份只从 Worker Secret 注入。HMAC 通过后，服务器仍必须执行原有的 Session、CSRF、RBAC 和审计检查。

服务器的 `admin_listen` 继续监听 loopback，`admin_public` 保持 `false`。Tunnel 只把 `origin-admin.cheesesec.com` 映射到 `https://127.0.0.1:9443`，不能指向公开数据面端口或公网 IP。

## 发布对象与指针

发布仓库生成版本化对象，Worker 只读取当前指针：

```text
indexes/catalog/seq-<20 位十进制>.json
indexes/ota/<channel>/seq-<20 位十进制>.json
indexes/policy/seq-<20 位十进制>/<name>.json
resources/sha256/<sha256>/<filename>
pointers/catalog.json
pointers/ota/<channel>.json
```

对外映射使用下列固定键：

```text
catalog/index.json
policy/endpoints.json
policy/trust-roots.json
policy/source-registry.json
policy/revocations.json
schema/store-v1/<name>.schema.json
schema/crp-v1/<name>.schema.json
ota/channels/<channel>/index.json
```

索引序号只能递增。旧索引、旧资源和撤回事件不能覆盖或删除。Worker 返回 `ETag`、可用的 `Last-Modified`、`X-CheeseSec-Index-Sequence` 和对应的 `Cache-Control`。它不验证或重签 CRP，签名阈值、来源根、吊销、防降级和激活仍由 CheeseWAF 负责。

## 配置和上线条件

Worker 的 R2 绑定名称固定为 `PUBLICATION_INDEX` 和 `PUBLIC_RESOURCES`。`EDGE_POLICY_VERSION` 与 `ORIGIN_BASE_URL` 可以作为非敏感变量；`EDGE_ORIGIN_HMAC`、`CF_ACCESS_CLIENT_ID` 和 `CF_ACCESS_CLIENT_SECRET` 必须使用 Wrangler Secret。生产仓库不得提交 `.dev.vars`、Tunnel Token、Access 凭据、服务 Token 或签名私钥。

上线前必须分别证明以下结果：

1. Pages 静态构建、TypeScript、单元测试和产物边界检查通过。
2. R2 staging 桶包含已签名的目录、策略、schema、OTA 索引和内容寻址资源。
3. Tunnel、Access ACL、Origin HMAC 和 loopback 管理端口检查通过。
4. 公开端点的 `404`、`405`、`421`、条件请求、范围请求和无重定向检查通过。
5. 服务器的 `/health/ready`、认证、审批、审计、SSE 和 WebSocket 检查通过。

在这些证据齐全前，商店、OTA 和资源域名只能按契约示例描述，不能写成已经上线的服务。
