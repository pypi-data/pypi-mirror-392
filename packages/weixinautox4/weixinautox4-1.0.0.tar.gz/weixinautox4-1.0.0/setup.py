from setuptools import setup, find_packages

setup(
    name="weixinautox4",  # 包名
    version="1.0.0",  # 版本号
    description="WeChat automation SDK with license management.",
    author="agentaibot",
    author_email="zhilongfeng66@gmail.com",
    packages=find_packages(),  # 自动查找所有子包
    install_requires=[
        "requests>=2.24.0",  # HTTP 请求
        "Cython>=0.29.21",    # Cython 编译
        "pydantic>=1.8.2",    # 数据验证与配置管理
        "pywin32==311",       # Windows API 和 COM 交互
        "uiautomation==2.0.29", # Windows UI 自动化
    ],
    include_package_data=True,
    package_data={
        "weixinauto": ["secure/license_core.pyd"],  # 包含混淆后的 .pyd 文件
    },
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",  # 如果 README 是 markdown 格式
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 根据你的项目要求调整支持的 Python 版本
)
