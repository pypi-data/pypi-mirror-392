"""
结果格式化器

将建模结果格式化为 C++ 所需的系数矩阵格式。
"""

import logging

import pandas as pd

from ..core.config import Config

logger = logging.getLogger(__name__)


class ResultFormatter:
    """
    结果格式化器

    将建模结果转换为 C++ 程序所需的格式。
    """

    def __init__(self, config: Config):
        """
        初始化格式化器

        Args:
            config: 配置对象
        """
        self.config = config

    def format_auto_model(
        self,
        models: dict[str, dict],
        metric_data: pd.DataFrame,
    ) -> dict:
        """
        格式化自动建模结果

        Args:
            models: 模型字典 {metric_name: {feature_name: {w, a, b}}}
            metric_data: 实测指标数据（用于计算 Range）

        Returns:
            C++ 格式的结果字典
        """
        index = self.config.get_water_quality_params()
        columns = self.config.get_feature_stations()

        if not index or not columns:
            logger.error("系统配置中未设置指标名称或特征名称")
            raise ValueError("配置缺失: water_quality_params 或 feature_stations")

        # 创建系数矩阵
        w_matrix = pd.DataFrame(0.0, index=index, columns=columns, dtype=float)
        a_matrix = pd.DataFrame(0.0, index=index, columns=columns, dtype=float)
        b_matrix = pd.DataFrame(0.0, index=index, columns=columns, dtype=float)
        A_vector = pd.DataFrame(-1.0, index=index, columns=["A"], dtype=float)
        range_matrix = pd.DataFrame(0.0, index=index, columns=["m", "n"], dtype=float)

        # 填充系数矩阵
        for metric_name, feature_dict in models.items():
            if metric_name not in index:
                logger.warning(f"指标 {metric_name} 不在配置中，跳过")
                continue

            for feature_name, params in feature_dict.items():
                if feature_name not in columns:
                    logger.warning(f"特征 {feature_name} 不在配置中，跳过")
                    continue

                w_matrix.loc[metric_name, feature_name] = params["w"]
                a_matrix.loc[metric_name, feature_name] = params["a"]
                b_matrix.loc[metric_name, feature_name] = params["b"]

            # 标记该指标已建模
            A_vector.loc[metric_name, "A"] = 1.0

        # 计算指标范围
        self._fill_range_matrix(range_matrix, metric_data)

        # 转换为扁平列表
        result = {
            "type": 1,
            "w": w_matrix.values.T.flatten().tolist(),  # columns × index
            "a": a_matrix.values.T.flatten().tolist(),
            "b": b_matrix.values.flatten().tolist(),  # index × columns (不转置)
            "A": A_vector.values.flatten().tolist(),
            "Range": range_matrix.values.flatten().tolist(),
        }

        logger.info(f"格式化完成: type=1, 建模指标数={int((A_vector['A'] == 1).sum())}")
        return result

    def format_tuning_model(
        self,
        coefficients: dict[str, float],
        metric_data: pd.DataFrame,
    ) -> dict:
        """
        格式化微调建模结果

        Args:
            coefficients: 调整系数字典 {metric_name: A}
            metric_data: 实测指标数据

        Returns:
            C++ 格式的结果字典
        """
        index = self.config.get_water_quality_params()

        if not index:
            logger.error("系统配置中未设置指标名称")
            raise ValueError("配置缺失: water_quality_params")

        # 创建 A 向量
        A_vector = pd.DataFrame(-1.0, index=index, columns=["A"], dtype=float)
        range_matrix = pd.DataFrame(0.0, index=index, columns=["m", "n"], dtype=float)

        # 填充 A 系数
        for metric_name, a_value in coefficients.items():
            if metric_name in index:
                A_vector.loc[metric_name, "A"] = a_value
            else:
                logger.warning(f"指标 {metric_name} 不在配置中，跳过")

        # 计算指标范围
        self._fill_range_matrix(range_matrix, metric_data)

        # 转换为扁平列表
        result = {
            "type": 0,
            "A": A_vector.values.flatten().tolist(),
            "Range": range_matrix.values.flatten().tolist(),
        }

        logger.info(f"格式化完成: type=0, 微调指标数={len(coefficients)}")
        return result

    def _fill_range_matrix(
        self,
        range_matrix: pd.DataFrame,
        metric_data: pd.DataFrame,
    ) -> None:
        """
        填充指标范围矩阵

        Args:
            range_matrix: 范围矩阵 (m, n 列)
            metric_data: 实测指标数据
        """
        for metric_name in range_matrix.index:
            if metric_name not in metric_data.columns:
                continue

            values = metric_data[metric_name].dropna()
            if values.empty:
                continue

            min_val = values.min()
            max_val = values.max()
            std_val = values.std()

            if min_val == max_val:
                logger.warning(f"指标 {metric_name} 上下限相同，样本量可能太少")
                std_val = 0

            # 下限: max(0, min - 3*std)
            range_down = max(0, min_val - std_val * 3)
            # 上限: max + 3*std
            range_up = max_val + std_val * 3

            range_matrix.loc[metric_name, "m"] = range_down
            range_matrix.loc[metric_name, "n"] = range_up

            logger.debug(f"{metric_name} Range: {range_down:.4f} - {range_up:.4f}")
