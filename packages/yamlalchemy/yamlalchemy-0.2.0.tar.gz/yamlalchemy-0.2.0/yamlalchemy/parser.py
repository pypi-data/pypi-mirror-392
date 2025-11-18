
__all__ = ['parse']

from typing import List, Optional, Union, Dict, Any
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import Query
from sqlalchemy.sql.schema import Table, Column
import yaml
from yamlalchemy.constants import *
from sqlalchemy import MetaData
from sqlalchemy.sql.functions import func
from yamlalchemy.statement import _order, _where, _limit, _offset, _having


metadata = MetaData()


class QueryBuilder:
    session: Session
    table: Optional[Table]
    columns: List[Column]
    group: List[Column]
    order_by: List[Column]
    where: List[Column]
    having: List[Column]
    limit: Optional[int]
    offset: Optional[int]
    joins: List[Dict[str, Any]]

    def __init__(self, session: Session) -> None:
        self.session = session
        self.table = None
        self.columns = []
        self.group = []
        self.order_by = []
        self.where = []
        self.having = []
        self.limit = None
        self.offset = None
        self.joins = []

    def set_table(self, table: Table) -> None:
        self.table = table

    def set_columns(self, columns: List[Column]) -> None:
        self.columns = columns

    def set_group(self, group: List[Column]) -> None:
        self.group = group

    def set_order_by(self, order_by: List[Column]) -> None:
        self.order_by = order_by

    def set_where(self, where_clause: List[Column]) -> None:
        self.where = where_clause

    def set_having(self, having_clause: List[Column]) -> None:
        self.having = having_clause

    def set_limit(self, limit: Optional[int]) -> None:
        self.limit = limit

    def set_offset(self, offset: Optional[int]) -> None:
        self.offset = offset

    def set_joins(self, joins: List[Dict[str, Any]]) -> None:
        self.joins = joins

    def to_query(self) -> Query:
        query = self.session.query(self.table)

        for join_spec in self.joins:
            join_table = join_spec['table']
            join_on = join_spec['on']
            join_type = join_spec.get('type', JOIN_INNER)

            if join_type == JOIN_INNER:
                query = query.join(join_table, join_on)
            elif join_type == JOIN_LEFT_OUTER:
                query = query.outerjoin(join_table, join_on)
            elif join_type == JOIN_RIGHT_OUTER:
                query = query.outerjoin(join_table, join_on)
            elif join_type == JOIN_FULL_OUTER:
                query = query.outerjoin(join_table, join_on, full=True)

        query = query.with_entities(*self.columns)
        query = query.filter(*self.where)
        query = query.group_by(*self.group)
        query = query.order_by(*self.order_by)
        query = _having(self.having, query)
        query = _limit(self.limit, query)
        query = _offset(self.offset, query)

        return query


def query_fragment(table: Table, columns: List[Dict[str, Any]], reflection: Optional[AutomapBase] = None) -> List[Column]:
    """
    args:
        table: SQLAlchemy table class
        columns: yaml table dictionary.
        reflection: AutomapBase for resolving table.column references
    """

    if isinstance(columns, list) is False:
        raise Exception(
            f"Columns must be list. {type(columns)} given.")

    cols = []
    for column in columns:
        name = column.get(NAME, None)
        alias = column.get(ALIAS, None)
        expr = column.get(FUNC, None)
        direction = column.get(DIRECTION, None)
        where_clause = column.get(FILTER, None)

        if '.' in name and reflection:
            parts = name.split('.')
            if len(parts) == 2:
                source_table = reflection.classes[parts[0]]
                col = getattr(source_table, parts[1])
            else:
                col = getattr(table, name)
        else:
            col = getattr(table, name)

        if expr is not None:
            column_aggr_func = getattr(func, expr)
            col = column_aggr_func(col)
            col = col.label(name)

        if direction is not None and direction in QUERY_ORDERS:
            col = _order(col, direction)

        if where_clause is not None:
            col = _where(col, where_clause)

        if alias:
            col = col.label(alias)

        cols.append(col)

    return cols


def parse(yaml_content: Union[str, Dict[str, Any]], session: Session, reflection: AutomapBase) -> QueryBuilder:
    """
    Initial entry point for yamlalchemy.
    Parses the given YAML string to create a SqlAlchemy query

    args:
        yaml_content: YAML content or Python dictionary.
        session: SqlAlchemy Session
        reflection: SqlAlchemy AutomapBase
    """

    if not yaml_content:
        raise Exception('No yaml content given.')
    qd = yaml_content

    if isinstance(yaml_content, dict) is False:
        qd = yaml.safe_load(yaml_content)

    if not isinstance(qd, dict):
        raise TypeError(
            "Argument for query parsing must be a Python dictionary.")

    if FROM not in qd:
        raise Exception(f"Missing \"{FROM}\" argument in query.")

    if COLUMN not in qd:
        qd[COLUMN] = []

    if GROUP not in qd:
        qd[GROUP] = []

    if ORDER not in qd:
        qd[ORDER] = []

    if WHERE not in qd:
        qd[WHERE] = []

    if HAVING not in qd:
        qd[HAVING] = []

    if LIMIT not in qd:
        qd[LIMIT] = None

    if OFFSET not in qd:
        qd[OFFSET] = None

    if JOIN not in qd:
        qd[JOIN] = []

    table = reflection.classes[qd[FROM]]
    columns = query_fragment(table, qd[COLUMN], reflection)
    group_by = query_fragment(table, qd[GROUP], reflection)
    order_by = query_fragment(table, qd[ORDER], reflection)
    where = query_fragment(table, qd[WHERE], reflection)
    having = query_fragment(table, qd[HAVING], reflection)

    joins = []
    for join_def in qd[JOIN]:
        join_table_name = join_def.get(JOIN_TABLE)
        join_on_def = join_def.get(JOIN_ON)
        join_type = join_def.get(JOIN_TYPE, JOIN_INNER)

        if not join_table_name:
            raise Exception(f"Missing \"{JOIN_TABLE}\" in JOIN definition.")

        if not join_on_def:
            raise Exception(f"Missing \"{JOIN_ON}\" in JOIN definition.")

        join_table = reflection.classes[join_table_name]

        left_col = join_on_def.get(JOIN_LEFT_COL, '')
        right_col = join_on_def.get(JOIN_RIGHT_COL, '')

        if not left_col or not right_col:
            raise Exception(
                f"Missing \"{JOIN_LEFT_COL}\" or \"{JOIN_RIGHT_COL}\" in JOIN ON definition.")

        left_parts = left_col.split('.')
        right_parts = right_col.split('.')

        if len(left_parts) == 2:
            left_table = reflection.classes[left_parts[0]]
            left_column = getattr(left_table, left_parts[1])
        else:
            left_column = getattr(table, left_col)

        if len(right_parts) == 2:
            right_table = reflection.classes[right_parts[0]]
            right_column = getattr(right_table, right_parts[1])
        else:
            right_column = getattr(join_table, right_col)

        join_condition = left_column == right_column

        joins.append({
            'table': join_table,
            'on': join_condition,
            'type': join_type
        })

    limit = qd[LIMIT]
    offset = qd[OFFSET]

    qb = QueryBuilder(session=session)
    qb.set_table(table)
    qb.set_columns(columns)
    qb.set_where(where)
    qb.set_group(group_by)
    qb.set_having(having)
    qb.set_order_by(order_by)
    qb.set_joins(joins)
    qb.set_limit(limit)
    qb.set_offset(offset)

    return qb
