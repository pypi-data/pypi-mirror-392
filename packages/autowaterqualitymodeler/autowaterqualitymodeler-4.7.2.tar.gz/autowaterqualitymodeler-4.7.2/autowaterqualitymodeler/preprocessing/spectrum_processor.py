"""
光谱数据预处理模块

提供数据清洗、重采样和平滑功能。
"""

import logging

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.signal import savgol_filter

from ..core.exceptions import DataValidationError, ProcessingError

logger = logging.getLogger(__name__)


class SpectrumProcessor:
    """
    光谱数据预处理器

    提供波长过滤、异常值检测、光谱重采样和平滑等功能。
    """

    def __init__(
        self,
        min_wavelength: int = 400,
        max_wavelength: int = 900,
        smooth_window: int = 11,
        smooth_order: int = 3,
    ):
        """
        初始化光谱处理器

        Args:
            min_wavelength: 最小波长 (nm)
            max_wavelength: 最大波长 (nm)
            smooth_window: Savitzky-Golay 平滑窗口大小 (必须是奇数)
            smooth_order: Savitzky-Golay 平滑多项式阶数

        Raises:
            ValueError: 参数值无效时
        """
        if min_wavelength >= max_wavelength:
            raise ValueError(
                f"min_wavelength ({min_wavelength}) must be less than "
                f"max_wavelength ({max_wavelength})"
            )
        if smooth_window < 3 or smooth_window % 2 == 0:
            raise ValueError(f"smooth_window ({smooth_window}) must be odd and >= 3")
        if smooth_order >= smooth_window:
            raise ValueError(
                f"smooth_order ({smooth_order}) must be less than "
                f"smooth_window ({smooth_window})"
            )

        self.min_wavelength = min_wavelength
        self.max_wavelength = max_wavelength
        self.smooth_window = smooth_window
        self.smooth_order = smooth_order

        logger.debug(
            f"初始化光谱处理器: 波长范围 {min_wavelength}-{max_wavelength}nm, "
            f"平滑窗口 {smooth_window}, 平滑阶数 {smooth_order}"
        )

    def preprocess(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """
        预处理光谱数据

        执行以下步骤:
        1. 过滤波长范围
        2. 过滤异常值
        3. 重采样光谱
        4. 平滑光谱

        Args:
            spectrum_data: 光谱数据，列名为波长，每行是一条光谱样本

        Returns:
            预处理后的光谱数据

        Raises:
            DataValidationError: 输入数据格式错误
            ProcessingError: 预处理过程中的错误
        """
        if spectrum_data is None or spectrum_data.empty:
            raise DataValidationError("输入的光谱数据为空")

        if not isinstance(spectrum_data, pd.DataFrame):
            raise DataValidationError(
                f"光谱数据必须是 DataFrame 类型，但接收到 {type(spectrum_data).__name__}"
            )

        try:
            logger.info(f"开始预处理光谱数据... 原始形状: {spectrum_data.shape}")

            # 1. 过滤波长范围
            filtered_data = self._filter_wavelength(spectrum_data)
            if filtered_data.empty:
                raise ProcessingError("波长过滤后没有剩余数据")

            # 2. 过滤异常值
            filtered_data = self._filter_anomalies(filtered_data)

            # 3. 重采样光谱
            resampled_data = self._resample_spectrum(filtered_data)

            # 4. 平滑光谱
            smoothed_data = self._smooth_spectrum(resampled_data)

            logger.info(f"光谱预处理完成，处理后形状: {smoothed_data.shape}")
            return smoothed_data

        except (DataValidationError, ProcessingError):
            raise
        except Exception as e:
            raise ProcessingError(f"光谱预处理失败: {str(e)}")

    def _filter_wavelength(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """过滤指定波长范围的数据"""
        try:
            # 将列名转换为float类型
            spectrum_data.columns = spectrum_data.columns.astype(float)
        except ValueError:
            raise DataValidationError("光谱数据列名无法转换为波长值(float类型)")

        # 过滤波长范围
        cols = [
            col
            for col in spectrum_data.columns
            if self.min_wavelength <= float(col) <= self.max_wavelength
        ]

        if not cols:
            raise ProcessingError(
                f"在范围 {self.min_wavelength}-{self.max_wavelength} nm 内没有有效波长"
            )

        filtered_data = spectrum_data[cols]
        logger.debug(
            f"波长过滤完成: {len(spectrum_data.columns)} → {len(filtered_data.columns)} 个波长"
        )

        return filtered_data

    def _filter_anomalies(
        self, spectrum_data: pd.DataFrame, threshold: float = 0.1
    ) -> pd.DataFrame:
        """过滤光谱中的异常值"""
        processed_data = spectrum_data.copy()

        # 检测异常值（反射率应在 0-1 之间）
        anomalies = (processed_data < 0) | (processed_data > 1)

        # 计算每行的异常值比例
        anomaly_ratio = anomalies.sum(axis=1) / anomalies.shape[1]
        bad_rows_count = (anomaly_ratio > threshold).sum()

        if bad_rows_count > 0:
            logger.warning(
                f"检测到 {bad_rows_count} 行数据中超过 {threshold * 100}% 的值为异常值"
            )

        # 将异常值替换为NaN
        processed_data[anomalies] = np.nan
        processed_data.replace([np.inf, -np.inf], np.nan, inplace=True)

        # 使用前向和后向填充
        processed_data = processed_data.ffill(axis=1).bfill(axis=1)

        logger.debug(f"异常值过滤完成，处理后形状: {processed_data.shape}")
        return processed_data

    def _resample_spectrum(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """使用三次样条插值对光谱进行重采样"""
        wavelengths = spectrum_data.columns.values.astype(float)
        data = spectrum_data.values

        # 定义目标波长（整数）
        target_wavelengths = np.arange(
            int(np.ceil(self.min_wavelength)),
            int(np.floor(self.max_wavelength)) + 1,
            1,
        )

        # 初始化重采样数据
        resampled_data = np.zeros((data.shape[0], len(target_wavelengths)))

        # 对每条光谱进行重采样
        for i in range(data.shape[0]):
            try:
                cs = CubicSpline(wavelengths, data[i, :], bc_type="not-a-knot")
                resampled_data[i, :] = cs(target_wavelengths)
            except Exception as e:
                logger.warning(f"样本 {i} 三次样条插值失败，使用线性插值: {e}")
                resampled_data[i, :] = np.interp(
                    target_wavelengths, wavelengths, data[i, :]
                )

        resampled_df = pd.DataFrame(
            resampled_data, index=spectrum_data.index, columns=target_wavelengths
        ).copy()

        logger.debug(
            f"光谱重采样完成，波长数: {len(wavelengths)} → {len(target_wavelengths)}"
        )
        return resampled_df

    def _smooth_spectrum(self, spectrum_data: pd.DataFrame) -> pd.DataFrame:
        """使用Savitzky-Golay滤波器平滑光谱"""
        data = spectrum_data.values

        window_length = self.smooth_window
        if window_length >= data.shape[1]:
            window_length = min(data.shape[1] - 1, 11)
            if window_length % 2 == 0:
                window_length -= 1

        polyorder = min(self.smooth_order, window_length - 1)

        try:
            smoothed_data = savgol_filter(data, window_length, polyorder, axis=1)

            # 保留窗口两端的原始数据
            half_window = window_length // 2
            smoothed_data[:, :half_window] = data[:, :half_window]
            smoothed_data[:, -half_window:] = data[:, -half_window:]

            return pd.DataFrame(
                smoothed_data, index=spectrum_data.index, columns=spectrum_data.columns
            )
        except Exception as e:
            logger.warning(f"平滑处理失败，返回原始数据: {e}")
            return spectrum_data
