"""
QueryBuilder helps make SQL query.

Example:
    select = QueryBuilder().select('table_name')
    select.field(('field_a', 'field_b'))
    select.where('field_a', '=', 10)

    print(select.build())
"""


class QueryBuilder(object):
    def __init__(self, pretty_print=False):
        self.operand = ""
        self.pretty_print = pretty_print
        if pretty_print:
            self.space = "\n "
        else:
            self.space = " "

        # SELECT
        self.__from_table = list()
        self.__field = list()
        self.__where = list()
        self.__join = list()
        self.__order = list()
        self.__group_by = list()
        self.__having = list()

        # INSERT
        self.__to_table = ""
        self.__value = list()

    def select(self, table):
        self.__from_table.append(table)
        self.operand = "SELECT"

        return self

    def insert(self, table):
        self.operand = "INSERT"
        self.__to_table = table

        return self

    def delete(self, table):
        self.operand = "DELETE"
        self.__to_table = table

        return self

    def where(self, lhs, op, rhs):
        self.__where.append(('AND', lhs, op, rhs))

        return self

    def or_where(self, lhs, op, rhs):
        self.__where.append(('OR ', lhs, op, rhs))

        return self

    def join(self, join_table, lhs, op, rhs):
        self.__join.append(('INNER', join_table, lhs, op, rhs))

        return self

    def left_join(self, join_table, lhs, op, rhs):
        self.__join.append(('LEFT', join_table, lhs, op, rhs))

        return self

    def right_join(self, join_table, lhs, op, rhs):
        self.__join.append(('RIGHT', join_table, lhs, op, rhs))

        return self

    def outer_join(self, join_table, lhs, op, rhs):
        self.__join.append(('OUTER', join_table, lhs, op, rhs))

        return self

    def group_by(self, field):
        self.__group_by.append(field)

        return self

    def having(self, lhs, op, rhs):
        self.__having.append(('AND', lhs, op, rhs))

        return self

    def or_having(self, lhs, op, rhs):
        self.__having.append(('OR ', lhs, op, rhs))

        return self

    def order(self, order_field, direction="ASC"):
        self.__order.append((order_field, direction))

        return self

    def field(self, field):
        if isinstance(field, list) or isinstance(field, tuple):
            for f in field:
                self.__field.append(f)

        else:
            self.__field.append(field)

        return self

    def value(self, value):
        value = value.strip()

        if not value.startswith('('):
            value = '(' + value

        if not value.endswith(')'):
            value += ')'

        self.__value.append(value)

        return self

    def build(self):
        operand_builder = {
            "SELECT": self.__build_select,
            "INSERT": self.__build_insert,
            "DELETE": self.__build_delete
        }

        if self.operand not in operand_builder:
            return ""

        result = operand_builder[self.operand]()

        return result

    def __build_select(self):
        build_sql = "SELECT "

        if len(self.__field) == 0:
            build_sql += "*"
        else:
            build_sql += ", ".join(self.__field)

        build_sql += self.space
        build_sql += " FROM "
        build_sql += ", ".join(self.__from_table)
        build_sql += self.space

        if len(self.__join) > 0:
            for join_type, join_table, lhs, op, rhs in self.__join:
                build_sql += " {join_type} JOIN {join_table} ON {lhs} {op} {rhs} ".format(
                    join_type=join_type,
                    join_table=join_table,
                    lhs=lhs, op=op, rhs=rhs
                )

                build_sql += self.space

        if len(self.__where) > 0:
            build_sql += " WHERE "
            where_sql = ""

            for and_or, lhs, op, rhs in self.__where:
                where_sql += " {and_or} {lhs} {op} {rhs}".format(
                    and_or=and_or,
                    lhs=lhs, op=op, rhs=rhs
                )
                where_sql += self.space

            build_sql += where_sql[4:]

        if len(self.__group_by) > 0:
            build_sql += " GROUP BY "
            build_sql += ", ".join(self.__group_by)
            having_sql = ""

            for and_or, lhs, op, rhs in self.__having:
                having_sql += " {and_or} {lhs} {op} {rhs}".format(
                    and_or=and_or,
                    lhs=lhs, op=op, rhs=rhs
                )
                having_sql += self.space

            build_sql += having_sql[4:]

        if len(self.__order) > 0:
            build_sql += " ORDER BY "
            orders = ["{field} {asc}".format(field=field, asc=asc) for field, asc in self.__order]

            build_sql += ", ".join(orders)

        return build_sql

    def __build_insert(self):
        build_sql = "INSERT INTO {table} ".format(table=self.__to_table)

        if len(self.__field) > 0:
            build_sql += "("
            build_sql += ", ".join(self.__field)
            build_sql += ")"

        build_sql += self.space
        build_sql += "VALUES"
        build_sql += self.space

        if self.pretty_print:
            build_sql += (", %s" % self.space).join(self.__value)
        else:
            build_sql += ", ".join(self.__value)

        return build_sql

    def __build_delete(self):
        build_sql = "DELETE FROM {table}".format(table=self.__to_table)

        if len(self.__where) > 0:
            build_sql += " WHERE "
            where_sql = ""

            for and_or, lhs, op, rhs in self.__where:
                where_sql += " {and_or} {lhs} {op} {rhs}".format(
                    and_or=and_or,
                    lhs=lhs, op=op, rhs=rhs
                )
                where_sql += self.space

            build_sql += where_sql[4:]

        return build_sql


if __name__ == '__main__':
    select = QueryBuilder(pretty_print=True).select('table_a')

    select.field(('field_a', 'field_b'))
    select.where('field_a', '=', 10)
    select.join('other_table', 'other_table.field_a', '=', 'table_a.field_a')

    print(select.build())
