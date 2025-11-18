from setuptools import setup, find_packages

setup(
    name="weixinautox4",  # 包名
    version="1.0.2",  # 版本号
    description="WeChat automation SDK with license management.",
    author="agentaibot",
    author_email="zhilongfeng66@gmail.com",
    packages=find_packages(),  # 自动发现包，确保包括所有子目录
    install_requires=[
        "requests>=2.24.0",
        "Cython>=0.29.21",
        "pydantic>=1.8.2",
        "pywin32==311",
        "uiautomation==2.0.29",
    ],
    include_package_data=True,
    package_data={
        "weixinauto": ["secure/*.pyd", "infra/uia/*.pyd"],  # 包含所有需要的 .pyd 文件
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
