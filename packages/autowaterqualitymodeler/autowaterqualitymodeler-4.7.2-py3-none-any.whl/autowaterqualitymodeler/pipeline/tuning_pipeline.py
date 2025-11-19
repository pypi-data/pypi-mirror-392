"""
微调建模流水线

基于历史预测值进行线性微调。
"""

import logging

import numpy as np
import pandas as pd

from ..models.linear_fitter import LinearModelFitter

logger = logging.getLogger(__name__)


class TuningPipeline:
    """
    微调建模流水线

    基于历史预测值和新实测值进行线性微调。
    """

    def __init__(self):
        """初始化流水线"""
        self.fitter = LinearModelFitter()

    def run(
        self,
        old_predictions: pd.DataFrame,
        new_measurements: pd.DataFrame,
    ) -> tuple[dict[str, float], pd.DataFrame]:
        """
        执行微调流程

        Args:
            old_predictions: 旧模型的预测值
            new_measurements: 新的实测值

        Returns:
            (调整系数字典, 调整后的预测DataFrame)
            调整系数字典格式: {metric_name: A}
        """
        logger.info("开始模型微调")

        # 找到共同的指标
        common_metrics = list(
            set(old_predictions.columns) & set(new_measurements.columns)
        )

        if not common_metrics:
            logger.warning("预测数据和实测数据没有共同的指标")
            return {}, pd.DataFrame(index=new_measurements.index)

        logger.info(f"共同指标: {common_metrics}")

        coefficients: dict[str, float] = {}
        adjusted_predictions = pd.DataFrame(index=old_predictions.index)

        for metric_name in common_metrics:
            predicted = old_predictions[metric_name]
            measured = new_measurements[metric_name].dropna()

            # 获取对应索引的预测值
            common_idx = predicted.index.intersection(measured.index)
            if len(common_idx) < 2:
                logger.warning(f"指标 {metric_name} 共同索引数量不足，跳过")
                continue

            pred_values = predicted.loc[common_idx]
            meas_values = measured.loc[common_idx]

            # 执行线性微调
            a = self.fitter.fit(pred_values, meas_values)

            if a is None:
                logger.warning(f"指标 {metric_name} 微调失败")
                continue

            coefficients[metric_name] = a

            # 计算调整后的预测值
            adjusted = self.fitter.predict(predicted, a)
            adjusted_predictions[metric_name] = adjusted

            logger.info(f"指标 {metric_name} 微调完成: A={a:.4f}")

        # 将负值替换为 NaN
        adjusted_predictions = adjusted_predictions.where(
            adjusted_predictions >= 0, np.nan
        )

        logger.info(f"微调完成: {len(coefficients)} 个指标")
        return coefficients, adjusted_predictions
