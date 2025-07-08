import logging
import logging.config
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from cert_generator import CertificateGenerator
from datetime import datetime
import os
import zipfile

# 配置日志
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# 跟踪已生成的证书文件
generated_certs = set()

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="证书生成API",
    version="1.0.0",
    description="证书生成服务API文档",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "证书",
            "description": "证书生成和管理相关接口",
        },
    ],
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "filter": True,
        "operationsSorter": "method",
        "tagsSorter": "alpha",
        "validatorUrl": None,
        "syntaxHighlight": {
            "activate": True,
            "theme": "tomorrow-night"
        }
    }
)

from fastapi.openapi.docs import get_swagger_ui_html
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={
            **app.swagger_ui_parameters,
            "lang": "zh-CN",
            "translator": """
                function (translations) {
                    translations['zh-CN'] = {
                        'operations': '操作',
                        'no operations': '无可用操作',
                        'try it out': '尝试一下',
                        'show/hide': '显示/隐藏',
                        'list operations': '列出操作',
                        'expand operations': '展开操作',
                        'authorize': '授权',
                        'response': '响应',
                        'request': '请求',
                        'model': '模型',
                        'schemes': '协议',
                        'im': '接口模型'
                    };
                    return translations;
                }
            """
        },
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
    )

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "欢迎使用证书生成API服务",
            "docs": "/docs",
            "endpoints": {
                "create_certificate": {
                    "method": "POST",
                    "path": "/certificates",
                    "description": "生成新的证书"
                },
                "download_certificate": {
                    "method": "GET",
                    "path": "/certificates/{file_name}",
                    "description": "下载证书文件"
                }
            }
        }
    )

class CertificateRequest(BaseModel):
    common_name: str
    validity_days: int = 365
    output_prefix: str = None

from fastapi.responses import StreamingResponse
from io import BytesIO

@app.post("/certificates", tags=["证书"])
async def create_certificate(request: CertificateRequest):
    logger.info(f"开始生成证书: {request.common_name}, 有效期: {request.validity_days}天")
    try:
        generator = CertificateGenerator()
        cert = generator.generate_cert(
            common_name=request.common_name,
            validity_days=request.validity_days
        )
        
        prefix = request.output_prefix or request.common_name
        key_bytes, cert_bytes = generator.get_cert_bytes(cert)
        
        # 创建包含两个文件的zip包
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{prefix}.key", key_bytes)
            zip_file.writestr(f"{prefix}.pem", cert_bytes)
        zip_buffer.seek(0)
        
        # 返回zip文件下载
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={prefix}_certificates.zip"
            }
        )
    except Exception as e:
        logger.error(f"生成证书失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

# 移除旧的下载端点

if __name__ == "__main__":
    import uvicorn
    logger.info("启动证书生成服务")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config="logging.conf")