"""
自动建模流水线

编排完整的自动建模流程。
"""

import logging
import os

import pandas as pd

from ..core.config import Config
from ..core.types import CombinedModelResult
from ..features.calculator import FeatureCalculator
from ..features.selector import FeatureSelector
from ..models.combiner import ModelCombiner

logger = logging.getLogger(__name__)


class AutoPipeline:
    """
    自动建模流水线

    编排特征计算、特征选择、模型组合的完整流程。
    """

    def __init__(self, config: Config):
        """
        初始化流水线

        Args:
            config: 配置对象
        """
        self.config = config

        # 加载三刺激值系数
        tris_coeff = self._load_tris_coefficients()

        # 初始化组件
        self.calculator = FeatureCalculator(tris_coeff=tris_coeff)
        self.selector = FeatureSelector()
        self.combiner = ModelCombiner()

    def _load_tris_coefficients(self) -> pd.DataFrame:
        """加载三刺激值系数表"""
        try:
            tris_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "resources",
                "D65xCIE.xlsx",
            )
            tris_coeff = pd.read_excel(tris_path, header=0, index_col=0)
            logger.info(f"加载三刺激值系数表: {tris_path}")
            return tris_coeff
        except Exception as e:
            logger.warning(f"加载三刺激值系数表失败: {e}")
            return pd.DataFrame()

    def run(
        self,
        spectrum_data: pd.DataFrame,
        metric_data: pd.DataFrame,
        data_type: str,
        max_features: int = 5,
    ) -> tuple[dict[str, dict], pd.DataFrame]:
        """
        执行自动建模流程

        Args:
            spectrum_data: 预处理后的光谱数据
            metric_data: 实测指标数据
            data_type: 数据类型
            max_features: 最大特征数

        Returns:
            (模型字典, 预测结果DataFrame)
            模型字典格式: {metric_name: {feature_name: {w, a, b}}}
        """
        logger.info(f"开始自动建模: {len(metric_data.columns)} 个指标")

        models: dict[str, dict] = {}
        predictions = pd.DataFrame(index=metric_data.index)

        for metric_name in metric_data.columns:
            # 跳过所有值相同的指标
            if metric_data[metric_name].nunique() == 1:
                logger.warning(f"指标 {metric_name} 所有值相同，跳过")
                continue

            try:
                result = self._build_metric_model(
                    spectrum_data,
                    metric_data[metric_name].dropna(),
                    data_type,
                    metric_name,
                    max_features,
                )

                if result:
                    models[metric_name] = result.to_dict()
                    predictions[metric_name] = result.predictions

                    logger.info(
                        f"指标 {metric_name} 建模完成: "
                        f"{len(result.features)} 个特征, "
                        f"相关性={result.correlation:.4f}"
                    )

            except Exception as e:
                logger.error(f"指标 {metric_name} 建模失败: {e}", exc_info=True)
                continue

        logger.info(f"自动建模完成: 成功建模 {len(models)} 个指标")
        return models, predictions

    def _build_metric_model(
        self,
        spectrum_data: pd.DataFrame,
        metric_series: pd.Series,
        data_type: str,
        metric_name: str,
        max_features: int,
    ) -> CombinedModelResult | None:
        """
        为单个指标构建模型

        Args:
            spectrum_data: 光谱数据
            metric_series: 指标数据
            data_type: 数据类型
            metric_name: 指标名称
            max_features: 最大特征数

        Returns:
            组合模型结果
        """
        # 1. 获取特征定义并计算特征
        feature_defs = self.config.get_feature_definitions(data_type, metric_name)
        if not feature_defs:
            logger.warning(f"指标 {metric_name} 没有特征定义")
            return None

        features = self.calculator.calculate_features(spectrum_data, feature_defs)
        if features.empty:
            logger.warning(f"指标 {metric_name} 特征计算结果为空")
            return None

        logger.debug(f"指标 {metric_name} 计算了 {len(features.columns)} 个特征")

        # 2. 选择最佳特征
        selected = self.selector.select_top_features(
            features, metric_series, max_features
        )
        if not selected:
            logger.warning(f"指标 {metric_name} 无法选择有效特征")
            return None

        # 3. 组合模型
        combined = self.combiner.find_best_combination(
            selected, features, metric_series
        )
        return combined
