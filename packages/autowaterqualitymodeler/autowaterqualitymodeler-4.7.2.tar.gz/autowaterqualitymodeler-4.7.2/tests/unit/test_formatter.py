"""
结果格式化器单元测试
"""

import pandas as pd
import pytest

from autowaterqualitymodeler.core.config import Config
from autowaterqualitymodeler.pipeline.formatter import ResultFormatter


class TestResultFormatter:
    """测试结果格式化器"""

    @pytest.fixture
    def formatter(self):
        """创建格式化器实例"""
        config = Config()
        return ResultFormatter(config)

    @pytest.fixture
    def sample_models(self):
        """创建样本模型数据"""
        return {
            "Turb": {
                "STZ1": {"w": 0.6, "a": 2.0, "b": 0.5},
                "STZ2": {"w": 0.4, "a": 3.0, "b": 0.6},
            },
            "Chla": {
                "STZ3": {"w": 1.0, "a": 1.5, "b": 0.7},
            },
        }

    @pytest.fixture
    def sample_metric_data(self):
        """创建样本指标数据"""
        data = {
            "Turb": [10.0, 20.0, 30.0, 40.0],
            "Chla": [15.0, 25.0, 35.0, 45.0],
            "SS": [20.0, 30.0, 40.0, 50.0],
        }
        return pd.DataFrame(data)

    def test_format_auto_model_structure(
        self, formatter, sample_models, sample_metric_data
    ):
        """测试自动建模格式化结果结构"""
        result = formatter.format_auto_model(sample_models, sample_metric_data)

        # 检查必需字段
        assert "type" in result
        assert "w" in result
        assert "a" in result
        assert "b" in result
        assert "A" in result
        assert "Range" in result

        # 检查类型
        assert result["type"] == 1
        assert isinstance(result["w"], list)
        assert isinstance(result["a"], list)
        assert isinstance(result["b"], list)
        assert isinstance(result["A"], list)
        assert isinstance(result["Range"], list)

    def test_format_auto_model_dimensions(
        self, formatter, sample_models, sample_metric_data
    ):
        """测试自动建模格式化结果维度"""
        result = formatter.format_auto_model(sample_models, sample_metric_data)

        index = formatter.config.get_water_quality_params()
        columns = formatter.config.get_feature_stations()

        n_metrics = len(index)
        n_features = len(columns)

        # 检查维度
        # w 和 a 是转置后展平: columns × index
        assert len(result["w"]) == n_metrics * n_features
        assert len(result["a"]) == n_metrics * n_features
        # b 是直接展平: index × columns
        assert len(result["b"]) == n_metrics * n_features
        assert len(result["A"]) == n_metrics
        assert len(result["Range"]) == n_metrics * 2

    def test_format_auto_model_a_vector(
        self, formatter, sample_models, sample_metric_data
    ):
        """测试 A 向量标记"""
        result = formatter.format_auto_model(sample_models, sample_metric_data)

        A_vector = result["A"]
        index = formatter.config.get_water_quality_params()

        # Turb 和 Chla 应该标记为 1.0
        turb_idx = index.index("Turb")
        chla_idx = index.index("Chla")

        assert A_vector[turb_idx] == 1.0
        assert A_vector[chla_idx] == 1.0

        # 其他未建模的指标应该是 -1.0
        for i, metric in enumerate(index):
            if metric not in ["Turb", "Chla"]:
                assert A_vector[i] == -1.0

    def test_format_auto_model_range(
        self, formatter, sample_models, sample_metric_data
    ):
        """测试 Range 计算"""
        result = formatter.format_auto_model(sample_models, sample_metric_data)

        Range_vector = result["Range"]
        index = formatter.config.get_water_quality_params()

        # Turb 的范围
        turb_idx = index.index("Turb")
        turb_min = Range_vector[turb_idx * 2]
        turb_max = Range_vector[turb_idx * 2 + 1]

        # 应该在合理范围内
        assert turb_min >= 0
        assert turb_max > turb_min
        assert turb_min <= 10.0  # 最小值 10.0 - 3*std
        assert turb_max >= 40.0  # 最大值 40.0 + 3*std

    def test_format_tuning_model_structure(self, formatter, sample_metric_data):
        """测试微调建模格式化结果结构"""
        coefficients = {"Turb": 1.2, "Chla": 0.95}

        result = formatter.format_tuning_model(coefficients, sample_metric_data)

        # 检查必需字段
        assert "type" in result
        assert "A" in result
        assert "Range" in result

        # 检查类型
        assert result["type"] == 0
        assert isinstance(result["A"], list)
        assert isinstance(result["Range"], list)

    def test_format_tuning_model_a_vector(self, formatter, sample_metric_data):
        """测试微调模型 A 向量"""
        coefficients = {"Turb": 1.2, "Chla": 0.95}

        result = formatter.format_tuning_model(coefficients, sample_metric_data)

        A_vector = result["A"]
        index = formatter.config.get_water_quality_params()

        # 检查微调系数
        turb_idx = index.index("Turb")
        chla_idx = index.index("Chla")

        assert A_vector[turb_idx] == 1.2
        assert A_vector[chla_idx] == 0.95

        # 其他指标应该是 -1.0
        for i, metric in enumerate(index):
            if metric not in ["Turb", "Chla"]:
                assert A_vector[i] == -1.0

    def test_format_tuning_model_range(self, formatter, sample_metric_data):
        """测试微调模型 Range"""
        coefficients = {"Turb": 1.2}

        result = formatter.format_tuning_model(coefficients, sample_metric_data)

        Range_vector = result["Range"]

        # 应该有 2 * n_metrics 个值
        n_metrics = len(formatter.config.get_water_quality_params())
        assert len(Range_vector) == n_metrics * 2
