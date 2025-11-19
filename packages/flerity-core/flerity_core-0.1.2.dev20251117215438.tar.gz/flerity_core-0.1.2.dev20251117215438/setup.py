"""Setup configuration for flerity-core."""

from setuptools import find_packages, setup

setup(
    name="flerity_core",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "sqlalchemy[asyncio]>=2.0.0",
        "asyncpg>=0.29.0",
        "pydantic>=2.5.0",
        "fastapi>=0.104.0",
        "redis>=5.0.0",
        "httpx>=0.25.0",
        "structlog>=23.2.0",
        "cryptography>=41.0.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
    ],
)
