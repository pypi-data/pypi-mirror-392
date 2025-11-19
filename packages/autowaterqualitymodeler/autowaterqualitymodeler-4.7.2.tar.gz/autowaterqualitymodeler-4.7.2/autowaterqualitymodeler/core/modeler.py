"""
自动水质建模器主模块

提供简洁的公开 API。
"""

import logging

import pandas as pd

from ..pipeline.auto_pipeline import AutoPipeline
from ..pipeline.formatter import ResultFormatter
from ..pipeline.tuning_pipeline import TuningPipeline
from ..preprocessing.spectrum_processor import SpectrumProcessor
from .config import Config
from .exceptions import DataValidationError, ModelingError
from .model import WaterQualityModel

logger = logging.getLogger(__name__)


class AutoWaterQualityModeler:
    """
    自动水质建模器

    提供一键式水质建模功能。

    使用示例:
        ```python
        modeler = AutoWaterQualityModeler()

        # 自动建模
        model = modeler.fit(spectrum_data, metric_data, "aerospot")

        # 统一预测接口（推荐使用）
        predictions = model.predict_unified(spectrum_data=new_spectrum_data)

        # 传统预测方式（需手动预处理）
        preprocessed = modeler.preprocessor.preprocess(new_spectrum_data)
        predictions = model.predict(preprocessed)

        # 保存模型
        model.save("model.json")

        # 获取 C++ 格式
        cpp_format = model.to_dict()
        ```
    """

    def __init__(
        self,
        config_path: str | None = None,
        min_wavelength: int = 400,
        max_wavelength: int = 900,
        smooth_window: int = 11,
        smooth_order: int = 3,
    ):
        """
        初始化建模器

        Args:
            config_path: 配置文件路径
            min_wavelength: 最小波长 (nm)
            max_wavelength: 最大波长 (nm)
            smooth_window: 平滑窗口大小
            smooth_order: 平滑多项式阶数
        """
        self.config_path = config_path
        self.config = Config(config_path)

        # 初始化组件
        self.preprocessor = SpectrumProcessor(
            min_wavelength=min_wavelength,
            max_wavelength=max_wavelength,
            smooth_window=smooth_window,
            smooth_order=smooth_order,
        )
        self.auto_pipeline = AutoPipeline(self.config)
        self.tuning_pipeline = TuningPipeline()
        self.formatter = ResultFormatter(self.config)

        # 保存参数
        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength

        logger.info("初始化 AutoWaterQualityModeler")

    def fit(
        self,
        spectrum_data: pd.DataFrame,
        metric_data: pd.DataFrame,
        data_type: str = "aerospot",
        old_predictions: pd.DataFrame | None = None,
    ) -> WaterQualityModel:
        """
        自动建模（根据样本量自动选择策略）

        Args:
            spectrum_data: 光谱数据（行为样本，列为波长）
            metric_data: 实测指标数据（行为样本，列为指标）
            data_type: 数据类型
            old_predictions: 旧模型的预测值（样本量不足时用于微调）

        Returns:
            训练好的 WaterQualityModel 对象

        Raises:
            DataValidationError: 数据验证失败
            ModelingError: 建模失败
        """
        logger.info(
            f"开始建模: samples={len(spectrum_data)}, "
            f"metrics={len(metric_data.columns)}, data_type={data_type}"
        )

        try:
            # 1. 数据验证
            self._validate_inputs(spectrum_data, metric_data)

            # 2. 标准化列名
            logger.info("标准化列名...")
            metric_data = self.config.normalize_dataframe_columns(metric_data)
            metric_data = self._prepare_metric_data(metric_data)

            if old_predictions is not None:
                old_predictions = self.config.normalize_dataframe_columns(
                    old_predictions
                )
                old_predictions = self._prepare_metric_data(old_predictions)

            # 3. 获取模型参数
            model_params = self.config.get_model_params(data_type)
            min_samples = model_params.get("min_samples", 6)
            max_features = model_params.get("max_features", 5)

            # 4. 根据样本量选择策略
            if len(metric_data) >= min_samples:
                logger.info(
                    f"样本量足够 ({len(metric_data)} >= {min_samples})，使用自动建模策略"
                )
                return self._fit_auto(
                    spectrum_data, metric_data, data_type, max_features
                )
            else:
                logger.info(
                    f"样本量不足 ({len(metric_data)} < {min_samples})，使用微调策略"
                )
                if old_predictions is None:
                    raise DataValidationError(
                        f"样本量不足 ({len(metric_data)} < {min_samples})，"
                        "必须提供 old_predictions 参数用于微调"
                    )
                return self._fit_tuning(old_predictions, metric_data)

        except DataValidationError:
            raise
        except Exception as e:
            logger.error(f"建模失败: {e}", exc_info=True)
            raise ModelingError(f"建模失败: {e}")

    def _fit_auto(
        self,
        spectrum_data: pd.DataFrame,
        metric_data: pd.DataFrame,
        data_type: str,
        max_features: int,
    ) -> WaterQualityModel:
        """执行自动建模策略"""
        # 1. 预处理光谱数据
        logger.info("预处理光谱数据...")
        processed_spectrum = self.preprocessor.preprocess(spectrum_data)

        # 2. 执行自动建模
        logger.info("执行自动建模流水线...")
        models, predictions = self.auto_pipeline.run(
            processed_spectrum, metric_data, data_type, max_features
        )

        if not models:
            raise ModelingError("没有成功建模任何指标")

        # 3. 格式化为 C++ 格式
        logger.info("格式化模型结果...")
        cpp_format = self.formatter.format_auto_model(models, metric_data)

        # 4. 创建模型对象（传递预处理器参数）
        model = WaterQualityModel(
            cpp_format,
            self.config_path,
            data_type,
            self.min_wavelength,
            self.max_wavelength,
            self.preprocessor.smooth_window,
            self.preprocessor.smooth_order,
        )

        logger.info(f"自动建模完成: {len(model.get_supported_metrics())} 个指标")
        return model

    def _fit_tuning(
        self,
        old_predictions: pd.DataFrame,
        new_measurements: pd.DataFrame,
    ) -> WaterQualityModel:
        """执行微调策略"""
        # 1. 执行微调
        logger.info("执行微调流水线...")
        coefficients, adjusted_predictions = self.tuning_pipeline.run(
            old_predictions, new_measurements
        )

        if not coefficients:
            raise ModelingError("没有成功微调任何指标")

        # 2. 格式化为 C++ 格式
        logger.info("格式化微调结果...")
        cpp_format = self.formatter.format_tuning_model(coefficients, new_measurements)

        # 3. 创建模型对象（传递预处理器参数）
        model = WaterQualityModel(
            cpp_format,
            self.config_path,
            "aerospot",
            self.min_wavelength,
            self.max_wavelength,
            self.preprocessor.smooth_window,
            self.preprocessor.smooth_order,
        )

        logger.info(f"微调完成: {len(coefficients)} 个指标")
        return model

    def _validate_inputs(
        self,
        spectrum_data: pd.DataFrame,
        metric_data: pd.DataFrame,
    ) -> None:
        """验证输入数据"""
        if spectrum_data is None or spectrum_data.empty:
            raise DataValidationError("光谱数据为空")

        if metric_data is None or metric_data.empty:
            raise DataValidationError("实测数据为空")

        if len(spectrum_data) != len(metric_data):
            raise DataValidationError(
                f"光谱数据({len(spectrum_data)}条)与"
                f"实测数据({len(metric_data)}条)样本数不一致"
            )

    def _prepare_metric_data(self, metric_data: pd.DataFrame) -> pd.DataFrame:
        """
        准备实测数据，移除不需要的列并只保留预设的水质指标

        Args:
            metric_data: 原始实测数据

        Returns:
            过滤后的实测数据，只包含预设的水质指标
        """
        # 1. 移除辅助列
        columns_to_drop = [
            "index",
            "latitude",
            "longitude",
            "Latitude",
            "Longitude",
        ]
        cleaned_data = metric_data.drop(columns=columns_to_drop, errors="ignore")

        # 2. 获取预设的水质指标列表
        valid_metrics = set(self.config.get_water_quality_params())

        # 3. 找出不在预设中的指标
        current_metrics = set(cleaned_data.columns)
        unsupported_metrics = current_metrics - valid_metrics

        # 4. 警告用户不支持的指标
        if unsupported_metrics:
            logger.warning(
                f"以下指标不在预设的水质参数中，将被忽略: {sorted(unsupported_metrics)}"
            )

        # 5. 只保留预设的指标（保持原始顺序）
        valid_columns = [col for col in cleaned_data.columns if col in valid_metrics]

        if not valid_columns:
            raise DataValidationError(
                f"没有找到任何预设的水质指标。"
                f"预设指标: {sorted(valid_metrics)}, "
                f"实际指标: {sorted(current_metrics)}"
            )

        logger.info(f"保留 {len(valid_columns)} 个预设指标: {valid_columns}")

        return cleaned_data[valid_columns]
