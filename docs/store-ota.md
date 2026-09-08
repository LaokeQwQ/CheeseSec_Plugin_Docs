# 插件商店与更新索引

CheeseSec Plugins 是面向 CheeseSec 生态的独立插件产品。插件是否适用于某个产品、可用版本及安装步骤，以插件说明和对应宿主产品的文档为准。

## 浏览插件

访问 [CheeseSec 插件商店](https://store.cheesesec.com/) 无需登录。商店展示已公开发布的插件；如果目录为空，表示当前没有可展示的正式发布。文档中的示例不代表可安装的插件。

开发者也可以读取公开的 v1 目录：

```sh
curl --fail https://store.cheesesec.com/v1/catalog/index.json
```

目录包含发布记录、撤回记录和目录序号。读取方应识别 `api_version`，检查记录类型、命名空间、版本和摘要；被撤回的发布不应继续作为可安装候选。

## 更新索引

公开更新索引按 `stable`、`canary`、`dev` 三个通道区分：

```text
https://ota.cheesesec.com/v1/channels/stable/index.json
https://ota.cheesesec.com/v1/channels/canary/index.json
https://ota.cheesesec.com/v1/channels/dev/index.json
```

通道索引可能没有发布记录。索引存在不表示某个宿主已经支持自动更新；请先确认对应产品的升级功能、兼容要求和备份步骤。

## 下载与校验

正式发布记录中的资源地址采用以下格式：

```text
https://res.cheesesec.com/sha256/<sha256>/<filename>
```

下载后应核对发布记录中的 SHA-256 摘要。摘要匹配只能证明内容一致，不能替代签名、信任来源、撤回状态或兼容性检查。安装应使用对应宿主支持的验证与安装流程，不应直接执行未经验证的包。

## 公开接口约定

- 公开目录、更新索引和资源端点仅供 `GET`、`HEAD` 读取。
- 不要向公开读取端点发送账号密码、会话 Cookie、访问令牌或其他凭据。
- 不存在的路径返回 `404`，不支持的方法返回 `405`。
- 客户端可以使用 `ETag` 和条件请求避免重复下载；更新索引的序号应防止旧版本被误认为新版本。
- 资源下载支持单段字节范围请求；客户端应处理 `206` 和无效范围的 `416` 响应。

公开 JSON 结构以对应 v1 schema 为准。插件包格式请参阅 [CRP 开发指南](crp-development.md)，宿主集成示例仅适用于其注明的产品。
