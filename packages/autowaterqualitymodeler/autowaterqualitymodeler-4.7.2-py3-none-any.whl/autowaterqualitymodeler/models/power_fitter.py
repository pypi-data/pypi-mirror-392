"""
幂函数模型拟合器

提供 y = a * x^b 形式的幂函数拟合功能。
"""

import logging
import warnings

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr

from ..core.types import PowerFitResult

logger = logging.getLogger(__name__)


class PowerModelFitter:
    """
    幂函数模型拟合器

    拟合 y = a * x^b 形式的幂函数模型。
    """

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        initial_guess: list[float] | None = None,
    ) -> PowerFitResult | None:
        """
        拟合幂函数模型

        Args:
            x: 特征值数组（必须为正数）
            y: 目标值数组（必须为正数）
            initial_guess: 参数初始猜测值 [a, b]

        Returns:
            拟合结果，失败返回 None
        """
        # 数据验证
        if len(x) < 3:
            logger.warning("有效数据点少于3个，无法拟合")
            return None

        # 过滤非正数
        valid_mask = (x > 0) & (y > 0) & ~np.isnan(x) & ~np.isnan(y)
        x_valid = x[valid_mask]
        y_valid = y[valid_mask]

        if len(x_valid) < 3:
            logger.warning("过滤后有效数据点少于3个，无法拟合")
            return None

        logger.debug(
            f"拟合数据范围 - x: {x_valid.min():.4f}-{x_valid.max():.4f}, "
            f"y: {y_valid.min():.4f}-{y_valid.max():.4f}"
        )

        try:
            # 初始猜测
            if initial_guess is None:
                initial_guess = [1.0, 1.0]

            # 参数约束
            bounds = ([0.000001, -50], [100000, 50])

            # 执行拟合
            popt, pcov = curve_fit(
                self._power_function,
                x_valid,
                y_valid,
                p0=initial_guess,
                maxfev=10000,
                method="trf",
                bounds=bounds,
            )

            a, b = popt

            # 检查参数是否接近边界
            if abs(a) > bounds[1][0] * 0.9 or abs(b) > bounds[1][1] * 0.9:
                logger.warning(f"拟合参数接近边界值: a={a:.4f}, b={b:.4f}")

            # 计算预测值
            y_pred = self._power_function(x_valid, a, b)

            # 计算评价指标
            if len(set(y_valid)) > 1 and len(set(y_pred)) > 1:
                correlation, _ = pearsonr(y_valid, y_pred)
            else:
                logger.warning("输入数组是常量，相关系数设为0.1")
                correlation = 0.1

            rmse = float(np.sqrt(np.mean((y_pred - y_valid) ** 2)))
            ss_res = np.sum((y_valid - y_pred) ** 2)
            ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
            r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

            logger.debug(
                f"拟合完成: a={a:.4f}, b={b:.4f}, "
                f"corr={correlation:.4f}, rmse={rmse:.4f}, r2={r2:.4f}"
            )

            return PowerFitResult(
                a=float(a),
                b=float(b),
                correlation=float(correlation),
                rmse=rmse,
                r2=r2,
            )

        except Exception as e:
            logger.error(f"幂函数拟合失败: {e}")
            return None

    def predict(self, x: np.ndarray, a: float, b: float) -> np.ndarray:
        """
        使用幂函数模型预测

        Args:
            x: 特征值数组
            a: 幂函数参数 a
            b: 幂函数参数 b

        Returns:
            预测值数组
        """
        return self._power_function(x, a, b)

    @staticmethod
    def _power_function(x: np.ndarray, a: float, b: float) -> np.ndarray:
        """幂函数: y = a * x^b"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return a * np.power(x, b)
