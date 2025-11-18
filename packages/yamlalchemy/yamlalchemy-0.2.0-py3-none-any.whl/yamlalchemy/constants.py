__all__ = [
    'FROM',
    'COLUMN',
    'FUNC',
    'ALIAS',
    'GROUP',
    'ORDER',
    'ORDER_ASC',
    'ORDER_DESC',
    'NAME',
    'DIRECTION',
    'WHERE',
    'FILTER',
    'OP_AND',
    'OP_OR',
    'OP_NOT',
    'OPERATORS',
    'QUERY_ORDERS',
    'COMP_EQ',
    'COMP_GT',
    'COMP_GTE',
    'COMP_LT',
    'COMP_LTE',
    'COMP_NEQ',
    'COMP_LIKE',
    'COMP_NLIKE',
    'COMP_ILIKE',
    'COMP_NILIKE',
    'COMP_IN',
    'COMP_NIN',
    'COMP_IS',
    'COMP_NIS',
    'COMP_CONTAINS',
    'COMP_STARTS_WITH',
    'COMP_ENDS_WITH',
    'COMPARATORS',
    'LIMIT',
    'OFFSET',
    'HAVING',
    'JOIN',
    'JOIN_TABLE',
    'JOIN_ON',
    'JOIN_LEFT_COL',
    'JOIN_RIGHT_COL',
    'JOIN_TYPE',
    'JOIN_INNER',
    'JOIN_LEFT_OUTER',
    'JOIN_RIGHT_OUTER',
    'JOIN_FULL_OUTER',
    'JOIN_TYPES'
]


FROM = '$from'
LIMIT = '$limit'
OFFSET = '$offset'
COLUMN = '$column'
GROUP = '$group'
FUNC = '$func'
ALIAS = '$alias'
NAME = '$name'
ORDER = '$order'
DIRECTION = '$direction'

WHERE = '$where'
FILTER = '$filter'
HAVING = '$having'

# JOIN constants
JOIN = '$join'
JOIN_TABLE = '$table'
JOIN_ON = '$on'
JOIN_LEFT_COL = '$left'
JOIN_RIGHT_COL = '$right'
JOIN_TYPE = '$type'

# JOIN types
JOIN_INNER = 'inner'
JOIN_LEFT_OUTER = 'left'
JOIN_RIGHT_OUTER = 'right'
JOIN_FULL_OUTER = 'outer'
JOIN_TYPES = {JOIN_INNER, JOIN_LEFT_OUTER, JOIN_RIGHT_OUTER, JOIN_FULL_OUTER}

OP_AND = "$and"
OP_OR = "$or"
OP_NOT = "$not"
OPERATORS = {OP_AND, OP_OR, OP_NOT}

ORDER_ASC = 'asc'
ORDER_DESC = 'desc'
QUERY_ORDERS = {ORDER_ASC, ORDER_DESC}


COMP_EQ = "$eq"
COMP_GT = "$gt"
COMP_GTE = "$gte"
COMP_LT = "$lt"
COMP_LTE = "$lte"
COMP_NEQ = "$neq"
COMP_LIKE = "$like"
COMP_ILIKE = "$ilike"
COMP_NLIKE = "$nlike"
COMP_NILIKE = "$nilike"
COMP_IN = "$in"
COMP_NIN = "$nin"
COMP_IS = "$is"
COMP_NIS = "$nis"
COMP_CONTAINS = "$contains"
COMP_STARTS_WITH = "$startswith"
COMP_ENDS_WITH = "$endswith"

COMPARATORS = {COMP_EQ, COMP_GT, COMP_GTE, COMP_LT, COMP_LTE, COMP_NEQ, COMP_LIKE, COMP_IN, COMP_NIN,
               COMP_IS, COMP_NIS, COMP_ILIKE, COMP_NLIKE, COMP_NILIKE, COMP_CONTAINS, COMP_STARTS_WITH, COMP_ENDS_WITH}
