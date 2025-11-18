from setuptools import setup, find_packages

setup(
    name="weixinautox4",  # 包名
    version="1.0.7",  # 版本号
    description="WeChat automation SDK with license management.",
    author="agentaibot",
    author_email="zhilongfeng66@gmail.com",
    packages=find_packages(),  # 包含 weixinauto 下所有模块
    install_requires=[
        "requests>=2.24.0",  # HTTP 请求
        "Cython>=0.29.21",    # Cython 编译
        "pydantic>=1.8.2",    # 数据验证与配置管理
        "pywin32==311",       # Windows API 和 COM 交互
        "uiautomation==2.0.29", # Windows UI 自动化
    ],
    include_package_data=True,
    package_data={
        # PyArmor runtime 包里的 pyd
        "pyarmor_runtime_000000": ["pyarmor_runtime.*"],

        # uia 中用到的选择器配置
        "weixinauto.infra.uia": ["selectors/*.json"],

        # 授权核心 license_core.pyd 所在包
        # 你的实际路径是 weixinauto/secure/license_core.cp311-win_amd64.pyd
        "weixinauto.secure": ["license_core.*"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
