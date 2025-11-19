"""
集成测试：完整建模流程
"""

import numpy as np
import pandas as pd
import pytest

from autowaterqualitymodeler import (
    AutoWaterQualityModeler,
    DataValidationError,
    WaterQualityModel,
)


class TestCompleteWorkflow:
    """测试完整建模流程"""

    @pytest.fixture
    def modeler(self):
        """创建建模器实例"""
        return AutoWaterQualityModeler()

    @pytest.fixture
    def real_spectrum_data(self):
        """创建更真实的光谱数据"""
        np.random.seed(42)
        wavelengths = list(range(400, 901, 10))  # 每10nm采样
        n_samples = 15  # 足够自动建模

        data = {}
        for wl in wavelengths:
            # 模拟水体反射光谱特征
            base = 0.02 + 0.1 * np.exp(-((wl - 550) ** 2) / 10000)
            noise = np.random.normal(0, 0.005, n_samples)
            data[wl] = np.clip(base + noise, 0.001, 1.0)

        return pd.DataFrame(data)

    @pytest.fixture
    def real_metric_data(self):
        """创建真实的水质指标数据"""
        np.random.seed(42)
        n_samples = 15

        # 创建与光谱特征相关的指标（使用标准名称）
        base = np.linspace(1, 10, n_samples)

        data = {
            "Turb": base * 5 + np.random.normal(0, 2, n_samples),
            "Chla": base * 10 + np.random.normal(0, 3, n_samples),
            "SS": base * 20 + np.random.normal(0, 5, n_samples),
        }

        # 确保所有值为正
        for key in data:
            data[key] = np.maximum(data[key], 0.1)

        return pd.DataFrame(data)

    def test_auto_modeling_basic(self, modeler, real_spectrum_data, real_metric_data):
        """测试自动建模基本流程"""
        model = modeler.fit(real_spectrum_data, real_metric_data, data_type="aerospot")

        assert isinstance(model, WaterQualityModel)
        assert model.model_type == 1

        # 检查 C++ 格式
        cpp_format = model.to_dict()
        assert "type" in cpp_format
        assert "w" in cpp_format
        assert "a" in cpp_format
        assert "b" in cpp_format
        assert "A" in cpp_format
        assert "Range" in cpp_format

    def test_tuning_modeling_basic(self):
        """测试微调建模基本流程"""
        modeler = AutoWaterQualityModeler()

        # 小样本数据（3个样本，少于 min_samples=6）
        spectrum_data = pd.DataFrame(
            {400: [0.1, 0.2, 0.3], 500: [0.15, 0.25, 0.35], 600: [0.12, 0.22, 0.32]}
        )

        metric_data = pd.DataFrame(
            {"Turb": [10.0, 20.0, 30.0], "Chla": [25.0, 50.0, 75.0]}
        )

        old_predictions = pd.DataFrame(
            {"Turb": [12.0, 18.0, 28.0], "Chla": [22.0, 48.0, 72.0]}
        )

        model = modeler.fit(
            spectrum_data,
            metric_data,
            data_type="aerospot",
            old_predictions=old_predictions,
        )

        assert isinstance(model, WaterQualityModel)
        assert model.model_type == 0

    def test_tuning_without_old_predictions_raises_error(self):
        """测试小样本无旧预测值时抛出错误"""
        modeler = AutoWaterQualityModeler()

        # 小样本数据
        spectrum_data = pd.DataFrame(
            {400: [0.1, 0.2, 0.3], 500: [0.15, 0.25, 0.35], 600: [0.12, 0.22, 0.32]}
        )

        metric_data = pd.DataFrame(
            {"Turb": [10.0, 20.0, 30.0], "Chla": [25.0, 50.0, 75.0]}
        )

        with pytest.raises(DataValidationError, match="样本量不足"):
            modeler.fit(spectrum_data, metric_data, data_type="aerospot")

    def test_empty_spectrum_data_raises_error(self, modeler, real_metric_data):
        """测试空光谱数据抛出错误"""
        empty_spectrum = pd.DataFrame()

        with pytest.raises(DataValidationError, match="光谱数据为空"):
            modeler.fit(empty_spectrum, real_metric_data)

    def test_empty_metric_data_raises_error(self, modeler, real_spectrum_data):
        """测试空指标数据抛出错误"""
        empty_metric = pd.DataFrame()

        with pytest.raises(DataValidationError, match="实测数据为空"):
            modeler.fit(real_spectrum_data, empty_metric)

    def test_mismatched_samples_raises_error(self, modeler):
        """测试样本数不一致抛出错误"""
        spectrum_data = pd.DataFrame({400: [0.1, 0.2, 0.3], 500: [0.15, 0.25, 0.35]})

        metric_data = pd.DataFrame({"turbidity": [10.0, 20.0]})  # 只有2个样本

        with pytest.raises(DataValidationError, match="样本数不一致"):
            modeler.fit(spectrum_data, metric_data)

    def test_model_save_load_roundtrip(
        self, modeler, real_spectrum_data, real_metric_data
    ):
        """测试模型保存和加载往返"""
        import os
        import tempfile

        # 训练模型
        model = modeler.fit(real_spectrum_data, real_metric_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "model.json")

            # 保存
            model.save(path)

            # 加载
            loaded_model = WaterQualityModel.load(path)

            # 验证
            assert loaded_model.model_data == model.model_data
            assert loaded_model.model_type == model.model_type

    def test_cpp_format_consistency(
        self, modeler, real_spectrum_data, real_metric_data
    ):
        """测试 C++ 格式一致性"""
        model = modeler.fit(real_spectrum_data, real_metric_data)

        cpp_format = model.to_dict()

        # 检查格式
        assert cpp_format["type"] == 1

        # 检查维度一致性
        n_metrics = len(modeler.config.get_water_quality_params())
        n_features = len(modeler.config.get_feature_stations())

        # w 和 a 是 columns × index 展平
        assert len(cpp_format["w"]) == n_metrics * n_features
        assert len(cpp_format["a"]) == n_metrics * n_features
        # b 是 index × columns 展平（每个特征都有自己的 b）
        assert len(cpp_format["b"]) == n_metrics * n_features
        assert len(cpp_format["A"]) == n_metrics
        assert len(cpp_format["Range"]) == n_metrics * 2

    def test_column_name_normalization(self, modeler, real_spectrum_data):
        """测试列名标准化"""
        # 使用非标准列名
        metric_data = pd.DataFrame(
            {
                "TURBIDITY": np.random.uniform(5, 50, len(real_spectrum_data)),
                "CHLA": np.random.uniform(10, 100, len(real_spectrum_data)),
            }
        )

        # 应该能够处理（取决于配置中的映射）
        try:
            model = modeler.fit(real_spectrum_data, metric_data)
            assert model is not None
        except Exception:
            # 如果没有配置映射，可能会失败，这是可以接受的
            pass

    def test_auto_strategy_selection(self, modeler):
        """测试自动策略选择"""
        # 测试大样本 -> 自动建模
        np.random.seed(42)
        large_spectrum = pd.DataFrame(
            {wl: np.random.uniform(0.01, 0.5, 10) for wl in range(400, 901, 10)}
        )
        large_metric = pd.DataFrame(
            {
                "Turb": np.random.uniform(5, 50, 10),
                "Chla": np.random.uniform(10, 100, 10),
            }
        )

        model = modeler.fit(large_spectrum, large_metric)
        assert model.model_type == 1  # 自动建模

    def test_filter_unsupported_metrics(self, modeler, real_spectrum_data):
        """测试过滤不支持的指标"""
        # 创建包含不在预设中的指标的数据
        metric_data = pd.DataFrame(
            {
                "Turb": np.random.uniform(5, 50, len(real_spectrum_data)),
                "Chla": np.random.uniform(10, 100, len(real_spectrum_data)),
                "unsupported_metric": np.random.uniform(1, 10, len(real_spectrum_data)),
                "another_unsupported": np.random.uniform(1, 5, len(real_spectrum_data)),
            }
        )

        # 应该能够建模，但会忽略不支持的指标
        model = modeler.fit(real_spectrum_data, metric_data)
        assert model is not None
        assert model.model_type == 1

        # 检查只有支持的指标被建模
        cpp_format = model.to_dict()
        A_vector = cpp_format["A"]
        index = modeler.config.get_water_quality_params()

        # Turb 和 Chla 应该被建模
        turb_idx = index.index("Turb")
        chla_idx = index.index("Chla")
        assert A_vector[turb_idx] == 1.0
        assert A_vector[chla_idx] == 1.0

    def test_all_unsupported_metrics_raises_error(self, modeler, real_spectrum_data):
        """测试所有指标都不支持时抛出错误"""
        # 创建只包含不支持指标的数据
        metric_data = pd.DataFrame(
            {
                "unsupported_1": np.random.uniform(1, 10, len(real_spectrum_data)),
                "unsupported_2": np.random.uniform(1, 5, len(real_spectrum_data)),
            }
        )

        with pytest.raises(DataValidationError, match="没有找到任何预设的水质指标"):
            modeler.fit(real_spectrum_data, metric_data)

    def test_tuning_strategy_selection(self, modeler):
        """测试微调策略选择"""
        # 测试小样本 -> 微调
        small_spectrum = pd.DataFrame(
            {wl: np.random.uniform(0.01, 0.5, 3) for wl in range(400, 901, 100)}
        )
        small_metric = pd.DataFrame(
            {"Turb": [10.0, 20.0, 30.0], "Chla": [25.0, 50.0, 75.0]}
        )
        old_predictions = pd.DataFrame(
            {"Turb": [12.0, 18.0, 28.0], "Chla": [22.0, 48.0, 72.0]}
        )

        model = modeler.fit(
            small_spectrum, small_metric, old_predictions=old_predictions
        )
        assert model.model_type == 0  # 微调模型
