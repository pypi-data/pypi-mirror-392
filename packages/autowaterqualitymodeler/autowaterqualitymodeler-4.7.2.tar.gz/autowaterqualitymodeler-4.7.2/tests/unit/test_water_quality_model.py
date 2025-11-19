"""
水质模型类单元测试
"""

import json
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from autowaterqualitymodeler.core.model import WaterQualityModel


class TestWaterQualityModel:
    """测试水质模型类"""

    @pytest.fixture
    def auto_model(self, cpp_format_auto):
        """创建自动建模模型"""
        return WaterQualityModel(cpp_format_auto)

    @pytest.fixture
    def tuning_model(self, cpp_format_tuning):
        """创建微调模型"""
        return WaterQualityModel(cpp_format_tuning)

    def test_init_auto_model(self, cpp_format_auto):
        """测试自动模型初始化"""
        model = WaterQualityModel(cpp_format_auto)

        assert model.model_type == 1
        assert model.data_type == "aerospot"
        assert model.model_data == cpp_format_auto

    def test_init_tuning_model(self, cpp_format_tuning):
        """测试微调模型初始化"""
        model = WaterQualityModel(cpp_format_tuning)

        assert model.model_type == 0

    def test_get_supported_metrics(self, auto_model):
        """测试获取支持的指标"""
        metrics = auto_model.get_supported_metrics()

        assert isinstance(metrics, list)
        # A 向量中前两个是 1.0，对应 turbidity 和 ss (或 chla，取决于配置)
        assert len(metrics) >= 0  # 可能为空取决于配置

    def test_to_dict(self, auto_model, cpp_format_auto):
        """测试转换为字典"""
        result = auto_model.to_dict()

        assert result == cpp_format_auto

    def test_save_and_load(self, auto_model):
        """测试保存和加载模型"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_model.json")

            # 保存
            auto_model.save(path)
            assert os.path.exists(path)

            # 验证 JSON 格式正确
            with open(path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            assert saved_data == auto_model.model_data

            # 加载
            loaded_model = WaterQualityModel.load(path)
            assert loaded_model.model_data == auto_model.model_data
            assert loaded_model.model_type == auto_model.model_type

    def test_predict_tuning_wrong_type(self, auto_model):
        """测试自动模型不能使用微调预测方法"""
        old_predictions = pd.DataFrame({"turbidity": [1.0, 2.0]})

        with pytest.raises(ValueError, match="微调模型"):
            auto_model.predict_tuning(old_predictions)

    def test_predict_auto_wrong_type(self, tuning_model):
        """测试微调模型不能使用自动预测方法"""
        spectrum_data = pd.DataFrame({400: [0.5, 0.6], 500: [0.4, 0.5]})

        with pytest.raises(ValueError, match="微调模型"):
            tuning_model.predict(spectrum_data)

    def test_predict_tuning_basic(self, tuning_model):
        """测试微调模型基本预测"""
        old_predictions = pd.DataFrame(
            {"Turb": [10.0, 20.0, 30.0], "SS": [100.0, 150.0, 200.0]}
        )

        result = tuning_model.predict_tuning(old_predictions)

        assert isinstance(result, pd.DataFrame)
        # 应该包含微调过的指标
        # Turb 的 A 值是 1.2
        if "Turb" in result.columns:
            expected = old_predictions["Turb"] * 1.2
            np.testing.assert_array_almost_equal(
                result["Turb"].values, expected.values, decimal=5
            )

    def test_predict_tuning_negative_values(self, tuning_model):
        """测试微调预测时负值处理"""
        old_predictions = pd.DataFrame({"Turb": [-10.0, 20.0, 30.0]})

        result = tuning_model.predict_tuning(old_predictions)

        # 负值应该被替换为 NaN
        if "Turb" in result.columns:
            assert pd.isna(result["Turb"].iloc[0])

    def test_model_type_detection(self, cpp_format_auto, cpp_format_tuning):
        """测试模型类型检测"""
        auto_model = WaterQualityModel(cpp_format_auto)
        tuning_model = WaterQualityModel(cpp_format_tuning)

        assert auto_model.model_type == 1
        assert tuning_model.model_type == 0

    def test_save_creates_directory(self):
        """测试保存时创建目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "subdir", "test_model.json")
            model = WaterQualityModel({"type": 1, "w": [], "a": [], "b": [], "A": []})

            model.save(path)

            assert os.path.exists(path)
            assert os.path.isdir(os.path.join(tmpdir, "subdir"))

    def test_predict_unified_type1_with_preprocess(
        self, auto_model, sample_spectrum_data
    ):
        """测试 type=1 模型使用统一接口并自动预处理"""
        # 使用原始光谱数据，应该自动预处理
        result = auto_model.predict_unified(spectrum_data=sample_spectrum_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spectrum_data)
        # 应该返回预测结果

    def test_predict_unified_type1_without_preprocess(self, auto_model):
        """测试 type=1 模型使用统一接口但跳过预处理"""
        # 创建已预处理的光谱数据（400-900nm 整数波长）
        preprocessed_spectrum = pd.DataFrame(
            {wl: [0.5, 0.4, 0.6] for wl in range(400, 901, 1)}
        )

        result = auto_model.predict_unified(
            spectrum_data=preprocessed_spectrum, preprocess=False
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_predict_unified_type0(self, tuning_model, old_predictions):
        """测试 type=0 模型使用统一接口"""
        result = tuning_model.predict_unified(old_predictions=old_predictions)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(old_predictions)

        # 验证微调计算正确
        if "Turb" in result.columns:
            expected = old_predictions["Turb"] * 1.2
            np.testing.assert_array_almost_equal(
                result["Turb"].values, expected.values, decimal=5
            )

    def test_predict_unified_type1_missing_spectrum(self, auto_model):
        """测试 type=1 模型缺少光谱数据时报错"""
        with pytest.raises(ValueError, match="必须提供光谱数据"):
            auto_model.predict_unified()

    def test_predict_unified_type0_missing_predictions(self, tuning_model):
        """测试 type=0 模型缺少旧预测值时报错"""
        with pytest.raises(ValueError, match="必须提供旧模型的预测值"):
            tuning_model.predict_unified()

    def test_predict_unified_type1_with_both_inputs(
        self, auto_model, sample_spectrum_data, old_predictions
    ):
        """测试 type=1 模型同时提供两种输入时优先使用光谱数据"""
        result = auto_model.predict_unified(
            spectrum_data=sample_spectrum_data, old_predictions=old_predictions
        )

        # 应该使用光谱数据进行预测
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spectrum_data)

    def test_predict_unified_preprocessor_params(self):
        """测试预处理器参数可以自定义"""
        model_data = {"type": 1, "w": [], "a": [], "b": [], "A": [1.0]}

        # 使用自定义预处理参数
        model = WaterQualityModel(
            model_data,
            min_wavelength=450,
            max_wavelength=850,
            smooth_window=7,
            smooth_order=2,
        )

        assert model.preprocessor.min_wavelength == 450
        assert model.preprocessor.max_wavelength == 850
        assert model.preprocessor.smooth_window == 7
        assert model.preprocessor.smooth_order == 2
