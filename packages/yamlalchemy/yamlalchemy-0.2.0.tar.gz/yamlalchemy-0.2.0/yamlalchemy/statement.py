__all__ = ['_order', '_where', '_where_comp', '_limit', '_offset', '_having']

from typing import List, Dict, Any, Optional
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from yamlalchemy.constants import *
from sqlalchemy.sql.expression import and_, or_, not_


def _where_comp(col: Column, comp: str, values: List[Any]) -> List[BinaryExpression]:
    if comp == COMP_NEQ:
        return [col != value for value in values]
    if comp == COMP_GT:
        return [col > value for value in values]
    if comp == COMP_GTE:
        return [col >= value for value in values]
    if comp == COMP_LT:
        return [col < value for value in values]
    if comp == COMP_LTE:
        return [col <= value for value in values]
    if comp == COMP_EQ:
        return [col == value for value in values]
    if comp == COMP_LIKE:
        return [col.like(value) for value in values]
    if comp == COMP_NLIKE:
        return [col.not_like(value) for value in values]
    if comp == COMP_ILIKE:
        return [col.ilike(value) for value in values]
    if comp == COMP_NILIKE:
        return [col.not_ilike(value) for value in values]
    if comp == COMP_IN:
        return [col.in_(values)]
    if comp == COMP_NIN:
        return [col.notin_(values)]
    if comp == COMP_IS:
        return [col.is_(value) for value in values]
    if comp == COMP_NIS:
        return [col.is_not(value) for value in values]
    if comp == COMP_CONTAINS:
        return [col.contains(value) for value in values]
    if comp == COMP_STARTS_WITH:
        return [col.startswith(value) for value in values]
    if comp == COMP_ENDS_WITH:
        return [col.endswith(value) for value in values]


def _where(col: Column, where_clause: Dict[str, Any]) -> BooleanClauseList:
    """
    Definition
    """

    for op, clause in where_clause.items():
        filter_criteria = []

        if op in COMPARATORS:
            values = [clause]
            _values = _where_comp(col, op, values)
            filter_criteria.extend(_values)

        if op in OPERATORS:
            for comp, values in clause.items():
                if isinstance(values, list) is False:
                    values = [values]
                if comp in COMPARATORS:
                    _values = _where_comp(col, comp, values)
                    filter_criteria.extend(_values)

        col = and_(*filter_criteria)
        if op == OP_OR:
            col = or_(*filter_criteria)
        if op == OP_NOT:
            col = not_(*filter_criteria)
    return col


def _order(col: Column, direction: str) -> Column:
    if direction.lower() == ORDER_ASC:
        col = col.asc()
    if direction.lower() == ORDER_DESC:
        col = col.desc()

    return col


def _limit(limit: Optional[int], query: Query) -> Query:
    if limit is not None and isinstance(limit, int):
        query = query.limit(limit)

    return query


def _offset(offset: Optional[int], query: Query) -> Query:
    if offset is not None and isinstance(offset, int):
        query = query.offset(offset)

    return query


def _having(having_clause: List, query: Query) -> Query:
    for having in having_clause:
        # Having takes 2 positional arguments.
        # Each having argument must be bind one by one to query.
        query = query.having(having)
    return query
