# 商店与 OTA 契约（v1，契约版）

本文是 CheeseSec 商店、OTA、资源端点和插件运行边界的双语手册。它描述可验收的发布元数据契约，不表示线上服务或安装器已经部署。发布仓库中的机器可读 schema 位于 CheeseSec_Plugin/schema/store-v1/，公开镜像使用 https://store.cheesesec.com/schema/store/v1/。Pages、Worker、R2 和服务器的分工见 [Cloudflare 边缘路由契约](cloudflare-routing.md)。

## 三个固定端点

| 端点 | 角色 | 方法 | 关键约束 |
|---|---|---|---|
| https://store.cheesesec.com | 目录 | GET、HEAD | 只发布审核通过的 release 摘要 |
| https://ota.cheesesec.com | 版本索引 | GET、HEAD | pull-only，索引序号单调递增 |
| https://res.cheesesec.com | 不可变资源 | GET、HEAD | URL 必须绑定 SHA-256 内容地址，禁止重定向 |

端点不接收插件凭证。在线拉取需要管理员密码确认、一次性 Socket Lease 和审计；离线模式网络请求数必须为 0。

## 边缘与服务器分工

目录、策略、schema、OTA 索引和内容寻址资源属于公开读取面。Worker 只接受 `GET`、`HEAD`，按固定路径读取 R2；未知 Host 返回 `421`，未知路径返回 `404`，不把请求转发到服务器。

控制台、管理 API、认证、初始化、审批、CRP 激活、CWEDP、诊断上传、SSE 和 WebSocket 属于服务器请求。Worker 只回源到固定的 `ORIGIN_BASE_URL`，并加入 Cloudflare Access 身份与 Origin HMAC。服务器仍执行 Session、CSRF、RBAC 和审计检查，`admin_listen` 继续监听 loopback。

对象键、缓存类别、请求头和上线检查的完整约束见 [Cloudflare 边缘路由契约](cloudflare-routing.md) 与 [英文版本](cloudflare-routing.en.md)。

## 信任级别

支持 official、enterprise、community、personal、test 和 development 六类命名空间。信任级别只表达来源，不授予运行能力：能力仍由 sidecar descriptor、资源限制、审批和策略决定。

- 官方与认证企业普通发布采用 2-of-3，高风险发布采用 3-of-5；企业根只能签 enterprise/<org>/<plugin>。
- 社区、个人、测试、开发默认需要管理员确认；密钥最长有效期分别为 365、365、30、7 天。
- 官方与企业密钥最长有效期为 1095 天。密钥轮换和吊销必须保留旧记录，不能覆盖发布历史。

## 不可变 release 与撤回

每条 release 绑定 namespace@version#release_sequence、CRP 三种摘要、manifest/签名集合/descriptor/provenance 摘要、来源根、审核证据和签名验证报告。已发布记录只能追加，不能重写、降序或被镜像改写。撤回通过带理由和证据摘要的追加事件完成；OTA 索引不得继续引用已撤回 release。

## 离线导入

离线导入需要本地 .crp、信任根、来源注册表和吊销快照。顺序是：检查 CRP 三条目布局、验证 manifest/schema、核对 artifact 大小与 MD5/SHA-1/SHA-256、绑定来源根、验证签名阈值和有效期、检查吊销与发布序号、在需要时取得管理员确认。任何失败都拒绝安装和激活；只有全部门禁通过后才能交给 CheeseWAF staged 流程。吊销快照过期时保留 last-known-good，但暂停新的安装、升级和晋级。

## 34A sidecar 与 CWEDP

插件必须由异步 sidecar 执行，首个运行模式为 observe，默认 egress=deny，只能产生快照、hint 和健康状态；请求线程不得等待插件 I/O。WASM 和进程内原生插件不在契约内。

安装、升级、回滚和集群分发统一由 CWEDP pull-only 完成。HELLO/CAPABILITIES/DistributionIntent 协商后，可从 OTA、授权 seed、授权 peer 或离线 CRP 拉取；Ansible 只负责分发代理 bootstrap，不能推送或替换 CRP。传输必须保留三种摘要、签名 manifest、内容寻址分块和来源隔离/隔离记录。

这些页面中的命令和字段是契约示例。CheeseWAF 阶段验收没有独立证据前，不得把商店、OTA、CWEDP 或插件激活描述为已上线能力。
