import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class HistoryDataBundle:
    """用于封装参考数据、指标数据和建模数据的对象，方便后续统一保存和恢复。

    这个类提供了方便的接口来保存和加载历史数据，支持单文件保存和多文件合并加载。

    Attributes:
        ref_df: 参考数据（参考反演特征指标）
        merged_df: 合并数据（合并后的完整数据）
        measure_df: 测量数据（地面测量数据）

    Example:
        >>> ref = pd.DataFrame({'col': [1, 2, 3]})
        >>> merged = pd.DataFrame({'col': [1, 2, 3]})
        >>> measure = pd.DataFrame({'col': [1, 2, 3]})
        >>> bundle = HistoryDataBundle(ref, merged, measure)
        >>> bundle.save_to_file('history.h5')
        >>> loaded = HistoryDataBundle.load_from_file(['history.h5'])
        >>> loaded.ref_df.equals(ref)
        True
    """

    def __init__(
        self,
        ref_df: pd.DataFrame,
        merged_df: pd.DataFrame,
        measure_df: pd.DataFrame,
    ) -> None:
        """初始化历史数据束对象。

        Args:
            ref_df: 参考反演特征指标数据框
            merged_df: 合并后的完整数据框
            measure_df: 地面测量数据框

        Raises:
            TypeError: 如果任何参数不是 DataFrame
            ValueError: 如果任何 DataFrame 为空
        """
        if not isinstance(ref_df, pd.DataFrame):
            raise TypeError("ref_df 必须是 pandas DataFrame")
        if not isinstance(merged_df, pd.DataFrame):
            raise TypeError("merged_df 必须是 pandas DataFrame")
        if not isinstance(measure_df, pd.DataFrame):
            raise TypeError("measure_df 必须是 pandas DataFrame")

        if ref_df.empty or merged_df.empty or measure_df.empty:
            raise ValueError("所有 DataFrame 都不能为空")

        self.ref_df = ref_df
        self.merged_df = merged_df
        self.measure_df = measure_df

    def save_to_file(self, file_path: str) -> None:
        """将历史数据对象中的三个DataFrame保存到一个HDF5文件中。

        Args:
            file_path: 保存文件路径（HDF5 格式）

        Raises:
            IOError: 如果文件无法写入
            ValueError: 如果文件路径无效

        Example:
            >>> bundle.save_to_file('/path/to/history.h5')
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("file_path 必须是有效的字符串路径")

        try:
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

            with pd.HDFStore(file_path, mode="w") as store:
                store.put("ref_df", self.ref_df, format="table")
                store.put("merged_df", self.merged_df, format="table")
                store.put("measure_df", self.measure_df, format="table")

            logger.info(f"历史数据成功保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存历史数据失败: {file_path}, 错误: {e}", exc_info=True)
            raise IOError(f"无法保存到 {file_path}: {e}") from e

    @staticmethod
    def load_from_file(file_paths: list[str]) -> "HistoryDataBundle":
        """从单个或多个文件中加载数据并返回 HistoryDataBundle 对象。

        支持加载单个 HDF5 文件或多个文件并合并。加载时会验证三个 DataFrame
        的行数是否一致，不一致的数据会被跳过。

        Args:
            file_paths: HDF5 文件路径列表

        Returns:
            合并后的 HistoryDataBundle 实例，包含所有文件的数据

        Raises:
            ValueError: 如果文件列表为空或所有文件都加载失败
            FileNotFoundError: 如果指定的文件不存在
            IOError: 如果 HDF5 文件读取失败

        Example:
            >>> bundles = HistoryDataBundle.load_from_file([
            ...     'history1.h5',
            ...     'history2.h5'
            ... ])
            >>> len(bundles.ref_df)  # 合并后的总行数
            200
        """
        if not file_paths:
            raise ValueError("file_paths 不能为空列表")

        if not isinstance(file_paths, list):
            raise TypeError("file_paths 必须是字符串列表")

        all_ref_dfs: list[pd.DataFrame] = []
        all_merged_dfs: list[pd.DataFrame] = []
        all_measure_dfs: list[pd.DataFrame] = []

        for file_path in file_paths:
            try:
                # 检查文件存在性
                if not os.path.exists(file_path):
                    logger.warning(f"文件不存在，跳过: {file_path}")
                    continue

                with pd.HDFStore(file_path, mode="r") as store:
                    try:
                        ref_df = store.get("ref_df")
                        merged_df = store.get("merged_df")
                        measure_df = store.get("measure_df")
                    except KeyError as ke:
                        logger.warning(
                            f"文件中缺少必需的数据集: {file_path}，错误: {ke}，跳过此文件"
                        )
                        continue

                    # 验证数据存在性
                    if ref_df is None or merged_df is None or measure_df is None:
                        logger.warning(
                            f"文件中缺少必需的数据集: {file_path}，跳过此文件"
                        )
                        continue

                    # 验证行数一致性
                    ref_len = len(ref_df)
                    merged_len = len(merged_df)
                    measure_len = len(measure_df)

                    if (ref_len == merged_len == measure_len):
                        all_ref_dfs.append(ref_df)
                        all_merged_dfs.append(merged_df)
                        all_measure_dfs.append(measure_df)
                        logger.info(
                            f"成功加载文件: {file_path}, "
                            f"行数: {ref_len}"
                        )
                    else:
                        logger.warning(
                            f"文件中 DataFrame 行数不一致，跳过: {file_path} "
                            f"(ref: {ref_len}, merged: {merged_len}, "
                            f"measure: {measure_len})"
                        )

            except FileNotFoundError as e:
                logger.error(f"文件不存在: {file_path}")
                raise FileNotFoundError(f"找不到文件: {file_path}") from e
            except IOError as e:
                logger.error(
                    f"HDF5 文件 I/O 错误: {file_path}, 错误: {e}",
                    exc_info=True,
                )
                raise IOError(f"无法读取 {file_path}: {e}") from e
            except Exception as e:
                logger.error(
                    f"读取文件失败: {file_path}, 错误: {e}",
                    exc_info=True,
                )
                raise IOError(f"无法读取 {file_path}: {e}") from e

        # 检查是否有成功加载的数据
        if not all_ref_dfs:
            raise ValueError(
                f"未能从提供的文件列表中加载任何有效数据: {file_paths}"
            )

        try:
            # 合并所有数据
            combined_ref = pd.concat(all_ref_dfs, ignore_index=True)
            combined_merged = pd.concat(all_merged_dfs, ignore_index=True)
            combined_measure = pd.concat(all_measure_dfs, ignore_index=True)

            logger.info(
                f"成功合并 {len(file_paths)} 个文件，"
                f"总行数: {len(combined_ref)}"
            )
            return HistoryDataBundle(combined_ref, combined_merged, combined_measure)

        except Exception as e:
            logger.error(f"合并数据框失败: {e}", exc_info=True)
            raise ValueError(f"无法合并加载的数据: {e}") from e
