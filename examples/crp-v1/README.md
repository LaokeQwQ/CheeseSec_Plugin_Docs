# CRP v1 最小归档示例

这个目录只演示当前 `CheeseWAF/internal/crp.ParseArchive` 接受的归档布局。
它不是可安装插件：`signatures/manifest.json` 使用空数组，没有真实私钥或签名。

从本目录生成归档时，只选择下面三个文件。不要使用 `zip -r .`，否则会把
本说明文件也放进归档，当前 v1 解析器会拒绝未知条目。

```sh
zip -X demo-v1.crp manifest.json artifact/payload.txt signatures/manifest.json
unzip -l demo-v1.crp
```

预期条目只有：

```text
manifest.json
artifact/payload.txt
signatures/manifest.json
```

生成的 `.crp` 只用于布局检查。真正导入还需要有效的信任根、签名阈值、
来源注册和版本防降级检查。
