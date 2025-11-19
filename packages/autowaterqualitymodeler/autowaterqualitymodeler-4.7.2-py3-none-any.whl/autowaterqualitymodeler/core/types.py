"""
核心数据类型定义模块

提供清晰的数据结构，用于在各模块间传递数据。
"""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class PowerFitResult:
    """幂函数拟合结果: y = a * x^b"""

    a: float
    b: float
    correlation: float
    rmse: float
    r2: float

    def to_dict(self) -> dict[str, float]:
        """转换为字典格式"""
        return {
            "a": self.a,
            "b": self.b,
            "corr": self.correlation,
            "rmse": self.rmse,
            "r2": self.r2,
        }


@dataclass
class FeatureResult:
    """单个特征的拟合结果"""

    feature_name: str
    fit_result: PowerFitResult

    @property
    def correlation(self) -> float:
        """获取相关系数"""
        return self.fit_result.correlation

    @property
    def a(self) -> float:
        """获取 a 参数"""
        return self.fit_result.a

    @property
    def b(self) -> float:
        """获取 b 参数"""
        return self.fit_result.b


@dataclass
class CombinedModelResult:
    """组合模型结果"""

    features: list[tuple[str, float, float, float]]  # [(name, weight, a, b), ...]
    correlation: float
    rmse: float
    predictions: pd.Series

    def to_dict(self) -> dict[str, dict[str, float]]:
        """转换为字典格式: {feature_name: {w, a, b}}"""
        return {name: {"w": w, "a": a, "b": b} for name, w, a, b in self.features}


@dataclass
class ModelingConfig:
    """建模配置参数"""

    min_wavelength: int = 400
    max_wavelength: int = 900
    smooth_window: int = 11
    smooth_order: int = 3
    min_samples: int = 6
    max_features: int = 5

    def validate(self) -> None:
        """验证配置参数"""
        if self.min_wavelength >= self.max_wavelength:
            raise ValueError("min_wavelength must be less than max_wavelength")
        if self.smooth_window < 3 or self.smooth_window % 2 == 0:
            raise ValueError("smooth_window must be odd and at least 3")
        if self.smooth_order >= self.smooth_window:
            raise ValueError("smooth_order must be less than smooth_window")
        if self.min_samples < 3:
            raise ValueError("min_samples must be at least 3")
        if self.max_features < 1:
            raise ValueError("max_features must be at least 1")


@dataclass
class ValidationResult:
    """数据验证结果"""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """添加错误信息"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """添加警告信息"""
        self.warnings.append(message)
