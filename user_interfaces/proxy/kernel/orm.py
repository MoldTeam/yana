from typing import Iterable


class _DatabaseEntity:
    table_name = ''
    table_columns = ()
    
    def __setattr__(self, name, value):
        if name == 'table_columns':
            iterable = False
            try:
                iter(value)
                iterable = True
            except TypeError:
                pass
            if not iterable:
                raise TypeError('table columns must have iterable type')
            i = 0
            for column in value:
                if type(column) != str:
                    raise TypeError(f'table columns element {column} with index {i} not a string')
                i += 1
            object.__setattr__(self, name, value)
        elif name == 'table_name':
            if type(value) != str:
                raise TypeError('table name must be a string')
            object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        title = f"--- {self.__class__.__name__} ---"
        cols = ""
        if hasattr(self, 'columns'):
            for column, value in self.columns.items():
                cols += f"\n{column}: {value}"
        return f"{title}{cols}\n"

    def update_attrs(self):
        if hasattr(self, 'columns'):
            for column, value in self.columns.items():
                setattr(self, column, value)


class Source(_DatabaseEntity):
    table_columns = ('id', 'domain', 'description', 'is_api')
    table_name = 'sources'


class NewsTopic(_DatabaseEntity):
    table_columns = (
        'id', 'name', 'parent_news_topic_id', 'description')
    table_name = 'news_topics'


class SourceReference(_DatabaseEntity):
    table_columns = ('id', 'source_domain',
                        'news_topic_id', 'url', 'description')
    table_name = 'sources_references'


class PostgreORM:
    def __init__(self, connection):
        self.__conn = connection
    
    def __set_methods_to_entity(self, entity):
        # Database entity methods
        column = next(iter(entity.columns))
        value = getattr(entity, column)
        if type(value) == str:
            value = f"'{value}'"
        where = f"{column} = {value}"
        def update(table_alias='', set_values={'column_name': 'expression'}, from_item='', returning='', returning_alias=''):
            if returning == '':
                self.update_table(
                    entity, table_alias, set_values, from_item,
                    where, returning, returning_alias
                )
            else:
                return self.update_table(
                    entity, table_alias, set_values, from_item,
                    where, returning, returning_alias
                )
        def delete(table_alias='', using='', returning='', returning_alias=''):
            if returning == '':
                self.delete_from_table(
                    entity, table_alias, using, where,
                    returning, returning_alias
                )
            else:
                return self.delete_from_table(
                    entity, table_alias, using, where,
                    returning, returning_alias
                )
        entity.update = update
        entity.delete = delete

    def execute(self, query: str, auto_commit=True):
        cur = self.__conn.cursor()
        query_for_checking = query.lower()
        # CREATE
        if query_for_checking.startswith('create'):
            cur.execute(query)
            if auto_commit:
                self.__conn.commit()
        # INSERT
        elif query_for_checking.startswith('insert into'):
            cur.execute(query)
            if auto_commit:
                self.__conn.commit()
        # SELECT
        elif query_for_checking.startswith('select'):
            cur.execute(query)
            return cur.fetchall()
        # UPDATE
        elif query_for_checking.startswith('update'):
            if 'returning' not in query_for_checking:
                cur.execute(query)
                if auto_commit:
                    self.__conn.commit()
            else:
                q = cur.execute(query)
                if auto_commit:
                    self.__conn.commit()
                return q.fetchall()
        # DELETE
        elif query_for_checking.startswith('delete'):
            if 'returning' not in query_for_checking:
                cur.execute(query)
                if auto_commit:
                    self.__conn.commit()
            else:
                q = cur.execute(query)
                if auto_commit:
                    self.__conn.commit()
                return q.fetchall()

    def __get_columns_names(self, table_columns: Iterable[str], columns: Iterable[str]):
        if columns is None:
            raise ValueError('columns is required argument')
        elif type(columns) not in (list, tuple):
            raise TypeError('columns argument must be a list or tuple')
        else:
            if len(columns) < 1:
                raise ValueError('must specify at least one column in columns argument')
            def check_column_type(column):
                if type(column) != str:
                    raise TypeError(f'column "{column}" not a string')
            def check_column_existence(table_columns: Iterable[str], column: str):
                if column not in table_columns:
                    raise ValueError(f'this table don`t have column "{column}"')
            cols = []
            for column in columns:
                check_column_type(column)
                column_for_check = column.lower()
                splited_column = column.split(' ')
                if ' as ' in column_for_check:
                    cols.append(splited_column[-1])
                else:
                    check_column_existence(table_columns, column)
                    cols.append(splited_column[0])
            return cols

    def __check_alias(self, alias: str, alias_name: str):
        if alias != '':
            alias = alias.strip()
            if ' ' in alias:
                raise ValueError(f'{alias_name} argument must not contain spaces')

    def __get_entities_with_data(self, entity, columns, data):
        entities = []
        for l in data:
            e = entity()
            cols = {}
            i = 0
            for column in columns:
                cols[column] = l[i]
                i += 1
            e.columns = cols
            e.update_attrs()
            self.__set_methods_to_entity(e)
            entities.append(e)
        return entities

    # ### SELECT ###

    def __check_count(self, count):
        if count != 'all' and type(count) != int:
            raise TypeError("count argument value must be 'all' or integer value")
        elif type(count) == int and count < 1:
            raise ValueError('count argument must be greater than zero')

    def select_from_table(self, entity, columns: Iterable[str], table_alias='', joins=['join expression'], where='', group_by='', having='', order_by='', count='all'):
        # checking arguments
        cols = self.__get_columns_names(entity.table_columns, columns)
        self.__check_count(count)
        self.__check_alias(table_alias, 'table alias')
        # generating query
        query = f"SELECT {', '.join(columns)} FROM {entity.table_name}"
        if table_alias != '':
            query += f" AS {table_alias}"
        if joins != ['join expression']:
            if type(joins) != list:
                raise TypeError('joins argument must be a list')
            else:
                for e in joins:
                    if type(e) != str:
                        raise TypeError(f"value '{e}' in joins list not a string")
                    else:
                        query += f" JOIN {e}"
        if where != '':
            query += f" WHERE {where}"
        if group_by != '':
            element = ''
            for char in group_by:
                if char != ' ':
                    element += char
                else:
                    break
            in_columns = False
            for column in columns:
                if column == element:
                    in_columns = True
            if not in_columns:
                raise ValueError('grouping element must be in columns argument')
            query += f" GROUP BY {group_by}"
        if having != '':
            query += f" HAVING {having}"
        if order_by != '':
            query += f" ORDER BY {order_by}"
        if count != 'all':
            query += f" LIMIT {count}"
        # execute and return
        data = self.execute(query)
        return self.__get_entities_with_data(entity, cols, data)

    def get_sources(self, columns=['id', 'domain', 'description', 'is_api'], table_alias='', joins=['join expression'], where='', group_by='', having='', order_by='', count='all'):
        return self.select_from_table(
            Source, columns, table_alias, joins, where, group_by,
            having, order_by, count
        )

    def get_news_topics(self, columns=['id', 'name', 'parent_news_topic_id', 'description'], table_alias='', joins=['join expression'], where='', group_by='', having='', order_by='', count='all'):
        return self.select_from_table(
            NewsTopic, columns, table_alias, joins, where,
            group_by, having, order_by, count
        )

    def get_sources_references(self, columns=['id', 'source_domain', 'news_topic_id', 'url', 'description'], table_alias='', joins=['join expression'], where='', group_by='', having='', order_by='', count='all'):
        return self.select_from_table(
            SourceReference, columns, table_alias, joins, where,
            group_by, having, order_by, count
        )

    # ### INSERT ###

    def insert_into_table(self, entity, columns: Iterable[str], table_alias='', overriding_value='', default_values=False, values=list[list], on_conflict='', returning='', returning_alias=''):
        # checking and prepare arguments
        self.__check_alias(table_alias, 'table alias')
        table_alias = table_alias.strip()
        if overriding_value != '':
            overriding_value = overriding_value.strip()
            if overriding_value.lower() not in ('system', 'user'):
                raise ValueError("overriding value must be 'system' or 'user'")
        if type(default_values) != bool:
            raise TypeError('default values argument must have boolean value')
        if type(values) not in (list, tuple):
            raise TypeError('values must be a list or tuple')
        if default_values and len(values) > 0:
            raise ValueError('cannot specify values and turn on default values at the same time')
        if not default_values and len(values) == 0:
            raise ValueError('necessary to turn off default values or specify values')
        self.__check_alias(returning_alias, 'returning alias')
        returning_alias = returning_alias.strip()
        # generating, execute and return query
        query = f"INSERT INTO {entity.table_name} ({', '.join(columns)})"
        if default_values:
            query += " DEFAULT VALUES"
            self.execute(query)
        else:
            if overriding_value != '':
                query += f" OVERRIDING {overriding_value.upper()} VALUE"
            query += " VALUES "
            for l in values:
                query += "("
                for value in l:
                    if type(value) == str:
                        query += f"'{value}', "
                    elif type(value) in (int, float):
                        query += f"{value}, "
                    elif type(value) == bool:
                        if value:
                            query += "true, "
                        else:
                            query += "false, "
                    elif value is None:
                        query += "null, "
                query = query.rstrip(', ')
                query += "), "
            query = query.rstrip(', ')
            if on_conflict != '':
                query += f" ON CONFLICT {on_conflict}"
            if returning != '':
                cols = self.__get_columns_names(entity.table_columns, columns)
                query += f" RETURNING {returning}"
                if returning_alias != '':
                    query += f" AS {returning_alias}"
                data = self.execute(query)
                return self.__get_entities_with_data(entity, cols, data)
            else:
                self.execute(query)

    def insert_into_sources(self, columns=['domain'], table_alias='', overriding_value='', values=[['example.com']], returning='', returning_alias=''):
        if returning == '':
            self.insert_into_table(
                Source, columns,
                table_alias, overriding_value,
                returning=returning, returning_alias=returning_alias,
                values=values
            )
        else:
            return self.insert_into_table(
                Source, columns,
                table_alias, overriding_value,
                returning=returning, returning_alias=returning_alias,
                values=values
            )
    
    def insert_into_news_topics(self, columns=['name'], table_alias='', overriding_value='', values=[['it']], returning='', returning_alias=''):
        if returning == '':
            self.insert_into_table(
                NewsTopic, columns,
                table_alias, overriding_value,
                returning=returning, returning_alias=returning_alias,
                values=values
            )
        else:
            return self.insert_into_table(
                NewsTopic, columns,
                table_alias, overriding_value,
                returning=returning, returning_alias=returning_alias,
                values=values
            )

    def insert_into_sources_references(self, columns=['source_domain', 'news_topic_id', 'url'], table_alias='', overriding_value='', values=[['https://example.com/world-news']], returning='', returning_alias=''):
        if returning == '':
            self.insert_into_table(
                SourceReference, columns,
                table_alias, overriding_value,
                returning=returning, returning_alias=returning_alias,
                values=values
            )
        else:
            return self.insert_into_table(
                SourceReference, columns,
                table_alias, overriding_value,
                returning=returning, returning_alias=returning_alias,
                values=values
            )

    # ### UPDATE ###

    def __check_dict_of_str(self, dictionary: dict, dict_name: str, example: dict[str: str], required=True):
        if type(dictionary) != dict:
            raise TypeError(f'{dict_name} argument must be a dictionary')
        if required:
            if dictionary == example:
                raise ValueError(f'must specify not example values in {dict_name} dictionary')
        for key, value in dictionary.items():
            dn = f'{dict_name} dictionary'
            if type(key) != str and type(value) != str:
                raise TypeError(
                    f"{dn} pair {key}: {value} type is wrong")
            elif type(key) != str:
                raise TypeError(f'{dn} key {key} type is wrong')
            elif type(value) != str:
                raise TypeError(f'{dn} value {value} under key {key} type is wrong')
        

    def update_table(self, entity, table_alias='', set_values={'column_name': 'expression'}, from_item='', where='', returning='', returning_alias=''):
        # checking and prepare arguments
        self.__check_alias(table_alias, 'table alias')
        self.__check_alias(returning_alias, 'returning alias')
        self.__check_dict_of_str(set_values, 'columns values', {'column_name': 'expression'})
        if from_item != '':
            from_item = from_item.strip()
            if ' ' in from_item:
                raise ValueError('from item argument must not contain spaces')
        # generating query
        query = f"UPDATE {entity.table_name}"
        if table_alias != '':
            query += f" AS {table_alias}"
        query += " SET "
        for column_name, expression in set_values.items():
            if not ' ' in expression.strip() and not expression.replace('.', '').isnumeric()\
                and expression != 'null':
                expression = f"'{expression}'"
            query += f"{column_name} = {expression}, "
        query = query.rstrip(', ')
        if from_item != '':
            query += f" FROM {from_item}"
        if where != '':
            query += f" WHERE {where}"
        if returning != '':
            query += f" RETURNING {returning}"
            if returning_alias != '':
                query += f" AS {returning_alias}"
            return self.execute(query)
        else:
            self.execute(query)

    def update_sources(self, table_alias='', set_values={'column_name': 'expression'}, from_item='', where='', returning='', returning_alias=''):
        if returning == '':
            self.update_table(
                Source, table_alias, set_values,
                from_item, where, returning, returning_alias
            )
        else:
            return self.update_table(
                Source, table_alias, set_values,
                from_item, where, returning, returning_alias
            )
    
    def update_news_topics(self, table_alias='', set_values={'column_name': 'expression'}, from_item='', where='', returning='', returning_alias=''):
        if returning == '':
            self.update_table(
                NewsTopic, table_alias, set_values,
                from_item, where, returning, returning_alias
            )
        else:
            return self.update_table(
                NewsTopic, table_alias, set_values,
                from_item, where, returning, returning_alias
            )

    def update_sources_references(self, table_alias='', set_values={'column_name': 'expression'}, from_item='', where='', returning='', returning_alias=''):
        if returning == '':
            self.update_table(
                SourceReference, table_alias, set_values,
                from_item, where, returning, returning_alias
            )
        else:
            return self.update_table(
                SourceReference, table_alias, set_values,
                from_item, where, returning, returning_alias
            )
    
    # ### DELETE ###

    def delete_from_table(self, entity, table_alias='', using='', where='', returning='', returning_alias=''):
        # checking arguments
        table_alias = table_alias.strip()
        returning_alias = returning_alias.strip()
        self.__check_alias(table_alias, 'table alias')
        self.__check_alias(returning_alias, 'returning alias')
        # generating query and return entities
        query = f"DELETE FROM {entity.table_name}"
        if table_alias != '':
            query += f" AS {table_alias}"
        if using != '':
            query += f" USING {using}"
        if where != '':
            query += f" WHERE {where}"
        if returning != '':
            query += f" RETURNING {returning}"
            if returning_alias != '':
                query += f" AS {returning_alias}"
            return self.execute(query)
        else:
            self.execute(query)
    
    def delete_from_sources(self, table_alias='', using='', where='', returning='', returning_alias=''):
        if returning == '':
            self.delete_from_table(
                Source, table_alias, using, where,
                returning, returning_alias
            )
        else:
            return self.delete_from_table(
                Source, table_alias, using, where,
                returning, returning_alias
            )

    def delete_from_news_topics(self, table_alias='', using='', where='', returning='', returning_alias=''):
        if returning == '':
            self.delete_from_table(
                NewsTopic, table_alias, using, where,
                returning, returning_alias
            )
        else:
            return self.delete_from_table(
                NewsTopic, table_alias, using, where,
                returning, returning_alias
            )

    def delete_from_sources_references(self, table_alias='', using='', where='', returning='', returning_alias=''):
        if returning == '':
            self.delete_from_table(
                SourceReference, table_alias, using, where,
                returning, returning_alias
            )
        else:
            return self.delete_from_table(
                SourceReference, table_alias, using, where,
                returning, returning_alias
            )
