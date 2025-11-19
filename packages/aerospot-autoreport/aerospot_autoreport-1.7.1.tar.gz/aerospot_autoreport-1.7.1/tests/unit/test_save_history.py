"""测试 HistoryDataBundle 模块的单元测试。

Tests:
    test_init_valid_dataframes: 测试有效 DataFrame 初始化
    test_init_invalid_dataframe_types: 测试无效 DataFrame 类型
    test_init_empty_dataframe: 测试空 DataFrame 错误
    test_save_to_file: 测试保存到 HDF5 文件
    test_save_to_file_invalid_path: 测试无效保存路径
    test_load_from_file_single: 测试加载单个文件
    test_load_from_file_multiple: 测试加载多个文件并合并
    test_load_from_file_empty_list: 测试空文件列表错误
    test_load_from_file_nonexistent: 测试不存在文件错误
    test_load_from_file_mismatched_length: 测试行数不一致处理
    test_load_from_file_missing_data: 测试缺少必需数据集错误
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.autoreport.processor.data.save_history import HistoryDataBundle


@pytest.fixture
def sample_dataframes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """创建示例 DataFrame 数据集。

    Returns:
        包含 ref_df、merged_df、measure_df 的元组
    """
    data = {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    ref = pd.DataFrame(data)
    merged = pd.DataFrame(data)
    measure = pd.DataFrame(data)
    return ref, merged, measure


@pytest.fixture
def temp_hdf5_dir() -> str:
    """创建临时目录用于保存 HDF5 文件。

    Yields:
        临时目录路径
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestHistoryDataBundleInit:
    """测试 HistoryDataBundle 初始化"""

    def test_init_valid_dataframes(self, sample_dataframes):
        """测试使用有效 DataFrame 初始化成功"""
        ref, merged, measure = sample_dataframes
        bundle = HistoryDataBundle(ref, merged, measure)

        assert bundle.ref_df.equals(ref)
        assert bundle.merged_df.equals(merged)
        assert bundle.measure_df.equals(measure)

    def test_init_invalid_ref_df_type(self, sample_dataframes):
        """测试 ref_df 不是 DataFrame 时抛出 TypeError"""
        _, merged, measure = sample_dataframes
        with pytest.raises(TypeError, match="ref_df 必须是 pandas DataFrame"):
            HistoryDataBundle([1, 2, 3], merged, measure)

    def test_init_invalid_merged_df_type(self, sample_dataframes):
        """测试 merged_df 不是 DataFrame 时抛出 TypeError"""
        ref, _, measure = sample_dataframes
        with pytest.raises(TypeError, match="merged_df 必须是 pandas DataFrame"):
            HistoryDataBundle(ref, "invalid", measure)

    def test_init_invalid_measure_df_type(self, sample_dataframes):
        """测试 measure_df 不是 DataFrame 时抛出 TypeError"""
        ref, merged, _ = sample_dataframes
        with pytest.raises(TypeError, match="measure_df 必须是 pandas DataFrame"):
            HistoryDataBundle(ref, merged, {"col": 123})

    def test_init_empty_dataframe(self):
        """测试空 DataFrame 时抛出 ValueError"""
        valid = pd.DataFrame({"col": [1, 2]})
        empty = pd.DataFrame()

        with pytest.raises(ValueError, match="所有 DataFrame 都不能为空"):
            HistoryDataBundle(empty, valid, valid)

        with pytest.raises(ValueError, match="所有 DataFrame 都不能为空"):
            HistoryDataBundle(valid, empty, valid)

        with pytest.raises(ValueError, match="所有 DataFrame 都不能为空"):
            HistoryDataBundle(valid, valid, empty)


class TestHistoryDataBundleSave:
    """测试 HistoryDataBundle 保存功能"""

    def test_save_to_file_success(self, sample_dataframes, temp_hdf5_dir):
        """测试成功保存到 HDF5 文件"""
        ref, merged, measure = sample_dataframes
        bundle = HistoryDataBundle(ref, merged, measure)

        file_path = os.path.join(temp_hdf5_dir, "test_data.h5")
        bundle.save_to_file(file_path)

        # 验证文件存在
        assert os.path.exists(file_path)

        # 验证文件内容
        with pd.HDFStore(file_path, mode="r") as store:
            assert "ref_df" in store
            assert "merged_df" in store
            assert "measure_df" in store

    def test_save_to_file_creates_directories(self, sample_dataframes, temp_hdf5_dir):
        """测试保存时自动创建不存在的目录"""
        ref, merged, measure = sample_dataframes
        bundle = HistoryDataBundle(ref, merged, measure)

        nested_path = os.path.join(temp_hdf5_dir, "nested", "dir", "test.h5")
        bundle.save_to_file(nested_path)

        assert os.path.exists(nested_path)

    def test_save_to_file_invalid_path(self, sample_dataframes):
        """测试无效文件路径时抛出 ValueError"""
        ref, merged, measure = sample_dataframes
        bundle = HistoryDataBundle(ref, merged, measure)

        with pytest.raises(ValueError, match="file_path 必须是有效的字符串路径"):
            bundle.save_to_file(None)

        with pytest.raises(ValueError, match="file_path 必须是有效的字符串路径"):
            bundle.save_to_file("")

    def test_save_to_file_overwrite(self, sample_dataframes, temp_hdf5_dir):
        """测试覆盖现有文件"""
        ref1, merged1, measure1 = sample_dataframes
        ref2 = pd.DataFrame({"col1": [10, 20], "col2": [30, 40]})
        merged2 = pd.DataFrame({"col1": [10, 20], "col2": [30, 40]})
        measure2 = pd.DataFrame({"col1": [10, 20], "col2": [30, 40]})

        file_path = os.path.join(temp_hdf5_dir, "test_data.h5")

        bundle1 = HistoryDataBundle(ref1, merged1, measure1)
        bundle1.save_to_file(file_path)

        bundle2 = HistoryDataBundle(ref2, merged2, measure2)
        bundle2.save_to_file(file_path)

        # 验证数据被覆盖
        loaded = HistoryDataBundle.load_from_file([file_path])
        assert loaded.ref_df.equals(ref2)
        assert len(loaded.ref_df) == 2


class TestHistoryDataBundleLoad:
    """测试 HistoryDataBundle 加载功能"""

    def test_load_from_file_single(self, sample_dataframes, temp_hdf5_dir):
        """测试加载单个 HDF5 文件"""
        ref, merged, measure = sample_dataframes
        bundle = HistoryDataBundle(ref, merged, measure)

        file_path = os.path.join(temp_hdf5_dir, "test_data.h5")
        bundle.save_to_file(file_path)

        # 加载并验证
        loaded = HistoryDataBundle.load_from_file([file_path])
        assert loaded.ref_df.equals(ref)
        assert loaded.merged_df.equals(merged)
        assert loaded.measure_df.equals(measure)

    def test_load_from_file_multiple(self, temp_hdf5_dir):
        """测试加载多个文件并合并"""
        # 创建两个不同的数据集
        data1 = {"col1": [1, 2], "col2": [3, 4]}
        data2 = {"col1": [5, 6], "col2": [7, 8]}

        bundle1 = HistoryDataBundle(
            pd.DataFrame(data1),
            pd.DataFrame(data1),
            pd.DataFrame(data1),
        )
        bundle2 = HistoryDataBundle(
            pd.DataFrame(data2),
            pd.DataFrame(data2),
            pd.DataFrame(data2),
        )

        file1 = os.path.join(temp_hdf5_dir, "test1.h5")
        file2 = os.path.join(temp_hdf5_dir, "test2.h5")

        bundle1.save_to_file(file1)
        bundle2.save_to_file(file2)

        # 加载并合并
        loaded = HistoryDataBundle.load_from_file([file1, file2])

        assert len(loaded.ref_df) == 4
        assert len(loaded.merged_df) == 4
        assert len(loaded.measure_df) == 4

    def test_load_from_file_empty_list(self):
        """测试空文件列表时抛出 ValueError"""
        with pytest.raises(ValueError, match="file_paths 不能为空列表"):
            HistoryDataBundle.load_from_file([])

    def test_load_from_file_invalid_type(self):
        """测试非列表类型参数时抛出 TypeError"""
        with pytest.raises(TypeError, match="file_paths 必须是字符串列表"):
            HistoryDataBundle.load_from_file("single_file.h5")

    def test_load_from_file_nonexistent(self):
        """测试加载不存在的文件时抛出 ValueError"""
        with pytest.raises(ValueError, match="未能从提供的文件列表中加载任何有效数据"):
            HistoryDataBundle.load_from_file(["/nonexistent/path/file.h5"])

    def test_load_from_file_mismatched_length(self, temp_hdf5_dir):
        """测试行数不一致的文件被跳过"""
        # 创建行数不同的 DataFrame
        data_valid = {"col": [1, 2, 3]}
        data_invalid = {"col": [1, 2]}

        ref_valid = pd.DataFrame(data_valid)
        merged_valid = pd.DataFrame(data_valid)
        measure_valid = pd.DataFrame(data_valid)

        ref_invalid = pd.DataFrame(data_invalid)
        merged_invalid = pd.DataFrame(data_valid)
        measure_invalid = pd.DataFrame(data_valid)

        bundle_valid = HistoryDataBundle(ref_valid, merged_valid, measure_valid)
        bundle_invalid = HistoryDataBundle(
            ref_invalid, merged_invalid, measure_invalid
        )

        file_valid = os.path.join(temp_hdf5_dir, "valid.h5")
        file_invalid = os.path.join(temp_hdf5_dir, "invalid.h5")

        bundle_valid.save_to_file(file_valid)
        bundle_invalid.save_to_file(file_invalid)

        # 加载时只读取有效文件
        loaded = HistoryDataBundle.load_from_file([file_valid, file_invalid])
        assert len(loaded.ref_df) == 3

    def test_load_from_file_missing_data(self, temp_hdf5_dir):
        """测试缺少必需数据集的文件被跳过"""
        file_path = os.path.join(temp_hdf5_dir, "incomplete.h5")

        # 创建不完整的 HDF5 文件
        with pd.HDFStore(file_path, mode="w") as store:
            store.put("ref_df", pd.DataFrame({"col": [1, 2, 3]}))
            # 缺少 merged_df 和 measure_df

        # 应该抛出错误，因为所有文件都无效
        with pytest.raises(ValueError, match="未能从提供的文件列表中加载任何有效数据"):
            HistoryDataBundle.load_from_file([file_path])

    def test_load_from_file_partial_missing_data(self, temp_hdf5_dir):
        """测试部分文件缺少数据时只加载有效文件"""
        # 创建一个完整的文件
        data = {"col": [1, 2, 3]}
        bundle = HistoryDataBundle(
            pd.DataFrame(data),
            pd.DataFrame(data),
            pd.DataFrame(data),
        )
        file_complete = os.path.join(temp_hdf5_dir, "complete.h5")
        bundle.save_to_file(file_complete)

        # 创建一个不完整的文件
        file_incomplete = os.path.join(temp_hdf5_dir, "incomplete.h5")
        with pd.HDFStore(file_incomplete, mode="w") as store:
            store.put("ref_df", pd.DataFrame({"col": [1, 2, 3]}))

        # 加载时应该只使用完整的文件
        loaded = HistoryDataBundle.load_from_file([file_complete, file_incomplete])
        assert len(loaded.ref_df) == 3

    @pytest.mark.parametrize(
        "col_data,expected_length",
        [
            ([1, 2, 3], 3),
            ([1.0, 2.5, 3.7], 3),
            (["a", "b", "c"], 3),
        ],
    )
    def test_load_from_file_multiple_types(
        self, col_data, expected_length, temp_hdf5_dir
    ):
        """测试加载不同数据类型的 DataFrame"""
        data = {"col": col_data}
        bundle = HistoryDataBundle(
            pd.DataFrame(data),
            pd.DataFrame(data),
            pd.DataFrame(data),
        )

        file_path = os.path.join(temp_hdf5_dir, "test.h5")
        bundle.save_to_file(file_path)

        loaded = HistoryDataBundle.load_from_file([file_path])
        assert len(loaded.ref_df) == expected_length


class TestHistoryDataBundleRoundtrip:
    """集成测试：保存和加载往返"""

    def test_save_and_load_roundtrip(self, sample_dataframes, temp_hdf5_dir):
        """测试保存后加载数据完整性"""
        ref, merged, measure = sample_dataframes
        bundle = HistoryDataBundle(ref, merged, measure)

        file_path = os.path.join(temp_hdf5_dir, "roundtrip.h5")
        bundle.save_to_file(file_path)

        loaded = HistoryDataBundle.load_from_file([file_path])

        # 验证数据完整性
        pd.testing.assert_frame_equal(loaded.ref_df, ref)
        pd.testing.assert_frame_equal(loaded.merged_df, merged)
        pd.testing.assert_frame_equal(loaded.measure_df, measure)

    def test_multiple_roundtrips(self, sample_dataframes, temp_hdf5_dir):
        """测试多次保存和加载"""
        ref, merged, measure = sample_dataframes

        file_path1 = os.path.join(temp_hdf5_dir, "roundtrip1.h5")
        file_path2 = os.path.join(temp_hdf5_dir, "roundtrip2.h5")

        # 第一轮
        bundle1 = HistoryDataBundle(ref, merged, measure)
        bundle1.save_to_file(file_path1)

        # 第二轮：从第一个文件加载并保存到第二个文件
        loaded1 = HistoryDataBundle.load_from_file([file_path1])
        loaded1.save_to_file(file_path2)

        # 第三轮：加载第二个文件
        loaded2 = HistoryDataBundle.load_from_file([file_path2])

        # 验证数据一致性
        pd.testing.assert_frame_equal(loaded2.ref_df, ref)
        pd.testing.assert_frame_equal(loaded2.merged_df, merged)
        pd.testing.assert_frame_equal(loaded2.measure_df, measure)
