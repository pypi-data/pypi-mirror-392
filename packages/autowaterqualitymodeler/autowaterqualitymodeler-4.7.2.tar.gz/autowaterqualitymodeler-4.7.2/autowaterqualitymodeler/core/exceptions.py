"""
自定义异常类
"""


class WaterQualityModelError(Exception):
    """基础异常类"""

    pass


class DataValidationError(WaterQualityModelError):
    """数据验证错误"""

    pass


class ProcessingError(WaterQualityModelError):
    """数据处理错误"""

    pass


class ConfigurationError(WaterQualityModelError):
    """配置错误"""

    pass


class ModelingError(WaterQualityModelError):
    """建模错误"""

    pass
