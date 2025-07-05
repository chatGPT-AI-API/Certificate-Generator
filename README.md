# SSL证书生成工具

一个轻量级的Python工具，用于快速生成自签名SSL证书，适用于开发环境、内部服务或测试场景。

## 功能特性
- 生成RSA 2048位密钥对
- 创建自签名CA证书
- 自定义证书有效期
- 支持多域名/主机名配置（Subject Alternative Name）
- 一键生成PEM格式的证书和私钥
- 自动验证证书信息

## 适用场景
- 本地开发环境HTTPS配置
- 内部网络服务加密
- 测试环境SSL证书部署
- 学习SSL证书原理和应用

## 安装依赖
确保已安装Python 3.6+环境，执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

依赖说明：
- cryptography: 用于证书生成的核心库
- argparse: 处理命令行参数（Python标准库）

## 使用方法

### 基本用法
```bash
python cert_generator.py \
  --name "example.com" \
  --days 365 \
  --output my_domain_cert
```

### 高级用法（多域名配置）
```bash
python cert_generator.py \
  --name "example.com" \
  --days 730 \
  --output multi_domain_cert \
  --alt-names "www.example.com,api.example.com,test.example.com"
```

## 参数说明
| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `--name` | 证书通用名称(CN)，通常为主要域名 | 是 | 无 |
| `--days` | 有效期天数 | 否 | 365 |
| `--output` | 输出文件前缀 | 否 | 使用`--name`参数值 |
| `--alt-names` | 备用域名列表，用逗号分隔 | 否 | 无 |
| `--country` | 国家代码(2位) | 否 | CN |
| `--state` | 省份/州 | 否 | Beijing |
| `--locality` | 城市 | 否 | Beijing |
| `--org` | 组织名称 | 否 | Example Org |
| `--org-unit` | 部门名称 | 否 | IT Department |

## 生成文件
执行命令后会生成以下文件：
- `<output_prefix>.key`: 私钥文件（PEM格式）
- `<output_prefix>.pem`: 证书文件（PEM格式）
- `<output_prefix>.csr`: 证书签名请求文件（可选）

## 验证证书
生成证书后，可以使用OpenSSL验证证书信息：

```bash
# 查看证书信息
openssl x509 -in <output_prefix>.pem -text -noout

# 验证私钥与证书匹配
openssl rsa -noout -modulus -in <output_prefix>.key | openssl md5
openssl x509 -noout -modulus -in <output_prefix>.pem | openssl md5
```

## 注意事项
- 自签名证书不受浏览器信任，生产环境请使用正规CA机构颁发的证书
- 私钥文件应妥善保管，避免泄露
- 建议定期更新证书，避免使用过长有效期的证书
- 请勿在生产环境中依赖此工具生成的证书

## 常见问题
Q: 浏览器提示证书不受信任怎么办？
A: 这是正常现象，自签名证书不会被浏览器默认信任。开发环境可以手动将证书添加到信任列表。

Q: 可以生成ECC证书吗？
A: 目前版本仅支持RSA算法，后续版本可能会添加ECC支持。

Q: 如何批量生成多个证书？
A: 可以编写脚本循环调用本工具，或修改代码添加批量生成功能。