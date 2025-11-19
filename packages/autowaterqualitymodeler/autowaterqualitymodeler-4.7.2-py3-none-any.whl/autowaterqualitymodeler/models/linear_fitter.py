"""
线性模型拟合器

提供 y = A * x 形式的线性拟合功能（过原点），用于模型微调。
"""

import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)


class LinearModelFitter:
    """
    线性模型拟合器

    拟合 y = A * x 形式的线性模型（过原点），用于微调。
    """

    def fit(self, predicted: pd.Series, measured: pd.Series) -> float | None:
        """
        通过线性回归微调模型

        Args:
            predicted: 预测值
            measured: 实测值

        Returns:
            调整系数 A，失败返回 None
        """
        # 去除缺失值
        valid_data = pd.concat([predicted, measured], axis=1).dropna()

        if len(valid_data) < 2:
            logger.warning("有效数据点少于2个，无法进行线性调整")
            return None

        x = valid_data.iloc[:, 0].to_numpy().reshape(-1, 1)  # 预测值
        y = valid_data.iloc[:, 1].to_numpy()  # 实测值

        try:
            # 拟合线性模型（强制通过原点）
            model = LinearRegression(fit_intercept=False)
            model.fit(x, y)

            # 获取系数
            a = float(model.coef_[0])

            # 计算评估指标
            y_pred = model.predict(x)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))

            logger.info(
                f"线性微调完成: 系数={a:.4f}, R²={r2:.4f}, "
                f"RMSE={rmse:.4f}, 样本数={len(valid_data)}"
            )

            return a

        except Exception as e:
            logger.error(f"线性调整失败: {e}")
            return None

    def predict(self, x: pd.Series | np.ndarray, a: float) -> pd.Series | np.ndarray:
        """
        使用线性模型预测

        Args:
            x: 原始预测值
            a: 调整系数

        Returns:
            调整后的预测值
        """
        return a * x
