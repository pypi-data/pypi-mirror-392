"""
SQL Validation Tests
Tests that verify YAML → SQL conversion produces valid SQL syntax
"""
import unittest
from yamlalchemy import parse
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.dialects import mysql, postgresql, sqlite

Base = declarative_base()


class Product(Base):
    __tablename__ = 'Product'
    ProductID = Column(Integer, primary_key=True)
    Name = Column(String(50))
    Color = Column(String(15))
    ListPrice = Column(Float)
    CategoryID = Column(Integer)
    SellStartDate = Column(Date)


class ProductSubcategory(Base):
    __tablename__ = 'ProductSubcategory'
    ProductSubcategoryID = Column(Integer, primary_key=True)
    Name = Column(String(50))


class TestSQLValidation(unittest.TestCase):
    """Test that generated SQL is syntactically valid"""

    @classmethod
    def setUpClass(cls):
        """Set up mock database and tables"""
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(cls.engine)
        cls.session = Session(cls.engine)

        cls.base = automap_base()
        cls.base.classes.Product = Product
        cls.base.classes.ProductSubcategory = ProductSubcategory

    def _compile_sql(self, query, dialect=None):
        """Helper to compile query to SQL string"""
        if dialect:
            return str(query.statement.compile(
                dialect=dialect,
                compile_kwargs={"literal_binds": True}
            ))
        return str(query.statement.compile(compile_kwargs={"literal_binds": True}))

    def test_simple_select_sql_valid(self):
        """Test simple SELECT produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
            - $name: Color
        $where:
            - $name: ListPrice
              $filter:
                $gt: 100
        $limit: 10
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)

        # Verify SQL contains expected keywords
        self.assertIn('SELECT', sql.upper())
        self.assertIn('FROM', sql.upper())
        self.assertIn('WHERE', sql.upper())
        self.assertIn('LIMIT', sql.upper())
        self.assertIn('> 100', sql)

    def test_join_sql_valid(self):
        """Test JOIN produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Product.Name
            - $name: ProductSubcategory.Name
              $alias: Category
        $join:
            - $table: ProductSubcategory
              $on:
                $left: Product.CategoryID
                $right: ProductSubcategory.ProductSubcategoryID
              $type: inner
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)

        # Verify SQL contains JOIN
        self.assertIn('JOIN', sql.upper())
        self.assertIn('ProductSubcategory', sql)
        self.assertIn('ON', sql.upper())

    def test_aggregation_sql_valid(self):
        """Test aggregation query produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Color
            - $name: ListPrice
              $func: avg
              $alias: AvgPrice
            - $name: ProductID
              $func: count
              $alias: ProductCount
        $group:
            - $name: Color
        $having:
            - $name: ListPrice
              $func: avg
              $filter:
                $gt: 200
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)

        # Verify SQL contains aggregation keywords
        self.assertIn('AVG', sql.upper())
        self.assertIn('COUNT', sql.upper())
        self.assertIn('GROUP BY', sql.upper())
        self.assertIn('HAVING', sql.upper())

    def test_complex_query_sql_valid(self):
        """Test complex query with all features produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Product.Color
              $alias: Color
            - $name: ProductSubcategory.Name
              $alias: Category
            - $name: Product.ListPrice
              $func: avg
              $alias: AvgPrice
        $join:
            - $table: ProductSubcategory
              $on:
                $left: Product.CategoryID
                $right: ProductSubcategory.ProductSubcategoryID
              $type: inner
        $where:
            - $name: Color
              $filter:
                $nis: null
            - $name: ListPrice
              $filter:
                $and:
                  $gt: 50
                  $lt: 1000
        $group:
            - $name: Product.Color
            - $name: ProductSubcategory.Name
        $having:
            - $name: ListPrice
              $func: avg
              $filter:
                $gt: 200
        $order:
            - $name: Product.Color
              $direction: asc
        $limit: 20
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)

        # Verify all SQL components present
        self.assertIn('SELECT', sql.upper())
        self.assertIn('JOIN', sql.upper())
        self.assertIn('WHERE', sql.upper())
        self.assertIn('GROUP BY', sql.upper())
        self.assertIn('HAVING', sql.upper())
        self.assertIn('ORDER BY', sql.upper())
        self.assertIn('LIMIT', sql.upper())

    def test_mysql_dialect_valid(self):
        """Test MySQL dialect produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $where:
            - $name: Name
              $filter:
                $like: '%Bike%'
        $limit: 5
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query, dialect=mysql.dialect())

        # MySQL uses backticks
        self.assertIn('`', sql)
        self.assertIn('LIMIT', sql.upper())

    def test_postgresql_dialect_valid(self):
        """Test PostgreSQL dialect produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $where:
            - $name: Name
              $filter:
                $like: '%Bike%'
        $limit: 5
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query, dialect=postgresql.dialect())

        # PostgreSQL uses double quotes
        self.assertIn('"', sql)
        self.assertIn('LIMIT', sql.upper())

    def test_sqlite_dialect_valid(self):
        """Test SQLite dialect produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $limit: 5
        $offset: 10
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query, dialect=sqlite.dialect())

        # SQLite includes OFFSET
        self.assertIn('LIMIT', sql.upper())
        self.assertIn('OFFSET', sql.upper())

    def test_where_operators_sql_valid(self):
        """Test all WHERE operators produce valid SQL"""
        operators = [
            ('$gt', '>'),
            ('$gte', '>='),
            ('$lt', '<'),
            ('$lte', '<='),
            ('$neq', '!='),
        ]

        for yaml_op, sql_op in operators:
            with self.subTest(operator=yaml_op):
                yaml_content = f"""
                $from: Product
                $column:
                    - $name: Name
                $where:
                    - $name: ListPrice
                      $filter:
                        {yaml_op}: 100
                """
                query = parse(yaml_content, self.session, self.base).to_query()
                sql = self._compile_sql(query)
                self.assertIn(sql_op, sql, f"Operator {yaml_op} should produce {sql_op}")

    def test_null_checks_sql_valid(self):
        """Test NULL checks produce valid SQL"""
        # IS NULL
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $where:
            - $name: Color
              $filter:
                $is: null
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)
        self.assertIn('IS NULL', sql.upper())

        # IS NOT NULL
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $where:
            - $name: Color
              $filter:
                $nis: null
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)
        self.assertIn('IS NOT NULL', sql.upper())

    def test_in_operator_sql_valid(self):
        """Test IN operator produces valid SQL"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Color
        $where:
            - $name: Color
              $filter:
                $in:
                    - Red
                    - Blue
                    - Black
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        # IN operator doesn't work well with literal_binds, use normal compile
        sql = str(query.statement.compile())
        self.assertIn('IN', sql.upper())

    def test_order_by_sql_valid(self):
        """Test ORDER BY produces valid SQL"""
        # Ascending
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $order:
            - $name: Name
              $direction: asc
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)
        self.assertIn('ORDER BY', sql.upper())
        self.assertIn('ASC', sql.upper())

        # Descending
        yaml_content = """
        $from: Product
        $column:
            - $name: Name
        $order:
            - $name: Name
              $direction: desc
        """
        query = parse(yaml_content, self.session, self.base).to_query()
        sql = self._compile_sql(query)
        self.assertIn('ORDER BY', sql.upper())
        self.assertIn('DESC', sql.upper())

    def test_sql_compilation_no_errors(self):
        """Test that SQL compilation doesn't raise errors"""
        yaml_content = """
        $from: Product
        $column:
            - $name: Product.Color
            - $name: ProductSubcategory.Name
              $alias: Category
        $join:
            - $table: ProductSubcategory
              $on:
                $left: Product.CategoryID
                $right: ProductSubcategory.ProductSubcategoryID
        $where:
            - $name: ListPrice
              $filter:
                $gt: 100
        """
        query = parse(yaml_content, self.session, self.base).to_query()

        # Should not raise any exception
        try:
            sql = self._compile_sql(query)
            self.assertIsNotNone(sql)
            self.assertGreater(len(sql), 0)
        except Exception as e:
            self.fail(f"SQL compilation should not raise exception: {e}")


if __name__ == '__main__':
    unittest.main()
