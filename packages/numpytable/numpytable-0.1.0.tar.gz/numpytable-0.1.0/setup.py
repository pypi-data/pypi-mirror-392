from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="numpytable",  # 包名（PyPI上需唯一）
    version="0.1.0",    # 版本号
    author="knighthood2001",  # 作者名
    author_email="2109695291@qq.com",  # 作者邮箱
    description="快速将Excel复制的表格文本转换为NumPy数组",  # 短描述
    long_description=long_description,  # 长描述（来自README）
    long_description_content_type="text/markdown",
    url="https://github.com/Knighthood2001/numpytable",  # 项目地址（可选）
    packages=find_packages(),  # 自动发现包
    install_requires=["numpy>=1.19.0"],  # 依赖项
    classifiers=[  # 分类信息（PyPI用）
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.6",  # 支持的Python版本
)