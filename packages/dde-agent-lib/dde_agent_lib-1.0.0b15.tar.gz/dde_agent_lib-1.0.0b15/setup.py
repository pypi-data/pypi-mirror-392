from setuptools import setup, find_packages

setup(
    name='dde-agent-lib',
    version='1.0.0b15',
    packages=find_packages(),
    install_requires=[],
    author='geogpt',
    author_email='zhuquezhitu@zhejianglab.com',
    description='geogpt agent library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    package_data={
        # 原有配置：打包所有包下的 *.yaml 文件（保留）
        "": ["*.yaml"],
        # 新增配置：打包 db 包下 data 目录的所有文件和子目录
        "db": ["data/*", "data/**/*"]  # 递归匹配 data 下所有内容
    }
)