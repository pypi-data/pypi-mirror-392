import unittest
from unittest.mock import Mock, MagicMock
from yamlalchemy import parse
from yamlalchemy.parser import QueryBuilder, query_fragment
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.ext.automap import automap_base

Base = declarative_base()


class Product(Base):
    """Mock Product table for testing"""
    __tablename__ = 'Product'

    ProductID = Column(Integer, primary_key=True)
    Name = Column(String(50))
    Color = Column(String(15))
    ListPrice = Column(Float)
    SafetyStockLevel = Column(Integer)
    Class = Column(String(2))
    SellStartDate = Column(Date)
    CategoryID = Column(Integer)


class Category(Base):
    """Mock Category table for testing"""
    __tablename__ = 'Category'

    CategoryID = Column(Integer, primary_key=True)
    CategoryName = Column(String(50))


class Supplier(Base):
    """Mock Supplier table for testing"""
    __tablename__ = 'Supplier'

    SupplierID = Column(Integer, primary_key=True)
    SupplierName = Column(String(50))
    ProductID = Column(Integer)


class TestParserUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up in-memory SQLite database for testing"""
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.session = Session(cls.engine)

        # Create automap base with our mock tables
        cls.base = automap_base()
        cls.base.classes.Product = Product
        cls.base.classes.Category = Category
        cls.base.classes.Supplier = Supplier

    def test_query_builder_initialization(self):
        """Test QueryBuilder initialization"""
        qb = QueryBuilder(self.session)
        self.assertEqual(qb.session, self.session)
        self.assertIsNone(qb.table)
        self.assertEqual(qb.columns, [])
        self.assertEqual(qb.group, [])
        self.assertEqual(qb.order_by, [])
        self.assertEqual(qb.where, [])
        self.assertEqual(qb.having, [])
        self.assertIsNone(qb.limit)
        self.assertIsNone(qb.offset)

    def test_simple_select(self):
        """Test basic SELECT query"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
                -
                    $name: Color
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)
        # Verify the query can be compiled
        str(qs.statement.compile())

    def test_where_greater_than(self):
        """Test WHERE with greater than operator"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: ListPrice
                    $filter:
                        $gt: 100
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_less_than_equal(self):
        """Test WHERE with less than or equal operator"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: ListPrice
                    $filter:
                        $lte: 1000
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_in_operator(self):
        """Test WHERE IN operator"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
            $where:
                -
                    $name: Color
                    $filter:
                        $in:
                            - Red
                            - Blue
                            - Black
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_not_in_operator(self):
        """Test WHERE NOT IN operator"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
            $where:
                -
                    $name: Color
                    $filter:
                        $nin:
                            - Red
                            - Blue
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_is_null(self):
        """Test WHERE IS NULL"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: Class
                    $filter:
                        $is: null
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_is_not_null(self):
        """Test WHERE IS NOT NULL"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
            $where:
                -
                    $name: Color
                    $filter:
                        $nis: null
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_like(self):
        """Test WHERE LIKE operator"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: Name
                    $filter:
                        $like: '%Bike%'
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_contains(self):
        """Test WHERE contains (LIKE wrapper)"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: Class
                    $filter:
                        $contains: A
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_startswith(self):
        """Test WHERE startswith"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: Name
                    $filter:
                        $startswith: Mountain
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_where_endswith(self):
        """Test WHERE endswith"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $where:
                -
                    $name: Name
                    $filter:
                        $endswith: Bike
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_aggregate_avg(self):
        """Test aggregate function AVG"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
                -
                    $name: ListPrice
                    $func: avg
            $group:
                -
                    $name: Color
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_aggregate_sum(self):
        """Test aggregate function SUM"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
                -
                    $name: SafetyStockLevel
                    $func: sum
            $group:
                -
                    $name: Color
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_aggregate_count(self):
        """Test aggregate function COUNT"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
                -
                    $name: ProductID
                    $func: count
            $group:
                -
                    $name: Color
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_order_by_asc(self):
        """Test ORDER BY ascending"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $order:
                -
                    $name: Name
                    $direction: asc
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_order_by_desc(self):
        """Test ORDER BY descending"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $order:
                -
                    $name: ListPrice
                    $direction: desc
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_limit(self):
        """Test LIMIT"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $limit: 5
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_offset(self):
        """Test OFFSET"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $offset: 10
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_limit_and_offset(self):
        """Test LIMIT and OFFSET together"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $limit: 5
            $offset: 10
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_column_alias(self):
        """Test column with alias"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
                    $alias: Product Color
                -
                    $name: ListPrice
                    $alias: Price
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_dict_input(self):
        """Test parsing from dictionary instead of YAML string"""
        query_dict = {
            '$from': 'Product',
            '$column': [
                {'$name': 'Name'},
                {'$name': 'Color'}
            ],
            '$limit': 10
        }
        qs = parse(query_dict, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_complex_query(self):
        """Test complex query with multiple features"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Color
                    $alias: Product Color
                -
                    $name: ListPrice
                    $alias: Average Price
                    $func: avg
            $where:
                -
                    $name: Color
                    $filter:
                        $nis: null
                -
                    $name: ListPrice
                    $filter:
                        $gt: 100
            $group:
                -
                    $name: Color
            $order:
                -
                    $name: Color
                    $direction: asc
            $limit: 10
            $offset: 0
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_missing_from_raises_exception(self):
        """Test that missing $from raises exception"""
        yaml_content = """
            $column:
                -
                    $name: Name
        """
        with self.assertRaises(Exception) as context:
            parse(yaml_content, self.session, self.base)
        self.assertIn('$from', str(context.exception))

    def test_empty_content_raises_exception(self):
        """Test that empty content raises exception"""
        with self.assertRaises(Exception) as context:
            parse('', self.session, self.base)
        self.assertIn('No yaml content', str(context.exception))

    def test_invalid_yaml_structure(self):
        """Test that invalid YAML structure raises exception"""
        yaml_content = "invalid: yaml: structure:"
        with self.assertRaises(Exception):
            parse(yaml_content, self.session, self.base)

    def test_inner_join(self):
        """Test INNER JOIN"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
                -
                    $name: Category.CategoryName
            $join:
                -
                    $table: Category
                    $on:
                        $left: Product.CategoryID
                        $right: Category.CategoryID
                    $type: inner
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)
        # Verify the query can be compiled
        str(qs.statement.compile())

    def test_left_join(self):
        """Test LEFT OUTER JOIN"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
                -
                    $name: Category.CategoryName
            $join:
                -
                    $table: Category
                    $on:
                        $left: Product.CategoryID
                        $right: Category.CategoryID
                    $type: left
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_join_without_type_defaults_to_inner(self):
        """Test JOIN without type specification defaults to INNER"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
                -
                    $name: Category.CategoryName
            $join:
                -
                    $table: Category
                    $on:
                        $left: Product.CategoryID
                        $right: Category.CategoryID
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_multiple_joins(self):
        """Test multiple JOINs"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
                -
                    $name: Category.CategoryName
                -
                    $name: Supplier.SupplierName
            $join:
                -
                    $table: Category
                    $on:
                        $left: Product.CategoryID
                        $right: Category.CategoryID
                    $type: inner
                -
                    $table: Supplier
                    $on:
                        $left: Product.ProductID
                        $right: Supplier.ProductID
                    $type: left
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_join_with_where(self):
        """Test JOIN with WHERE clause"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
                -
                    $name: Category.CategoryName
            $join:
                -
                    $table: Category
                    $on:
                        $left: Product.CategoryID
                        $right: Category.CategoryID
                    $type: inner
            $where:
                -
                    $name: ListPrice
                    $filter:
                        $gt: 100
        """
        qs = parse(yaml_content, self.session, self.base).to_query()
        self.assertIsNotNone(qs)

    def test_join_missing_table_raises_exception(self):
        """Test that missing $table in JOIN raises exception"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $join:
                -
                    $on:
                        $left: Product.CategoryID
                        $right: Category.CategoryID
        """
        with self.assertRaises(Exception) as context:
            parse(yaml_content, self.session, self.base)
        self.assertIn('$table', str(context.exception))

    def test_join_missing_on_raises_exception(self):
        """Test that missing $on in JOIN raises exception"""
        yaml_content = """
            $from: Product
            $column:
                -
                    $name: Name
            $join:
                -
                    $table: Category
        """
        with self.assertRaises(Exception) as context:
            parse(yaml_content, self.session, self.base)
        self.assertIn('$on', str(context.exception))


if __name__ == '__main__':
    unittest.main()
