"""
特征选择器

根据拟合效果选择最佳特征。
"""

import logging

import pandas as pd

from ..core.types import FeatureResult
from ..models.power_fitter import PowerModelFitter

logger = logging.getLogger(__name__)


class FeatureSelector:
    """
    特征选择器

    根据幂函数拟合效果选择最佳特征。
    """

    def __init__(self, fitter: PowerModelFitter | None = None):
        """
        初始化特征选择器

        Args:
            fitter: 幂函数拟合器，如果为 None 则创建新实例
        """
        self.fitter = fitter or PowerModelFitter()

    def select_top_features(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        top_n: int | str = 5,
    ) -> list[FeatureResult]:
        """
        选择相关性最高的前 N 个特征

        Args:
            features: 特征数据，列为特征名
            target: 目标变量
            top_n: 选择的特征数量，可以是整数或 'all'

        Returns:
            按相关性降序排列的特征结果列表
        """
        if features.empty:
            logger.warning("特征数据为空")
            return []

        results: list[FeatureResult] = []

        for feature_name in features.columns:
            feature_values = features[feature_name]

            # 过滤有效数据（正数）
            valid_mask = (
                (feature_values > 0)
                & (target > 0)
                & (~feature_values.isna())
                & (~target.isna())
            )

            if valid_mask.sum() < 3:
                logger.debug(f"特征 {feature_name} 有效数据点少于3个，跳过")
                continue

            x = feature_values.loc[valid_mask].values
            y = target.loc[valid_mask].values

            # 拟合幂函数
            fit_result = self.fitter.fit(x, y)

            if fit_result:
                results.append(FeatureResult(feature_name, fit_result))
                logger.debug(
                    f"特征 {feature_name}: corr={fit_result.correlation:.4f}, "
                    f"a={fit_result.a:.4f}, b={fit_result.b:.4f}"
                )

        # 按相关性绝对值排序
        sorted_results = sorted(results, key=lambda x: abs(x.correlation), reverse=True)

        # 处理 top_n 参数
        if isinstance(top_n, str):
            if top_n.lower() == "all":
                selected = sorted_results
            else:
                try:
                    n = int(top_n)
                    selected = sorted_results[:n]
                except ValueError:
                    logger.warning(f"无效的 top_n 值: {top_n}，使用所有特征")
                    selected = sorted_results
        else:
            n = int(top_n)
            selected = sorted_results[:n]

        logger.info(f"从 {len(results)} 个特征中选择了 {len(selected)} 个最佳特征")

        return selected
