from math import log
import pandas as pd
import logging
import numpy as np
from autowaterqualitymodeler import AutoWaterQualityModeler

INDICATOR_NAMES = [
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
]

STZ_NAMES = [
    "STZ1",
    "STZ2",
    "STZ3",
    "STZ4",
    "STZ5",
    "STZ6",
    "STZ7",
    "STZ8",
    "STZ9",
    "STZ10",
    "STZ11",
    "STZ12",
    "STZ13",
    "STZ14",
    "STZ15",
    "STZ16",
    "STZ17",
    "STZ18",
    "STZ19",
    "STZ20",
    "STZ21",
    "STZ22",
    "STZ23",
    "STZ24",
    "STZ25",
    "STZ26",
]

logger = logging.getLogger(__file__)

class PredictByBin:
    def __init__(self, ref_data, uav_data, bin_data):
        self.ref_data = ref_data
        self.uav_data = uav_data
        self.bin_data = bin_data

        height = len(INDICATOR_NAMES)
        width = len(STZ_NAMES)

        # reshape 保证维度清晰
        self.A_data = np.array(bin_data.get('A'))
        self.w_data = np.array(bin_data.get('w')).reshape(width, height).T
        self.a_data = np.array(bin_data.get('a')).reshape(width, height).T

        # aw shape = (11 × 26)
        self.aw = self.a_data * self.w_data

        # b shape = (11 × 26)
        self.b_data = np.array(bin_data.get('b')).reshape(height, width)

        # inner/outer 列判断
        valid_indicators = [
            INDICATOR_NAMES[i] 
            for i, v in enumerate(self.A_data) 
            if v != -1.0
        ]

        self.uav_inner_indicators = list(set(self.uav_data.columns) & set(valid_indicators))
        logger.info(f"指标 {self.uav_inner_indicators}将被bin重新生成。。。")
        self.uav_outer_indicators = [
            c for c in self.uav_data.columns 
            if c not in self.uav_inner_indicators and c not in ['Latitue', 'Longitue']
        ]

    # ----------------- TYPE 0 -------------------
    def type0(self):
        # 自动补齐列，缺的为 NaN
        temp_uav = self.uav_data.reindex(columns=INDICATOR_NAMES)
        # 逐列乘 A_data（广播自动匹配 1D）
        new_uav = temp_uav * self.A_data

        # 只更新 inner 部分
        for col in self.uav_inner_indicators:
            self.uav_data[col] = new_uav[col]

        return self.uav_data.copy()

    # ----------------- 单个指标的计算函数 -------------------
    def _compute_indicator(self, modeler, preprocess_ref, indicator_name):
        stand_name = modeler.config_manager.format_output_column_name(indicator_name)
        i = INDICATOR_NAMES.index(stand_name)

        # 计算特征矩阵 X (677 × 26)
        features = modeler.feature_manager.calculate_features(preprocess_ref, 'aerospot', indicator_name)
        
        # 自动补齐缺失列，并确保列顺序完全一致
        X = features.reindex(columns=STZ_NAMES).values # 直接抽列，无需 concat

        # 幂运算
        xb = X ** self.b_data[i, :]

        # 点积： (677 × 26) dot (26)
        result = xb @ self.aw[i, :]

        return stand_name, result

    # ----------------- TYPE 1 -------------------
    def type1(self):
        modeler = AutoWaterQualityModeler()
        preprocess_ref = modeler.processor.preprocess(self.ref_data)

        normalized_inner = modeler.config_manager.normalize_dataframe_columns(
            self.uav_data[self.uav_inner_indicators]
        ).columns.tolist()

        for indicator_name in normalized_inner:
            col, values = self._compute_indicator(modeler, preprocess_ref, indicator_name)
            self.uav_data[col] = values

        return self.uav_data.copy()
 

