"""
pytest 配置和共享夹具

为 AutoWaterQualityModeler v2 测试提供共享夹具。
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_spectrum_data() -> pd.DataFrame:
    """创建样本光谱数据（10个样本，波长400-900nm）"""
    np.random.seed(42)
    wavelengths = list(range(400, 901, 5))  # 每5nm一个采样点
    n_samples = 10

    # 模拟真实光谱数据（反射率0-1之间）
    data = {}
    for wl in wavelengths:
        # 生成模拟光谱，包含一些噪声
        base_value = 0.3 + 0.4 * np.sin((wl - 400) / 200)
        noise = np.random.normal(0, 0.05, n_samples)
        data[wl] = np.clip(base_value + noise, 0.01, 0.99)

    return pd.DataFrame(data)


@pytest.fixture
def sample_metric_data() -> pd.DataFrame:
    """创建样本水质指标数据（10个样本）"""
    np.random.seed(42)
    n_samples = 10

    # 模拟真实水质指标（使用标准名称）
    data = {
        "Turb": np.random.uniform(5, 50, n_samples),
        "Chla": np.random.uniform(10, 100, n_samples),
        "SS": np.random.uniform(10, 200, n_samples),
        "TN": np.random.uniform(0.5, 5, n_samples),
        "TP": np.random.uniform(0.01, 0.5, n_samples),
    }

    return pd.DataFrame(data)


@pytest.fixture
def small_metric_data() -> pd.DataFrame:
    """创建小样本水质指标数据（3个样本，用于微调测试）"""
    np.random.seed(42)

    data = {
        "Turb": np.array([10.0, 20.0, 30.0]),
        "Chla": np.array([25.0, 50.0, 75.0]),
    }

    return pd.DataFrame(data)


@pytest.fixture
def old_predictions() -> pd.DataFrame:
    """创建旧模型预测值（用于微调测试）"""
    data = {
        "Turb": np.array([12.0, 18.0, 28.0]),
        "Chla": np.array([22.0, 48.0, 72.0]),
    }

    return pd.DataFrame(data)


@pytest.fixture
def simple_feature_data() -> pd.DataFrame:
    """创建简单特征数据（用于特征选择和模型组合测试）"""
    np.random.seed(42)
    n_samples = 20

    # 创建与目标变量相关的特征
    base = np.linspace(1, 10, n_samples)

    data = {
        "STZ1": base * 2 + np.random.normal(0, 0.5, n_samples),
        "STZ2": base * 1.5 + np.random.normal(0, 0.3, n_samples),
        "STZ3": np.random.uniform(1, 20, n_samples),  # 不相关的特征
        "STZ4": base**2 / 10 + np.random.normal(0, 0.2, n_samples),
    }

    return pd.DataFrame(data)


@pytest.fixture
def simple_target() -> pd.Series:
    """创建简单目标变量（与特征数据对应）"""
    np.random.seed(42)
    n_samples = 20
    base = np.linspace(1, 10, n_samples)
    # 目标变量与 STZ1 和 STZ4 高度相关
    target = base * 3 + np.random.normal(0, 0.3, n_samples)
    return pd.Series(target)


@pytest.fixture
def power_fit_data() -> tuple[pd.Series, pd.Series]:
    """创建幂函数拟合数据: y = 2 * x^0.5"""
    np.random.seed(42)
    x = np.linspace(1, 100, 50)
    y = 2 * np.power(x, 0.5) + np.random.normal(0, 0.1, len(x))
    return pd.Series(x), pd.Series(y)


@pytest.fixture
def linear_fit_data() -> tuple[pd.Series, pd.Series]:
    """创建线性拟合数据: y = 1.5 * x"""
    np.random.seed(42)
    x = np.linspace(1, 50, 30)
    y = 1.5 * x + np.random.normal(0, 0.5, len(x))
    return pd.Series(x), pd.Series(y)


@pytest.fixture
def cpp_format_auto() -> dict:
    """创建 C++ 格式的自动建模结果

    注意: 实际配置有 11 个水质参数和 26 个特征站点
    w 和 a 矩阵大小应该是 26 * 11 = 286 (columns × index，转置后展平)
    b 矩阵大小应该是 11 * 26 = 286 (index × columns，不转置)
    """
    n_metrics = 11
    n_features = 26

    # 创建权重矩阵 (扁平化: features × metrics)
    w_flat = [0.0] * (n_features * n_metrics)
    a_flat = [0.0] * (n_features * n_metrics)

    # 为第一个指标设置两个特征的权重 (STZ1 和 STZ2)
    w_flat[0] = 0.6  # STZ1 for metric 0
    w_flat[11] = 0.4  # STZ2 for metric 0

    a_flat[0] = 2.0
    a_flat[11] = 3.0

    # b 矩阵 (扁平化: metrics × features)
    b_flat = [0.0] * (n_metrics * n_features)
    # 为第一个指标的 STZ1 和 STZ2 设置 b 值
    b_flat[0] = 0.5  # metric 0, feature 0 (STZ1)
    b_flat[1] = 0.6  # metric 0, feature 1 (STZ2)

    return {
        "type": 1,
        "w": w_flat,
        "a": a_flat,
        "b": b_flat,
        "A": [1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
        "Range": [0.0, 100.0, 0.0, 50.0] + [0.0] * 18,
    }


@pytest.fixture
def cpp_format_tuning() -> dict:
    """创建 C++ 格式的微调建模结果"""
    return {
        "type": 0,
        "A": [1.2, 0.95, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
        "Range": [5.0, 60.0, 10.0, 120.0] + [0.0] * 18,
    }
