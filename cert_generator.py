from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

try:
    # 尝试导入Tkinter库（Python 3）
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    tk_available = True
except ImportError:
    # 导入失败时设置标志
    tk_available = False

class CertificateGenerator:
    def __init__(self):
        import logging
        logging.basicConfig(level=logging.INFO)
        
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        logging.info(f"私钥生成成功: {self.private_key is not None}")

    def generate_cert(self, common_name, validity_days=365):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(datetime.UTC)
        ).not_valid_after(
            datetime.now(datetime.UTC) + timedelta(days=validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        ).sign(self.private_key, hashes.SHA256(), default_backend())

        return cert

    def save_to_files(self, cert, prefix='cert'):
        with open(f"{prefix}.key", "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(f"{prefix}.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

def run_gui():
    if not tk_available:
        messagebox.showerror("错误", "无法导入Tkinter库，请确保您的Python环境支持GUI。")
        return

    def generate_certificate():
        common_name = entry_common_name.get()
        validity_days = int(spinbox_days.get())
        output_prefix = entry_output.get() or common_name

        if not common_name:
            messagebox.showerror("错误", "请输入证书通用名称")
            return

        try:
            generator = CertificateGenerator()
            certificate = generator.generate_cert(common_name, validity_days)
            generator.save_to_files(certificate, output_prefix)
            messagebox.showinfo("成功", f"证书已生成: {output_prefix}.key/pem")
        except Exception as e:
            messagebox.showerror("错误", f"生成证书时出错: {str(e)}")

    root = tk.Tk()
    root.title("SSL证书生成工具")
    root.geometry("400x300")
    root.resizable(False, False)

    # 设置中文字体
    style = ttk.Style()
    style.configure("TLabel", font=("SimHei", 10))
    style.configure("TButton", font=("SimHei", 10))
    style.configure("TEntry", font=("SimHei", 10))

    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    # 证书通用名称
    ttk.Label(frame, text="证书通用名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_common_name = ttk.Entry(frame, width=30)
    entry_common_name.grid(row=0, column=1, sticky=tk.W, pady=5)

    # 有效期天数
    ttk.Label(frame, text="有效期天数:").grid(row=1, column=0, sticky=tk.W, pady=5)
    spinbox_days = ttk.Spinbox(frame, from_=1, to=3650, width=27, value=365)
    spinbox_days.grid(row=1, column=1, sticky=tk.W, pady=5)

    # 输出文件名前缀
    ttk.Label(frame, text="输出文件名前缀:").grid(row=2, column=0, sticky=tk.W, pady=5)
    entry_output = ttk.Entry(frame, width=30)
    entry_output.grid(row=2, column=1, sticky=tk.W, pady=5)

    # 生成按钮
    button_generate = ttk.Button(frame, text="生成证书", command=generate_certificate)
    button_generate.grid(row=3, column=0, columnspan=2, pady=20)

    # 底部信息
    ttk.Label(frame, text="SSL证书生成工具 v1.0").grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SSL证书生成工具')
    parser.add_argument('-n', '--name', help='证书通用名称')
    parser.add_argument('-d', '--days', type=int, default=365, help='有效期天数')
    parser.add_argument('-o', '--output', help='输出文件名前缀')
    parser.add_argument('--gui', action='store_true', help='启动图形界面')
    
    args = parser.parse_args()
    
    if args.gui or (args.name is None and tk_available):
        run_gui()
    else:
        if args.name is None:
            parser.error('-n/--name 参数是必需的，除非使用 --gui 选项')
        
        generator = CertificateGenerator()
        certificate = generator.generate_cert(args.name, args.days)
        generator.save_to_files(certificate, args.output or args.name)
        print(f"证书已生成: {args.output or args.name}.key/pem")