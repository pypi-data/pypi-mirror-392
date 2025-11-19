import pandas as pd
from autowaterqualitymodeler.core.modeler import AutoWaterQualityModeler
from autowaterqualitymodeler.core.model import WaterQualityModel


def main():
    import os

    # 获取当前脚本路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 构造ref_data.csv和uav.csv的绝对路径
    spectrum_path = os.path.join(current_dir, "ref_data.csv")
    indicator_path = os.path.join(current_dir, "uav.csv")

    print("spectrum_data path:", spectrum_path)
    print("indicator_data path:", indicator_path)

    # 检查文件是否存在
    if not os.path.isfile(spectrum_path):
        raise FileNotFoundError(f"光谱文件未找到: {spectrum_path}")
    if not os.path.isfile(indicator_path):
        raise FileNotFoundError(f"指标文件未找到: {indicator_path}")

    # 读取数据
    spectrum_data = pd.read_csv(spectrum_path, header=0, index_col=0)
    indicator_data = pd.read_csv(indicator_path, header=0, index_col=0)

    modeler = AutoWaterQualityModeler()
    model_result = modeler.fit(spectrum_data=spectrum_data, metric_data=indicator_data, old_predictions=indicator_data)
    model_json = model_result.model_data

    custom_model = WaterQualityModel(model_json)
    print("yes")


if __name__ == "__main__":
    main()
