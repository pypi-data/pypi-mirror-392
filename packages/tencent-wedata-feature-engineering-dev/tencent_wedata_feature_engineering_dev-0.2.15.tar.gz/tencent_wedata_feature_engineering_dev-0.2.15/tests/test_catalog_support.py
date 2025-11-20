"""
测试 catalog_name 参数支持
"""
import os
import pytest
from unittest.mock import Mock, MagicMock, patch

from wedata.common.utils import common_utils


class TestBuildFullTableName:
    """测试 build_full_table_name 函数的 catalog 支持"""
    
    def test_build_table_name_without_catalog(self):
        """测试不提供 catalog 时的行为（向后兼容）"""
        os.environ["WEDATA_DEFAULT_FEATURE_STORE_DATABASE"] = "test_db"
        
        result = common_utils.build_full_table_name("test_table")
        assert result == "test_db.test_table"
        
        result = common_utils.build_full_table_name("test_table", "custom_db")
        assert result == "custom_db.test_table"
    
    def test_build_table_name_with_explicit_catalog(self):
        """测试显式提供 catalog 时的行为"""
        os.environ["WEDATA_DEFAULT_FEATURE_STORE_DATABASE"] = "test_db"
        
        result = common_utils.build_full_table_name(
            "test_table", 
            catalog_name="my_catalog"
        )
        assert result == "my_catalog.test_db.test_table"
        
        result = common_utils.build_full_table_name(
            "test_table", 
            "custom_db",
            catalog_name="my_catalog"
        )
        assert result == "my_catalog.custom_db.test_table"
    
    def test_build_table_name_with_spark_client(self):
        """测试使用 spark_client 获取当前 catalog"""
        os.environ["WEDATA_DEFAULT_FEATURE_STORE_DATABASE"] = "test_db"

        # Mock SparkClient
        mock_spark_client = Mock()
        mock_spark_client.get_current_catalog.return_value = "spark_catalog"

        result = common_utils.build_full_table_name(
            "test_table",
            spark_client=mock_spark_client
        )
        assert result == "spark_catalog.test_db.test_table"
        mock_spark_client.get_current_catalog.assert_called_once()

    def test_catalog_name_overrides_spark_client(self):
        """测试显式 catalog_name 优先于 spark_client"""
        os.environ["WEDATA_DEFAULT_FEATURE_STORE_DATABASE"] = "test_db"

        mock_spark_client = Mock()
        mock_spark_client.get_current_catalog.return_value = "spark_catalog"

        result = common_utils.build_full_table_name(
            "test_table",
            catalog_name="explicit_catalog",
            spark_client=mock_spark_client
        )
        assert result == "explicit_catalog.test_db.test_table"
        # 不应该调用 get_current_catalog
        mock_spark_client.get_current_catalog.assert_not_called()

    def test_spark_client_exception_fallback(self):
        """测试当 spark_client.get_current_catalog 抛异常时回退到2级表名"""
        os.environ["WEDATA_DEFAULT_FEATURE_STORE_DATABASE"] = "test_db"

        mock_spark_client = Mock()
        mock_spark_client.get_current_catalog.side_effect = Exception("Catalog error")

        result = common_utils.build_full_table_name(
            "test_table",
            spark_client=mock_spark_client
        )
        # 应该回退到2级表名
        assert result == "test_db.test_table"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

