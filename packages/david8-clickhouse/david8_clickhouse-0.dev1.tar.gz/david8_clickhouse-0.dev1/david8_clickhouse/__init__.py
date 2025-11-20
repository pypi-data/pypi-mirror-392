from david8.core.base_dialect import BaseDialect as _BaseDialect
from david8.core.base_query_builder import BaseQueryBuilder as _BaseQueryBuilder
from david8.param_styles import PyFormatParamStyle
from david8.protocols.query_builder import QueryBuilderProtocol


def get_qb(is_quote_mode: bool = False) -> QueryBuilderProtocol:
    dialect = _BaseDialect(PyFormatParamStyle(), is_quote_mode)
    return _BaseQueryBuilder(dialect)
