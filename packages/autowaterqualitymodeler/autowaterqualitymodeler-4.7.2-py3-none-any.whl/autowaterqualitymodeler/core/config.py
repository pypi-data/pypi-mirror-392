"""
配置管理模块

提供特征配置和系统配置的加载和访问功能。
支持 Python 配置（可被 Nuitka 编译）和 JSON 配置（向后兼容）。
"""

import importlib.util
import json
import logging
import os
from typing import Any

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Config:
    """配置管理器"""

    DATA_TYPES = ["warning_device", "shore_data", "smart_water", "aerospot"]

    def __init__(
        self,
        config_path: str | None = None,
        system_config_path: str | None = None,
    ):
        """
        初始化配置管理器

        Args:
            config_path: 特征配置文件路径（支持 .py 或 .json）
            system_config_path: 系统配置文件路径（支持 .py 或 .json）
        """
        # 加载特征配置
        if config_path is None:
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config",
            )
            # 优先使用 Python 配置，回退到 JSON
            config_path = self._find_config_file(config_dir, "features_config")

        self.config_path = config_path
        self.feature_config = self._load_config(
            config_path, "features_config", required=True
        )

        # 加载系统配置
        if system_config_path is None:
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config",
            )
            system_config_path = self._find_config_file(config_dir, "system_config")

        self.system_config = self._load_config(
            system_config_path,
            "system_config",
            required=False,
            default=self._default_system_config(),
        )

        # 加载列名映射
        self._input_mapping = self._load_input_mapping()
        self._output_mapping = self._load_output_mapping()

        logger.info(f"配置加载完成: {config_path}")

    def _find_config_file(self, config_dir: str, config_name: str) -> str:
        """
        查找配置文件，优先使用 .py，回退到 .json

        Args:
            config_dir: 配置目录
            config_name: 配置名称（不含扩展名）

        Returns:
            配置文件完整路径
        """
        py_path = os.path.join(config_dir, f"{config_name}.py")
        json_path = os.path.join(config_dir, f"{config_name}.json")

        if os.path.exists(py_path):
            logger.debug(f"使用 Python 配置: {py_path}")
            return py_path
        elif os.path.exists(json_path):
            logger.debug(f"使用 JSON 配置: {json_path}")
            return json_path
        else:
            # 默认返回 Python 路径（后续会报错）
            return py_path

    def _load_config(
        self,
        path: str,
        module_name: str,
        required: bool = True,
        default: dict | None = None,
    ) -> dict:
        """
        加载配置文件（支持 .py 和 .json）

        Args:
            path: 配置文件路径
            module_name: 模块名称
            required: 是否必须存在
            default: 默认配置

        Returns:
            配置字典
        """
        # 1. 尝试加载 Python 配置模块
        if path.endswith(".py"):
            try:
                config_dict = self._load_python_config(path, module_name)
                logger.info(f"成功加载 Python 配置: {path}")
                return config_dict
            except Exception as e:
                logger.warning(f"加载 Python 配置失败: {path}, {e}")
                # 尝试回退到 JSON
                json_path = path.replace(".py", ".json")
                if os.path.exists(json_path):
                    logger.info(f"回退到 JSON 配置: {json_path}")
                    return self._load_json(json_path, required, default)
                elif required:
                    raise ConfigurationError(f"配置文件加载失败: {path}")
                else:
                    return default or {}

        # 2. 加载 JSON 配置
        return self._load_json(path, required, default)

    def _load_python_config(self, path: str, module_name: str) -> dict:
        """
        动态导入 Python 配置模块

        Args:
            path: Python 文件路径
            module_name: 模块名称

        Returns:
            配置字典
        """
        # 方式1：尝试使用标准导入（对 Nuitka 编译更友好）
        try:
            # 获取配置包路径
            config_package = "autowaterqualitymodeler.config"
            full_module_name = f"{config_package}.{module_name}"

            # 尝试导入
            import importlib

            module = importlib.import_module(full_module_name)

            # 获取配置
            if hasattr(module, "get_config"):
                return module.get_config()
            elif hasattr(module, "FEATURES_CONFIG"):
                return module.FEATURES_CONFIG
            elif hasattr(module, "SYSTEM_CONFIG"):
                return module.SYSTEM_CONFIG
            else:
                raise ConfigurationError(f"配置模块 {full_module_name} 缺少配置变量")

        except ImportError:
            # 方式2：动态加载文件（开发环境）
            logger.debug(f"标准导入失败，尝试动态加载: {path}")
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ConfigurationError(f"无法加载配置模块: {path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 获取配置
            if hasattr(module, "get_config"):
                return module.get_config()
            elif hasattr(module, "FEATURES_CONFIG"):
                return module.FEATURES_CONFIG
            elif hasattr(module, "SYSTEM_CONFIG"):
                return module.SYSTEM_CONFIG
            else:
                raise ConfigurationError(f"配置模块 {path} 缺少配置变量")

    def _load_json(
        self, path: str, required: bool = True, default: dict | None = None
    ) -> dict:
        """加载 JSON 配置文件"""
        if not os.path.exists(path):
            if required:
                raise ConfigurationError(f"配置文件不存在: {path}")
            else:
                logger.info(f"配置文件不存在: {path}，使用默认配置")
                return default or {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            if required:
                raise ConfigurationError(f"配置文件JSON格式错误: {path}, {e}")
            else:
                logger.warning(f"配置文件JSON格式错误: {path}，使用默认配置")
                return default or {}

    def _default_system_config(self) -> dict:
        """默认系统配置"""
        return {
            "water_quality_params": [
                "Turb",
                "SS",
                "SD",
                "DO",
                "CODMn",
                "COD",
                "Chla",
                "TN",
                "TP",
                "Chroma",
                "NH3-N",
            ],
            "feature_stations": [f"STZ{i}" for i in range(1, 27)],
            "column_name_mapping": {"input_mappings": {}, "output_mappings": {}},
        }

    def get_water_quality_params(self) -> list[str]:
        """获取水质参数列表"""
        return self.system_config.get("water_quality_params", [])

    def get_feature_stations(self) -> list[str]:
        """获取特征站点列表"""
        return self.system_config.get("feature_stations", [])

    def get_feature_definitions(self, data_type: str, metric_name: str) -> list[dict]:
        """
        获取指定数据类型和指标的特征定义

        Args:
            data_type: 数据类型
            metric_name: 指标名称

        Returns:
            特征定义列表
        """
        if data_type not in self.DATA_TYPES:
            logger.warning(f"不支持的数据类型: {data_type}")
            return []

        # 获取特征引用
        if data_type in self.feature_config:
            if metric_name in self.feature_config[data_type]:
                features = self.feature_config[data_type][metric_name].get(
                    "features", []
                )
            elif "default" in self.feature_config[data_type]:
                features = self.feature_config[data_type]["default"].get("features", [])
            else:
                logger.warning(f"未找到 {data_type} 下 {metric_name} 的特征定义")
                return []
        else:
            return []

        # 解析特征定义
        full_definitions = []
        for ref in features:
            feature_id = ref.get("feature_id")
            if not feature_id:
                continue

            if (
                "features" in self.feature_config
                and feature_id in self.feature_config["features"]
            ):
                base_def = self.feature_config["features"][feature_id].copy()
                if "bands" in ref:
                    base_def["bands"] = ref["bands"]
                full_definitions.append(base_def)
            else:
                logger.warning(f"未找到特征ID: {feature_id}")

        return full_definitions

    def get_model_params(self, data_type: str | None = None) -> dict:
        """获取模型参数"""
        params = {"min_samples": 6, "max_features": 5}

        # 全局参数
        if "model_params" in self.feature_config:
            params.update(self.feature_config["model_params"])

        # 数据类型参数
        if data_type and data_type in self.feature_config:
            if "model_params" in self.feature_config[data_type]:
                params.update(self.feature_config[data_type]["model_params"])

        return params

    def _load_input_mapping(self) -> dict[str, str]:
        """加载输入列名映射"""
        mapping_config = self.system_config.get("column_name_mapping", {})
        mappings = mapping_config.get("input_mappings", {})

        # 添加标准名称到自身的映射
        for param in self.get_water_quality_params():
            if param not in mappings:
                mappings[param] = param

        return mappings

    def _load_output_mapping(self) -> dict[str, str]:
        """加载输出列名映射"""
        mapping_config = self.system_config.get("column_name_mapping", {})
        mappings = mapping_config.get("output_mappings", {})

        if not mappings:
            for param in self.get_water_quality_params():
                mappings[param] = param.capitalize()

        return mappings

    def normalize_column_name(self, column_name: str) -> str:
        """将用户列名标准化为系统内部名称"""
        return self._input_mapping.get(column_name, column_name)

    def normalize_dataframe_columns(self, df: Any) -> Any:
        """标准化 DataFrame 的列名"""
        import pandas as pd

        if not isinstance(df, pd.DataFrame):
            return df

        normalized_df = df.copy()
        column_mapping = {}

        for col in normalized_df.columns:
            normalized_name = self.normalize_column_name(col)
            if normalized_name != col:
                column_mapping[col] = normalized_name

        if column_mapping:
            normalized_df = normalized_df.rename(columns=column_mapping)
            logger.info(f"列名标准化: {column_mapping}")

        return normalized_df
