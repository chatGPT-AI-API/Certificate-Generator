# 证书生成器

## 功能描述
自动生成SSL/TLS证书的Python脚本，支持自定义有效期和密钥长度

## 文档结构

- [使用指南](#使用方法)
- [证书生成参数说明](#参数说明)
- [常见问题解答](./faq.md)

## 环境要求
- Python 3.8+
- cryptography 41.0.7+

## 快速开始
```bash
pip install -r requirements.txt
python cert_generator.py
```

## 配置选项
- 证书有效期（默认365天）
- RSA密钥长度（默认2048位）
- 输出目录设置

## 使用示例
```python
from cert_generator import generate_cert

generate_cert(
    common_name="example.com",
    validity_days=730,
    key_size=4096
)
```

## 贡献指南
欢迎提交PR和改进建议

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

### 依赖安装失败
- 确保使用Python 3.8+版本
- 尝试先升级pip：`python -m pip install --upgrade pip`
- 如果安装cryptography失败，可能需要安装OpenSSL开发包

### 证书生成时间过长
- 2048位密钥生成约需2-5秒属正常现象
- 4096位密钥可能需要10-30秒
- 建议开发环境使用2048位密钥

### 权限被拒绝错误
- 输出目录需要写入权限
- Windows用户请避免写入系统保护目录
- 建议使用绝对路径指定输出位置

### 证书验证失败
- 检查系统时间是否准确
- 确保证书未过期（默认365天）
- 验证证书链完整性

### 自定义配置无效
- 确保在调用generate_cert前设置参数
- 检查参数类型是否正确
- 查看控制台警告信息
