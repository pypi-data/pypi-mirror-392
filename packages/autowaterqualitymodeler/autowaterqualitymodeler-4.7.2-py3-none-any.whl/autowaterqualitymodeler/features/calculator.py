"""
特征计算模块

提供光谱特征公式解析和计算功能。
"""

import ast
import logging
from typing import Callable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureCalculator:
    """
    特征计算器

    支持公式解析和计算，包括波段反射率、波段组合、三刺激值等。
    """

    def __init__(self, tris_coeff: pd.DataFrame | None = None):
        """
        初始化特征计算器

        Args:
            tris_coeff: 三刺激值系数表，用于颜色特征计算
        """
        self.tris_coeff = tris_coeff
        self.functions = self._register_functions()
        self.data: pd.DataFrame = pd.DataFrame()
        self.columns: set[float] = set()

    def _register_functions(self) -> dict[str, Callable]:
        """注册支持的函数"""
        return {
            "sum": self._sum,
            "mean": self._mean,
            "abs": self._abs,
            "ref": self._ref,
            "tris": self._tris,
            "diff": self._diff,
            "ratio": self._ratio,
            "norm": self._norm,
            "log": self._log,
        }

    def calculate_feature(
        self, spectrum_data: pd.DataFrame, feature_definition: dict
    ) -> pd.Series:
        """
        根据特征定义计算单个特征

        Args:
            spectrum_data: 光谱数据
            feature_definition: 特征定义字典，包含 name 和 formula 字段

        Returns:
            计算的特征值
        """
        formula = feature_definition.get("formula")
        name = feature_definition.get("name")
        band_map = feature_definition.get("bands", {})

        if not name or not formula:
            return pd.Series(dtype=float)

        try:
            expr = formula
            for band, wavelength in band_map.items():
                expr = expr.replace(band, str(wavelength))
            result = self.evaluate(expr, spectrum_data)
            result.name = name
            return result
        except Exception as e:
            logger.error(f"计算特征 {name} 失败: {e}", exc_info=True)
            return pd.Series(dtype=float)

    def calculate_features(
        self, spectrum_data: pd.DataFrame, feature_definitions: list[dict]
    ) -> pd.DataFrame:
        """
        根据多个特征定义计算特征

        Args:
            spectrum_data: 光谱数据
            feature_definitions: 特征定义列表

        Returns:
            计算的特征数据
        """
        features = pd.DataFrame(index=spectrum_data.index)

        for feature_def in feature_definitions:
            feature = self.calculate_feature(spectrum_data, feature_def)
            if not feature.empty:
                features[feature.name] = feature

        return features

    def evaluate(self, expression: str, data: pd.DataFrame) -> pd.Series:
        """
        解析并计算表达式

        Args:
            expression: 特征公式
            data: 光谱数据

        Returns:
            计算结果
        """
        try:
            self.data = data
            self.columns = set(data.columns.astype(float))

            result = self._eval(ast.parse(expression, mode="eval").body)

            if isinstance(result, pd.Series):
                return result
            else:
                return pd.Series(result, index=data.index)
        except Exception as e:
            logger.error(f"表达式 '{expression}' 计算失败: {e}")
            raise ValueError(f"表达式 '{expression}' 计算失败: {e}")

    def _eval(self, node: ast.AST) -> pd.Series | float | str:
        """递归解析表达式"""
        if isinstance(node, ast.BinOp):
            left = self._eval(node.left)
            right = self._eval(node.right)

            if isinstance(node.op, ast.Add):
                return left + right  # type: ignore
            elif isinstance(node.op, ast.Sub):
                return left - right  # type: ignore
            elif isinstance(node.op, ast.Mult):
                return left * right  # type: ignore
            elif isinstance(node.op, ast.Div):
                if isinstance(right, pd.Series):
                    zero_mask = right == 0
                    if zero_mask.any():
                        logger.warning("除法运算中检测到除数为零，将替换为NaN")
                        right = right.copy()
                        right[zero_mask] = np.nan
                return left / right  # type: ignore
            elif isinstance(node.op, ast.Pow):
                return left**right  # type: ignore
            else:
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("不支持的函数调用格式")
            func_name = node.func.id.lower()
            if func_name not in self.functions:
                raise ValueError(f"不支持的函数: {func_name}")

            if func_name == "tris":
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Name):
                    raise ValueError("tris() 需要一个参数 'x', 'y' 或 'z'")
                arg = node.args[0].id
                return self.functions[func_name](arg)

            args = [self._eval(arg) for arg in node.args]
            return self.functions[func_name](*args)

        elif isinstance(node, ast.Constant):
            return node.value  # type: ignore

        elif isinstance(node, ast.Name):
            var_name = node.id
            try:
                band = float(var_name)
                if band in self.columns:
                    return self.data[band]
                else:
                    nearest_band = min(self.columns, key=lambda x: abs(x - band))
                    logger.warning(
                        f"波长 {band} 不存在，使用最接近的波长 {nearest_band}"
                    )
                    return self.data[nearest_band]
            except ValueError:
                if var_name in ["x", "y", "z"]:
                    return var_name
                else:
                    raise ValueError(f"无效的变量名: {var_name}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval(node.operand)

            if isinstance(node.op, ast.USub):
                return -operand  # type: ignore
            elif isinstance(node.op, ast.UAdd):
                return operand
            else:
                raise ValueError(f"不支持的一元运算符: {type(node.op).__name__}")

        else:
            raise ValueError(f"不支持的表达式类型: {type(node).__name__}")

    def _sum(self, start_band: float, end_band: float) -> pd.Series:
        """计算波段范围内的和"""
        start_band = float(start_band)
        end_band = float(end_band)

        cols = [
            col for col in self.data.columns if start_band <= float(col) <= end_band
        ]
        if not cols:
            raise ValueError(f"波段范围 {start_band}-{end_band} 内没有数据")

        return self.data[cols].sum(axis=1)

    def _mean(self, start_band: float, end_band: float) -> pd.Series:
        """计算波段范围内的均值"""
        start_band = float(start_band)
        end_band = float(end_band)

        cols = [
            col for col in self.data.columns if start_band <= float(col) <= end_band
        ]
        if not cols:
            raise ValueError(f"波段范围 {start_band}-{end_band} 内没有数据")

        return self.data[cols].mean(axis=1)

    def _abs(self, value: pd.Series | float) -> pd.Series | float:
        """计算绝对值"""
        return abs(value)  # type: ignore

    def _ref(self, band: float) -> pd.Series:
        """获取指定波段的反射率"""
        band = float(band)

        if band in self.columns:
            return self.data[band]
        else:
            nearest_band = min(self.columns, key=lambda x: abs(x - band))
            logger.warning(f"波长 {band} 不存在，使用最接近的波长 {nearest_band}")
            return self.data[nearest_band]

    def _tris(self, channel: str) -> pd.Series:
        """计算三刺激值"""
        if channel not in ["x", "y", "z"]:
            raise ValueError("tris() 参数必须是 'x', 'y' 或 'z'")

        if self.tris_coeff is None or self.tris_coeff.empty:
            raise ValueError("未加载三刺激值系数表")

        index = {"x": 0, "y": 1, "z": 2}[channel]
        coef = self.tris_coeff.iloc[index]

        valid_bands = [
            col
            for col in self.data.columns
            if col in coef.index or float(col) in coef.index
        ]
        if not valid_bands:
            raise ValueError("当前光谱数据与三刺激值系数表波段不匹配")

        result = pd.Series(0.0, index=self.data.index)
        for band in valid_bands:
            if band in coef.index:
                coef_value = coef[band]
            else:
                coef_value = coef[float(band)]
            result += self.data[band] * coef_value

        return result

    def _diff(self, band1: float, band2: float) -> pd.Series:
        """计算两个波段的差值"""
        return self._ref(float(band1)) - self._ref(float(band2))

    def _ratio(self, band1: float, band2: float) -> pd.Series:
        """计算两个波段的比值"""
        band1_ref = self._ref(float(band1))
        band2_ref = self._ref(float(band2))

        zero_mask = band2_ref == 0
        if zero_mask.any():
            logger.warning(f"ratio({band1}, {band2}) 中存在除数为零的情况")
            band2_ref = band2_ref.copy()
            band2_ref[zero_mask] = np.nan

        return band1_ref / band2_ref

    def _norm(
        self, value: pd.Series | float, min_val: float, max_val: float
    ) -> pd.Series | float:
        """归一化值到指定范围"""
        min_val = float(min_val)
        max_val = float(max_val)

        if isinstance(value, pd.Series):
            range_val = max_val - min_val
            if range_val == 0:
                logger.warning(f"归一化范围为零: {min_val}-{max_val}")
                return pd.Series(min_val, index=value.index)

            value_range = value.max() - value.min()
            if value_range == 0:
                logger.warning("输入数据范围为零，无法归一化")
                return pd.Series(min_val, index=value.index)

            return (value - value.min()) / value_range * range_val + min_val
        else:
            return value

    def _log(self, value: pd.Series | float, base: float = 10) -> pd.Series | float:
        """对数变换"""
        base = float(base)

        if base <= 0:
            raise ValueError(f"对数的底数必须大于0: {base}")

        if isinstance(value, pd.Series):
            invalid_mask = value <= 0
            if invalid_mask.any():
                logger.warning(
                    f"对数变换中检测到{invalid_mask.sum()}个非正值，将替换为NaN"
                )
                value = value.copy()
                value[invalid_mask] = np.nan

            return np.log(value) / np.log(base)
        else:
            if value <= 0:
                logger.warning(f"对数变换的输入值必须大于0: {value}")
                return np.nan
            return np.log(value) / np.log(base)
