"""
AutoWaterQualityModeler - 自动水质光谱建模工具

自动水质光谱建模工具，提供一键式水质建模、预测和评估功能。
"""

from .core.config import Config
from .core.exceptions import (
    ConfigurationError,
    DataValidationError,
    ModelingError,
    ProcessingError,
    WaterQualityModelError,
)
from .core.model import WaterQualityModel
from .core.modeler import AutoWaterQualityModeler

# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("autowaterqualitymodeler")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.0.0+unknown"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import PackageNotFoundError, version

        try:
            __version__ = version("autowaterqualitymodeler")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "0.0.0+unknown"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.0.0+unknown"

__all__ = [
    "AutoWaterQualityModeler",
    "WaterQualityModel",
    "Config",
    "WaterQualityModelError",
    "DataValidationError",
    "ProcessingError",
    "ConfigurationError",
    "ModelingError",
]
