# 文档贡献规范

本仓库是 CheeseSec Plugin 的双语手册。每项说明必须与 CheeseWAF 的可执行契约和验收证据一致；仅有设计的内容必须明确标注“契约版”，不得把未实现的安装、OTA、热载或 CWEDP 行为写成现成功能。

提交文档前请检查中英文含义、配置键、域名、版本和许可证，并运行 git diff --check。安全敏感示例必须写明确认次数、10 秒等待、审计、回滚和离线行为。

提交前还必须运行 CRP schema、示例归档、双语页面、链接和 secret scan
门禁（见 README 的本地命令）。schema 只描述当前 v1 可执行边界；生成的
`.crp`、私钥、Token、密码和构建输出不得提交。

当前 v1 CRP 示例只能包含 `manifest.json`、一个 `artifact/<file>` 和
`signatures/manifest.json`。`provenance/`、`package_id`、`class`、目标 API、
平台/架构、权限等内容必须明确标为 v2/规划，不能混入当前 Get Started。
示例不得包含私钥、Token、密码、客户数据或生成产物。贡献者应说明信任级别、
签名阈值、密钥有效期、吊销方式、审批记录和变更记录。Ansible 只描述
bootstrap；安装、升级、回滚和集群分发只描述 CWEDP。

新增页面时，同时维护中文和英文入口，并在页面中链接权威 contract。域名固定为 store.cheesesec.com、ota.cheesesec.com 和 res.cheesesec.com；离线包统一称为 .crp（CheeseWAF Resources Package）。

许可证和第三方资料必须保留来源与版权信息。不要复制闭源手册、凭证或不可再分发素材。
