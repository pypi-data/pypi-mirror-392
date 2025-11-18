# ============================================
# setup.py — DSF EngineXAI SDK
# ============================================
from setuptools import setup, find_packages
import os

# Leer README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dsf-enginexai-sdk",  # ✅ ACTUALIZADO
    version="1.0.1",
    author="Jaime Alexander Jimenez",
    author_email="contacto@dsfuptech.cloud",
    description="Explainable AI Scoring SDK with LLM Integration for Transparent Risk Assessment",  # ✅ ACTUALIZADO
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaimeajl/dsf-enginexai-sdk",  # ✅ ACTUALIZADO
    project_urls={
        "Documentation": "https://dsfuptech.cloud/docs",
        "Source": "https://github.com/jaimeajl/dsf-enginexai-sdk",  # ✅ ACTUALIZADO
        "API Endpoint": "https://dsf-scoring-h7y7tiqp6-api-dsfuptech.vercel.app/",  # ✅ ACTUALIZADO
    },
    packages=find_packages(include=["dsf_enginexai_sdk", "dsf_enginexai_sdk.*"]),  # ✅ ACTUALIZADO
    include_package_data=True,
    license="Proprietary License © 2025 Jaime Alexander Jimenez (Uptech)",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",  # ✅ AÑADIDO
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial",  # ✅ AÑADIDO
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",  # ✅ AÑADIDO
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="explainable-ai xai llm-integration credit-scoring risk-assessment adaptive-learning transparency compliance fintech",  # ✅ ACTUALIZADO
)

