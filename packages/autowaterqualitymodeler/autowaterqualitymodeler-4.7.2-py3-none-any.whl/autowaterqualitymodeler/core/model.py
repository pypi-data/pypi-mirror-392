"""
水质模型类

封装训练好的模型，提供预测、保存、加载功能。
"""

import json
import logging
import os

import numpy as np
import pandas as pd

from ..features.calculator import FeatureCalculator
from ..preprocessing.spectrum_processor import SpectrumProcessor
from .config import Config

logger = logging.getLogger(__name__)


class WaterQualityModel:
    """
    水质模型

    封装训练好的模型参数，提供预测功能。
    使用 C++ 格式存储模型参数。
    """

    def __init__(
        self,
        model_data: dict,
        config_path: str | None = None,
        data_type: str = "aerospot",
        min_wavelength: int = 400,
        max_wavelength: int = 900,
        smooth_window: int = 11,
        smooth_order: int = 3,
    ):
        """
        初始化模型

        Args:
            model_data: C++ 格式的模型数据
            config_path: 配置文件路径（用于预测时计算特征）
            data_type: 数据类型
            min_wavelength: 最小波长 (nm)
            max_wavelength: 最大波长 (nm)
            smooth_window: 平滑窗口大小
            smooth_order: 平滑多项式阶数
        """
        self.model_data = model_data
        self.model_type = model_data.get("type", 1)
        self.data_type = data_type
        self.config = Config(config_path)

        # 初始化预处理器
        self.preprocessor = SpectrumProcessor(
            min_wavelength=min_wavelength,
            max_wavelength=max_wavelength,
            smooth_window=smooth_window,
            smooth_order=smooth_order,
        )

        # 加载三刺激值系数
        tris_coeff = self._load_tris_coefficients()
        self.calculator = FeatureCalculator(tris_coeff=tris_coeff)

        logger.info(f"加载模型: type={self.model_type}")

    def _load_tris_coefficients(self) -> pd.DataFrame:
        """加载三刺激值系数表"""
        try:
            tris_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "resources",
                "D65xCIE.xlsx",
            )
            return pd.read_excel(tris_path, header=0, index_col=0)
        except Exception:
            return pd.DataFrame()

    def predict(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """
        对新数据进行预测

        Args:
            spectrum_data: 光谱数据（预处理后）

        Returns:
            预测结果 DataFrame
        """
        if self.model_type == 1:
            return self._predict_auto(spectrum_data)
        else:
            # 微调模型需要传入旧预测值，不是光谱数据
            raise ValueError(
                "微调模型 (type=0) 不能直接预测光谱数据，"
                "请传入旧模型的预测值并使用 predict_tuning()"
            )

    def predict_unified(
        self,
        spectrum_data: pd.DataFrame | None = None,
        old_predictions: pd.DataFrame | None = None,
        preprocess: bool = True,
    ) -> pd.DataFrame:
        """
        统一预测接口

        根据模型类型自动选择预测策略：
        - type=1 (自动建模): 使用光谱数据，自动预处理 → 提取特征 → w,a,b 矩阵计算
        - type=0 (微调模型): 使用原始反演数据，与 A 系数相乘

        Args:
            spectrum_data: 光谱数据（原始或预处理后）
            old_predictions: 旧模型的预测值（原始反演数据）
            preprocess: 是否对光谱数据进行预处理（仅 type=1 有效）

        Returns:
            预测结果 DataFrame

        Raises:
            ValueError: 输入数据不满足模型类型要求时

        Examples:
            >>> # type=1 模型预测
            >>> model = WaterQualityModel.load("auto_model.json")
            >>> predictions = model.predict_unified(spectrum_data=raw_spectrum)

            >>> # type=0 模型预测
            >>> tuning_model = WaterQualityModel.load("tuning_model.json")
            >>> predictions = tuning_model.predict_unified(old_predictions=old_results)
        """
        if self.model_type == 1:
            # 自动建模模型：需要光谱数据
            if spectrum_data is None:
                raise ValueError(
                    "自动建模模型 (type=1) 必须提供光谱数据。"
                    "请使用 spectrum_data 参数传入光谱数据。"
                )

            # 预处理光谱数据
            if preprocess:
                logger.info("正在预处理光谱数据...")
                try:
                    processed_spectrum = self.preprocessor.preprocess(spectrum_data)
                    logger.debug(
                        f"预处理完成: {spectrum_data.shape} → {processed_spectrum.shape}"
                    )
                except Exception as e:
                    logger.error(f"光谱预处理失败: {e}", exc_info=True)
                    raise ValueError(f"光谱预处理失败: {e}")
            else:
                processed_spectrum = spectrum_data
                logger.info("跳过预处理，使用已预处理的光谱数据")

            # 执行预测
            return self._predict_auto(processed_spectrum)

        elif self.model_type == 0:
            # 微调模型：需要旧预测值
            if old_predictions is None:
                raise ValueError(
                    "微调模型 (type=0) 必须提供旧模型的预测值。"
                    "请使用 old_predictions 参数传入原始反演数据。"
                )

            return self.predict_tuning(old_predictions)

        else:
            raise ValueError(f"未知的模型类型: {self.model_type}")

    def predict_tuning(self, old_predictions: pd.DataFrame) -> pd.DataFrame:
        """
        使用微调模型进行预测

        Args:
            old_predictions: 旧模型的预测值

        Returns:
            调整后的预测值
        """
        if self.model_type != 0:
            raise ValueError("此方法仅适用于微调模型 (type=0)")

        A_vector = self.model_data.get("A", [])
        index = self.config.get_water_quality_params()

        predictions = pd.DataFrame(index=old_predictions.index)

        for i, metric_name in enumerate(index):
            if i >= len(A_vector):
                break

            a_value = A_vector[i]
            if a_value == -1:
                # 未微调的指标
                continue

            if metric_name in old_predictions.columns:
                predictions[metric_name] = old_predictions[metric_name] * a_value

        # 将负值替换为 NaN
        predictions = predictions.where(predictions >= 0, np.nan)

        return predictions

    def _predict_auto(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """自动建模模型的预测"""
        index = self.config.get_water_quality_params()
        columns = self.config.get_feature_stations()

        # 从扁平数组重建矩阵
        w_flat = self.model_data.get("w", [])
        a_flat = self.model_data.get("a", [])
        b_flat = self.model_data.get("b", [])
        A_vector = self.model_data.get("A", [])

        if not w_flat or not a_flat or not b_flat:
            logger.error("模型数据不完整")
            return pd.DataFrame(index=spectrum_data.index)

        # 重建矩阵
        # w 和 a: 扁平化是 columns × index (转置后展平)
        # b: 扁平化是 index × columns (不转置)
        n_metrics = len(index)
        n_features = len(columns)

        w_matrix = np.array(w_flat).reshape(n_features, n_metrics).T  # index × columns
        a_matrix = np.array(a_flat).reshape(n_features, n_metrics).T
        b_matrix = np.array(b_flat).reshape(n_metrics, n_features)  # index × columns

        predictions = pd.DataFrame(index=spectrum_data.index)

        # 对每个已建模的指标进行预测
        for i, metric_name in enumerate(index):
            if i >= len(A_vector) or A_vector[i] == -1:
                continue  # 未建模的指标

            # 获取该指标使用的特征
            metric_weights = w_matrix[i, :]
            metric_a = a_matrix[i, :]
            metric_b = b_matrix[i, :]

            # 找到非零权重的特征
            active_features = np.where(metric_weights != 0)[0]

            if len(active_features) == 0:
                continue

            # 计算特征值
            feature_defs = self.config.get_feature_definitions(
                self.data_type, metric_name
            )
            if not feature_defs:
                logger.warning(f"指标 {metric_name} 没有特征定义")
                continue

            features = self.calculator.calculate_features(spectrum_data, feature_defs)

            # 加权求和
            weighted_sum = pd.Series(0.0, index=spectrum_data.index)

            for j in active_features:
                if j >= len(columns):
                    continue

                feature_name = columns[j]
                if feature_name not in features.columns:
                    continue

                w = metric_weights[j]
                a = metric_a[j]
                b = metric_b[j]

                # y = w * a * x^b
                x = features[feature_name]
                x_positive = x[x > 0]
                if x_positive.empty:
                    continue

                y = a * np.power(x_positive.values, b)
                weighted_sum.loc[x_positive.index] += w * y

            predictions[metric_name] = weighted_sum

        return predictions

    def get_supported_metrics(self) -> list[str]:
        """获取模型支持的指标列表"""
        index = self.config.get_water_quality_params()
        A_vector = self.model_data.get("A", [])

        supported = []
        for i, metric_name in enumerate(index):
            if i < len(A_vector) and A_vector[i] != -1:
                supported.append(metric_name)

        return supported

    def to_dict(self) -> dict:
        """返回 C++ 格式的模型数据"""
        return self.model_data

    def save(self, path: str) -> None:
        """
        保存模型到文件

        Args:
            path: 保存路径（JSON 格式）
        """
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_data, f, ensure_ascii=False, indent=2)

        logger.info(f"模型已保存到: {path}")

    @classmethod
    def load(
        cls,
        path: str,
        config_path: str | None = None,
        data_type: str = "aerospot",
        min_wavelength: int = 400,
        max_wavelength: int = 900,
        smooth_window: int = 11,
        smooth_order: int = 3,
    ) -> "WaterQualityModel":
        """
        从文件加载模型

        Args:
            path: 模型文件路径
            config_path: 配置文件路径
            data_type: 数据类型
            min_wavelength: 最小波长 (nm)
            max_wavelength: 最大波长 (nm)
            smooth_window: 平滑窗口大小
            smooth_order: 平滑多项式阶数

        Returns:
            WaterQualityModel 实例
        """
        with open(path, "r", encoding="utf-8") as f:
            model_data = json.load(f)

        logger.info(f"从 {path} 加载模型")
        return cls(
            model_data,
            config_path,
            data_type,
            min_wavelength,
            max_wavelength,
            smooth_window,
            smooth_order,
        )
