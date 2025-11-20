from david8.core.fn_generator import SeparatedStrArgsCallableFactory as _SeparatedStrArgsCallableFactory

# https://clickhouse.com/docs/sql-reference/functions/string-functions#concatWithSeparator
concat_with_separator = _SeparatedStrArgsCallableFactory(name='concatWithSeparator', separator=', ')
