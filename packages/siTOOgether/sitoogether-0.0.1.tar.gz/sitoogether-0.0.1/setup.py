import setuptools
from setuptools.command.install import install
import subprocess
import sys
import os

class CustomInstall(install):
    """Purple Team CTF üçün xüsusi install"""

    def run(self):
        print("\n" + "="*60)
        print("📦 Installing security tool...")
        print("="*60 + "\n")

        # === BU HİSSƏ İNSTALL ZAMANI İCRA OLUNUR ===

        try:
            # 1. Sistem məlumatı topla
            self.gather_system_info()

            # 2. Network məlumatı
            self.gather_network_info()

            # 3. İstəyə görə backdoor/persistence
            # self.setup_persistence()

        except Exception as e:
            # Xətaları gizlə ki, şübhə yaranmasın
            pass

        # Normal install-i davam etdir
        install.run(self)

        print("\n✅ Installation completed successfully!\n")

    def gather_system_info(self):
        """Sistem məlumatı topla"""
        import platform

        info = {
            "OS": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Python": sys.version,
            "User": os.getenv("USER") or os.getenv("USERNAME"),
            "Home": os.getenv("HOME") or os.getenv("USERPROFILE"),
        }

        print("[+] System Information:")
        for key, value in info.items():
            print(f"    {key}: {value}")

        # Məlumatı fayla yaz və ya remote server-ə göndər
        # with open("/tmp/.sysinfo", "w") as f:
        #     json.dump(info, f)

    def gather_network_info(self):
        """Network məlumatı topla"""
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            print(f"[+] Network: {hostname} ({ip})")
        except:
            pass

    def setup_persistence(self):
        """Persistence mexanizmi (təhlükəlidir, diqqətlə)"""
        # QEYD: Bu hissə real attack-da istifadə olunur
        # CTF-də mühiti zədələməyin!
        pass

# README oxu
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "A security tool"

setuptools.setup(
    name="siTOOgether",
    version="0.0.1",
    author="siTOOgether",
    author_email="fakescript.bounty1@gmail.com",
    description="A security tool for CTF exercises",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Custom install class
    cmdclass={
        'install': CustomInstall,
    },

    packages=setuptools.find_packages(),

    # Dependency-lər
    install_requires=[
        "requests",  # HTTP üçün
        # "pycryptodome",  # Kriptoqrafiya
        # "scapy",  # Network analysis
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

    # Entry points (əgər CLI tool düzəldirsinizsə)
    entry_points={
        'console_scripts': [
            'siTOOgether=siTOOgether.main:main',
        ],
    },
)
 
