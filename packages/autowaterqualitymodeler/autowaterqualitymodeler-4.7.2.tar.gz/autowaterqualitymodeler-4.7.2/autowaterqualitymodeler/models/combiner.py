"""
模型组合器

将多个特征模型加权组合，找到最佳组合。
"""

import logging

import numpy as np
import pandas as pd

from ..core.types import CombinedModelResult, FeatureResult

logger = logging.getLogger(__name__)


class ModelCombiner:
    """
    模型组合器

    将多个特征的幂函数模型加权组合。
    """

    def find_best_combination(
        self,
        selected_features: list[FeatureResult],
        feature_data: pd.DataFrame,
        target: pd.Series,
    ) -> CombinedModelResult | None:
        """
        找到最佳的特征组合

        尝试不同数量的特征组合，选择相关性最高的组合。

        Args:
            selected_features: 已按相关性排序的特征列表
            feature_data: 特征数据
            target: 目标变量

        Returns:
            最佳组合结果，失败返回 None
        """
        if not selected_features:
            logger.warning("没有可用的特征")
            return None

        best_result: CombinedModelResult | None = None
        best_corr = 0.0

        # 尝试不同数量的特征组合
        for n in range(1, len(selected_features) + 1):
            subset = selected_features[:n]
            result = self._evaluate_combination(subset, feature_data, target)

            if result and result.correlation > best_corr:
                best_corr = result.correlation
                best_result = result
                logger.debug(f"使用 {n} 个特征时相关性: {result.correlation:.4f}")

        if best_result:
            logger.info(
                f"最佳组合: {len(best_result.features)} 个特征, "
                f"相关性={best_result.correlation:.4f}, RMSE={best_result.rmse:.4f}"
            )

        return best_result

    def _evaluate_combination(
        self,
        features: list[FeatureResult],
        feature_data: pd.DataFrame,
        target: pd.Series,
    ) -> CombinedModelResult | None:
        """
        评估特征组合的效果

        Args:
            features: 特征列表
            feature_data: 特征数据
            target: 目标变量

        Returns:
            组合结果
        """
        # 计算权重（基于相关性绝对值）
        total_corr = sum(abs(f.correlation) for f in features)
        if total_corr == 0:
            logger.warning("总相关性为0，无法计算权重")
            return None

        weights = {f.feature_name: abs(f.correlation) / total_corr for f in features}

        # 计算加权预测值
        predictions = self._calculate_weighted_predictions(
            features, feature_data, weights
        )

        if predictions is None or predictions.empty:
            return None

        # 计算评估指标（只在共同索引上）
        common_index = predictions.index.intersection(target.index)
        if len(common_index) < 3:
            logger.warning("共同索引数量少于3个，无法评估")
            return None

        y_true = target.loc[common_index].values
        y_pred = predictions.loc[common_index].values

        # 计算相关系数和 RMSE
        correlation = float(np.corrcoef(y_pred, y_true)[0, 1])
        rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))

        # 构建特征元组列表
        feature_tuples = [
            (f.feature_name, weights[f.feature_name], f.a, f.b) for f in features
        ]

        return CombinedModelResult(
            features=feature_tuples,
            correlation=correlation,
            rmse=rmse,
            predictions=predictions,
        )

    def _calculate_weighted_predictions(
        self,
        features: list[FeatureResult],
        feature_data: pd.DataFrame,
        weights: dict[str, float],
    ) -> pd.Series | None:
        """
        计算加权预测值

        Args:
            features: 特征列表
            feature_data: 特征数据
            weights: 特征权重

        Returns:
            加权预测值
        """
        inverted_values: dict[str, pd.Series] = {}

        for feature in features:
            name = feature.feature_name
            x_data = feature_data[name].dropna()
            x_data = x_data[x_data > 0]

            if x_data.empty:
                continue

            # 应用幂函数: y = a * x^b
            inverted = feature.a * np.power(x_data.values, feature.b)
            inverted_values[name] = pd.Series(inverted, index=x_data.index)

        if not inverted_values:
            logger.warning("没有有效的预测值")
            return None

        # 找到共同索引
        common_indices = set.intersection(
            *[set(series.index) for series in inverted_values.values()]
        )

        if not common_indices:
            logger.warning("特征没有共同的有效索引")
            return None

        common_indices_list = sorted(list(common_indices))

        # 加权求和
        weighted_result = pd.Series(0.0, index=common_indices_list)
        for name, series in inverted_values.items():
            weighted_result += series.loc[common_indices_list] * weights[name]

        return weighted_result

    def predict(
        self,
        model_result: CombinedModelResult,
        feature_data: pd.DataFrame,
    ) -> pd.Series:
        """
        使用组合模型进行预测

        Args:
            model_result: 组合模型结果
            feature_data: 特征数据

        Returns:
            预测值
        """
        # 重建 FeatureResult 对象
        from ..core.types import PowerFitResult

        features = []
        weights = {}

        for name, w, a, b in model_result.features:
            fit_result = PowerFitResult(a=a, b=b, correlation=0, rmse=0, r2=0)
            features.append(FeatureResult(name, fit_result))
            weights[name] = w

        predictions = self._calculate_weighted_predictions(
            features, feature_data, weights
        )

        if predictions is None:
            return pd.Series(dtype=float)

        return predictions
