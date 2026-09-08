# CheeseSec Plugin 手册索引

## 读者入口

- CRP 开发手册：crp-development.md
- CRP Development Handbook：crp-development.en.md
- DuckDB 扩展契约：duckdb-extension.md
- DuckDB Extension Contract：duckdb-extension.en.md
- CRP v1 最小示例：../examples/crp-v1/README.md
- Minimal CRP v1 example：../examples/crp-v1/README.en.md
- 商店与 OTA 契约：store-ota.md
- Store and OTA contract：store-ota.en.md

## 文档状态

本文档仓库维护开发、签名、审批、发布、离线交付和运维约束。涉及 CheeseWAF 运行时行为时，以 CheeseWAF 的架构 contract 和阶段验收证据为准；没有执行证据的内容必须标记为契约版或规划中。

## 发布资源

- 商店目录：store.cheesesec.com
- OTA 索引：ota.cheesesec.com
- 不可变资源：res.cheesesec.com
- 离线包：.crp（CheeseWAF Resources Package）

当前 v1 只接受 `manifest.json`、一个 `artifact/<file>` 和
`signatures/manifest.json`。`provenance/`、DuckDB 专用字段和其他扩展字段
属于 v2/规划，不能写进当前 Get Started。
