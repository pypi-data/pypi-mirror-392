"""
线性拟合器单元测试
"""

import numpy as np
import pandas as pd

from autowaterqualitymodeler.models.linear_fitter import LinearModelFitter


class TestLinearModelFitter:
    """测试线性拟合器（过原点）"""

    def test_fit_basic(self, linear_fit_data):
        """测试基本拟合功能"""
        x, y = linear_fit_data
        fitter = LinearModelFitter()

        a = fitter.fit(x, y)

        assert a is not None
        # 斜率应该接近 1.5
        assert 1.2 < a < 1.8

    def test_fit_perfect_linear(self):
        """测试完美线性关系"""
        x = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        y = pd.Series([2.0, 4.0, 6.0, 8.0, 10.0])
        fitter = LinearModelFitter()

        a = fitter.fit(x, y)

        assert a is not None
        # 应该非常接近 2.0
        assert abs(a - 2.0) < 0.01

    def test_fit_insufficient_data(self):
        """测试样本量不足"""
        x = pd.Series([1.0])
        y = pd.Series([2.0])
        fitter = LinearModelFitter()

        a = fitter.fit(x, y)

        # 样本量太少应该返回 None
        assert a is None

    def test_fit_all_zeros(self):
        """测试全零值情况"""
        x = pd.Series([0.0, 0.0, 0.0])
        y = pd.Series([1.0, 2.0, 3.0])
        fitter = LinearModelFitter()

        a = fitter.fit(x, y)

        # 分母为零，sklearn会返回0系数
        # 这是合理的行为，因为 y = 0 * x = 0
        assert a == 0.0 or a is None

    def test_predict(self, linear_fit_data):
        """测试预测功能"""
        x, y = linear_fit_data
        fitter = LinearModelFitter()

        a = fitter.fit(x, y)
        assert a is not None

        predictions = fitter.predict(x, a)

        assert len(predictions) == len(x)
        assert isinstance(predictions, pd.Series)

        # 预测值应该与真实值高度相关
        corr = np.corrcoef(predictions, y)[0, 1]
        assert corr > 0.95

    def test_predict_with_series_index(self):
        """测试保留索引"""
        x = pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"])
        fitter = LinearModelFitter()

        predictions = fitter.predict(x, a=2.0)

        assert predictions.index.tolist() == ["a", "b", "c"]
        assert predictions.tolist() == [2.0, 4.0, 6.0]
