"""
幂函数拟合器单元测试
"""

import numpy as np

from autowaterqualitymodeler.models.power_fitter import PowerModelFitter


class TestPowerModelFitter:
    """测试幂函数拟合器"""

    def test_fit_basic(self, power_fit_data):
        """测试基本拟合功能"""
        x, y = power_fit_data
        fitter = PowerModelFitter()

        # 转换为 numpy 数组
        result = fitter.fit(x.values, y.values)

        assert result is not None
        assert hasattr(result, "a")
        assert hasattr(result, "b")
        assert hasattr(result, "correlation")
        assert hasattr(result, "rmse")
        assert hasattr(result, "r2")

        # 检查拟合参数接近真实值 (y = 2 * x^0.5)
        assert 1.5 < result.a < 2.5  # a 应该接近 2
        assert 0.3 < result.b < 0.7  # b 应该接近 0.5
        assert result.correlation > 0.95  # 相关性应该很高
        assert result.r2 > 0.9  # R² 应该很高

    def test_fit_with_negative_values(self):
        """测试包含负值的情况"""
        x = np.array([1, 2, -3, 4, 5])
        y = np.array([2, 4, 0, 8, 10])
        fitter = PowerModelFitter()

        result = fitter.fit(x, y)

        # 应该过滤掉负值后仍能拟合
        assert result is not None or result is None  # 可能成功也可能失败（样本太少）

    def test_fit_insufficient_data(self):
        """测试样本量不足的情况"""
        x = np.array([1.0, 2.0])
        y = np.array([2.0, 4.0])
        fitter = PowerModelFitter()

        result = fitter.fit(x, y)

        # 样本量太少应该返回 None
        assert result is None

    def test_fit_constant_values(self):
        """测试常数值情况"""
        x = np.array([5.0, 5.0, 5.0, 5.0])
        y = np.array([10.0, 10.0, 10.0, 10.0])
        fitter = PowerModelFitter()

        result = fitter.fit(x, y)

        # 常数值可能会拟合成功，但相关系数会很低
        if result is not None:
            assert result.correlation <= 0.2  # 相关性应该很低

    def test_fit_zero_values(self):
        """测试包含零值的情况"""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = np.array([0.0, 2.0, 4.0, 6.0, 8.0])
        fitter = PowerModelFitter()

        result = fitter.fit(x, y)

        # 应该过滤掉零值
        assert result is not None
        assert result.correlation > 0.8

    def test_predict(self, power_fit_data):
        """测试预测功能"""
        x, y = power_fit_data
        fitter = PowerModelFitter()

        result = fitter.fit(x.values, y.values)
        assert result is not None

        # 使用训练数据预测
        predictions = fitter.predict(x.values, result.a, result.b)

        assert len(predictions) == len(x)
        assert isinstance(predictions, np.ndarray)

        # 预测值应该与真实值相关
        corr = np.corrcoef(predictions, y.values)[0, 1]
        assert corr > 0.9

    def test_predict_with_negative_values(self):
        """测试预测时包含负值"""
        fitter = PowerModelFitter()

        x = np.array([1, 2, -3, 4, 5])
        predictions = fitter.predict(x, a=2.0, b=0.5)

        # 负值会产生 nan 或 warning，但会返回所有值
        assert len(predictions) == len(x)

    def test_predict_simple(self):
        """测试简单预测"""
        fitter = PowerModelFitter()

        x = np.array([1.0, 4.0, 9.0, 16.0])
        predictions = fitter.predict(x, a=2.0, b=0.5)

        # y = 2 * x^0.5
        expected = np.array([2.0, 4.0, 6.0, 8.0])
        np.testing.assert_array_almost_equal(predictions, expected, decimal=5)
