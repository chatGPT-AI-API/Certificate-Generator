from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from cert_generator import CertificateGenerator
from datetime import datetime
import os

app = FastAPI(title="证书生成API", version="1.0.0")

class CertificateRequest(BaseModel):
    common_name: str
    validity_days: int = 365
    output_prefix: str = None

@app.post("/certificates")
async def create_certificate(request: CertificateRequest):
    try:
        generator = CertificateGenerator()
        cert = generator.generate_cert(
            common_name=request.common_name,
            validity_days=request.validity_days
        )
        
        prefix = request.output_prefix or request.common_name
        generator.save_to_files(cert, prefix)
        
        return {
            "status": "success",
            "files": [f"{prefix}.key", f"{prefix}.pem"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/certificates/{file_name}")
async def download_certificate(file_name: str):
    if not file_name.endswith(('.key', '.pem')):
        raise HTTPException(status_code=400, detail="仅支持.key和.pem文件下载")
    
    if not os.path.exists(file_name):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)