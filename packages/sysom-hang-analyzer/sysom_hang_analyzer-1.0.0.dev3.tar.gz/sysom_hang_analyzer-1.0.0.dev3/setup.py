# setup.py
import os
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys

class PostInstallCommand(install):
    """Custom post-installation for installation mode."""
    def run(self):
        install.run(self)
        # 安装py-spy
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'py-spy'])
        
        # 尝试复制pstack到/opt/conda/bin/
        try:
            import shutil
            source_pstack = os.path.join(os.path.dirname(__file__), 'cluster', 'pstack')
            dest_pstack = '/opt/conda/bin/pstack'
            
            if os.path.exists(source_pstack):
                # 确保目标目录存在
                os.makedirs(os.path.dirname(dest_pstack), exist_ok=True)
                shutil.copy2(source_pstack, dest_pstack)
                # 设置执行权限
                os.chmod(dest_pstack, 0o755)
                print(f"Successfully installed pstack to {dest_pstack}")
            else:
                print("Warning: pstack script not found")
        except Exception as e:
            print(f"Warning: Failed to install pstack to /opt/conda/bin/: {e}")

setup(
    name="sysom-hang-analyzer",
    version="1.0.0.dev3",
    author="Your Name",
    author_email="your.email@example.com",
    description="Distributed stack collection and analysis tool",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        'cluster': ['flamegraph.pl', 'pstack'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    install_requires=[
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "distributed-coordinator=cluster.distributed_coordinator:main",
            "node-agent=cluster.node_agent:main",
            "stack-collector=cluster.auto_stack_collector:main",
            "stack-processor=cluster.stack_processor:main",
            "aggregate-analysis=cluster.aggregate_analysis:main",
            "trigger-collection=cluster.trigger_distributed_collection:main",
            "sysom-hang-analyzer=cluster.sysom_hang_analyzer:main",
        ],
    },
    scripts=['cluster/pstack', 'cluster/flamegraph.pl'],
    cmdclass={
        'install': PostInstallCommand,
    },
)