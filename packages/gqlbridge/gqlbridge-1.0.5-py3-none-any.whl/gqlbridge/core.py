from graphql import parse
from graphql.language.printer import print_ast
import re
import pandas as pd
import hashlib
from sqlalchemy import create_engine, text
import json
import os
import yaml

def get_table_name(schema_data, table_name):
    if schema_data == {}:
        return ''
    for table, col in schema_data.items():
        if col.get('table_name', '') == table_name and table_name != '':
            return table
    return ''


def fetchAlias(schema='public', table_name=None, col_name=None, attribute=None):
    if schema == '' or schema is None:
        schema = 'public'
    if attribute == 'table':
        return get_table_name(alias_data['tables'].get(schema, {}), table_name)
        return ''# if alias_data['tables'].get(schema, {}).get(table_name, {}).get('table_name', {}) == {} else alias_data['tables'].get(schema, {}).get(table_name, {}).get('table_name', {})
    if attribute == 'schema':
        return '' if alias_data['tables'].get(schema, {}).get(table_name, {}).get('schema_name', {}) == {} else alias_data['tables'].get(schema, {}).get(table_name, {}).get('schema_name', {})
    if table_name is not None:
        table_data = {} if alias_data['tables'].get(schema, {}).get(table_name, {}) == {} else alias_data['tables'].get(schema, {}).get(table_name, {})
    else:
        return ''
    for old_col, new_col in table_data.items():
        if col_name is not None and new_col == col_name:
            return old_col
    return ''


def form_list_filter_value(args):
    arg_list = [eachValue['value'] for eachValue in args['value']['values']]
    arg_string = '('
    for eachValue in args['value']['values']:
        if eachValue['kind'] in ['int_value', 'float_value']:
            arg_string += f'{eachValue["value"]},'
        if eachValue['kind'] == 'string_value':
            arg_string += "'" + eachValue["value"] + "',"
    arg_string  = arg_string[:-1]
    arg_string += ')'
    return arg_string

def get_symbol(symbol_string):
    if symbol_string == 'le':
        return '<='
    elif symbol_string == 'ge':
        return '>='
    elif symbol_string == 'lt':
        return '<'
    elif symbol_string == 'gt':
        return '>'
    elif symbol_string == 'eq':
        return '='
    elif symbol_string == 'ne':
        return '!='

def get_args(selection, tableName, schemaNameOld):
    filterString = ' where '
    paginationString, page_length = '', 0
    for args in selection['arguments']:
        if args['name']['value'] == 'first':
            page_length = int(args["value"]["value"])
            if int(args["value"]["value"]) < 0:
                raise Exception('Invalid page number')
    for args in selection['arguments']:
        paginationFlag = 0
        if args['name']['value'] == 'schema':
            continue
        if args['value']['kind'] in ['object_value'] and args['name']['value'] not in ['left', 'right', 'inner', 'full', 'outer', 'full outer', 'cross']:
            symbol = get_symbol(args['value']['fields'][0]['name']['value'])
            colName = fetchAlias(schemaNameOld, table_name=tableName, col_name=args["name"]["value"]).lower()
            colName = args["name"]["value"] if colName == '' else colName
            if args["value"]["fields"][0]["value"]["kind"] in ['string_value']:
                if re.match(r'.*\d{4}[\\-]\d{2}[\\-]\d{2}.*', args["value"]["fields"][0]["value"]["value"]) or re.match(r'.*\d{2}[\\-]\d{2}[\\-]\d{4}.*', args["value"]["fields"][0]["value"]["value"]):
                    filterString += f'{tableName}.{colName}::TIMESTAMP {symbol} \'{args["value"]["fields"][0]["value"]["value"]}\'::TIMESTAMP'
                else:
                    filterString += f'{tableName}.{colName} {symbol} \'{args["value"]["fields"][0]["value"]["value"]}\''
            else:
                filterString += f'{tableName}.{colName} {symbol} {args["value"]["fields"][0]["value"]["value"]}'

        elif args['value']['kind'] in ['object_value']:
            continue
        elif args['name']['value'] == 'first':
            paginationString += f' LIMIT {str(args["value"]["value"])} '
            paginationFlag = 1
        elif args['name']['value'] == 'after':
            paginationString += f' OFFSET {str(0 if args["value"]["value"] in ["0","1"] else (int(args["value"]["value"])-1) * page_length)} '
            paginationFlag = 1
        elif args['name']['value'] == 'orderBy':
            colName = fetchAlias(schemaNameOld, table_name=tableName, col_name=args["value"]["value"]).lower()
            colName = args["value"]["value"] if colName == '' else colName
            paginationString = f' ORDER BY {str(colName)} ' + paginationString
            paginationFlag = 1
        elif args['value']['kind'] in ['string_value']:
            colName = fetchAlias(schemaNameOld, table_name=tableName, col_name=args["name"]["value"]).lower()
            colName = args["name"]["value"] if colName == '' else colName
            if re.match(r'.*\d{4}[\\-]\d{2}[\\-]\d{2}.*', args["value"]["value"]) or re.match(r'.*\d{2}[\\-]\d{2}[\\-]\d{4}.*', args["value"]["value"]):
                filterString += f'{tableName}.{colName}::TIMESTAMP = \'{args["value"]["value"]}\'::TIMESTAMP'
            else:
                filterString += f'{tableName}.{colName} = \'{args["value"]["value"]}\''
        elif args['value']['kind'] == 'list_value':
            filterListVal = form_list_filter_value(args)
            colName = fetchAlias(schemaNameOld, table_name=tableName, col_name=args["name"]["value"]).lower()
            colName = args["name"]["value"] if colName == '' else colName
            filterString += f'{tableName}.{colName} in {filterListVal}'
        else:
            colName = fetchAlias(schemaNameOld, table_name=tableName, col_name=args["name"]["value"]).lower()
            colName = args["name"]["value"] if colName == '' else colName
            filterString += f'{tableName}.{colName} = {args["value"]["value"]}'
        if filterString != ' where ' and paginationFlag == 0:
            filterString += ' and  '
    return filterString[:-6] + paginationString

def extract_columns(node, path=None, results=None):
    if path is None:
        path = []
    if results is None:
        results = []

    if not isinstance(node, dict):
        return results

    if "name" in node and isinstance(node["name"], dict):
        name_val = node["name"].get("value")
        if name_val:
            path = path + [name_val]

    selection_set = node.get("selection_set", {})
    if isinstance(selection_set, dict):
        selections = selection_set.get("selections", [])
        if isinstance(selections, list):
            for item in selections:
                extract_columns(item, path, results)
            return results

    if path:
        results.append("/".join(path))
    return results


def prepare_json_col(json_schema_list, col_name, tableName):
    alias_counter = {"count": 0}  # simple counter for unique elem aliases

    def next_alias():
        alias_counter["count"] += 1
        return f"elem{alias_counter['count']}"

    def build_grouped(paths, base_ref):

        grouped = {}
        for path in paths:
            head, *tail = path.split('/')
            grouped.setdefault(head, []).append(tail)

        fields = []
        for head, tails in grouped.items():
            if head == "list_items":
                # Handle array expansion → give unique alias
                alias = next_alias()
                inner = build_grouped(
                    ["/".join(t) for t in tails if t],
                    f"{alias}.value"
                )
                return f"""(
                    SELECT jsonb_agg({inner})
                    FROM jsonb_array_elements({base_ref}) {alias}
                )"""
            else:
                # Object or leaf
                if any(t for t in tails):  # deeper fields exist
                    inner = build_grouped(
                        ["/".join(t) for t in tails if t],
                        f"{base_ref}->'{head}'"
                    )
                    fields.append(f"'{head}', {inner}")
                else:  # leaf field
                    fields.append(f"'{head}', {base_ref}->>'{head}'")

        return f"jsonb_build_object({', '.join(fields)})"

    # Root expression build
    json_expr = build_grouped(json_schema_list, f"{tableName}.{col_name}::jsonb")
    return f"\'{col_name}\', {json_expr}, "


def fetchSchema(arguments):
    for arg in arguments:
        arg_name = arg['name']['value'].lower()
        if arg_name == 'schema':
            return arg['value']['value']
    return ''


def prepare_selection_string(selection, table_or_col_flag, tableName=None, schema=None): # 0 - col, 1 - table
    if selection['selection_set'] is not None and table_or_col_flag == 1:
        tableNameOld = f"{selection['name']['value']}"
        schemaNameOld = fetchSchema(selection['arguments'])
        schemaNameOld = 'public' if schemaNameOld == '' else schemaNameOld
        schemaName = fetchAlias(schemaNameOld, table_name=tableNameOld, col_name=tableNameOld, attribute='schema').lower()
        schemaName = schemaNameOld if schemaName == '' else schemaName
        tableName = fetchAlias(schemaNameOld, table_name=tableNameOld, col_name=tableNameOld, attribute='table').lower()
        tableName = tableNameOld if tableName == '' else tableName
        filterString = get_args(selection, tableName,schemaNameOld)

        if schemaName == '':
            return f' {tableName}{filterString}', tableName
        return f' {schemaName}.{tableName}{filterString}', tableName
    elif selection['selection_set'] is not None and selection['arguments'] == [] and table_or_col_flag == 0:
        json_schema_list = []
        for eachSelection in selection['selection_set']['selections']:
            json_schema_list += extract_columns(eachSelection)
        schemaNameOld = fetchSchema(schema['arguments'])
        oldTableName = fetchAlias(schemaNameOld, table_name=tableName, col_name=tableName, attribute='table').lower()
        tableName = tableName if oldTableName == '' else oldTableName

        json_col = prepare_json_col(json_schema_list, selection['name']['value'], tableName)

        return f'{json_col}'
    elif selection['selection_set'] is None:
        schemaNameOld = fetchSchema(schema['arguments'])
        oldTableName = fetchAlias(schemaNameOld, table_name=tableName, col_name=tableName,attribute='table').lower()
        tableName = tableName if oldTableName == '' else oldTableName
        colName = fetchAlias(schemaNameOld, table_name=tableName, col_name=selection["name"]["value"]).lower()
        colName = selection["name"]["value"] if colName == '' else colName
        sqlQuery = f'\'{colName}\', {tableName}.{colName}, '
        return sqlQuery


def get_join_condition_from_graphql(arguments, parent_table, join_table, parent_schema, join_schema):
    join_type = "INNER JOIN"  # default
    join_condition, parent_col_list = [], []

    for arg in arguments:
        arg_name = arg['name']['value'].lower()

        if arg_name in ("left", "right", "full", "inner", "cross"):
            # Map GraphQL key -> SQL join type
            join_type = {
                "left": "LEFT JOIN",
                "right": "RIGHT JOIN",
                "full": "FULL JOIN",
                "inner": "INNER JOIN",
                "cross": "CROSS JOIN"
            }[arg_name]

            if arg['value']['kind'] == 'object_value':
                for field in arg['value']['fields']:
                    val = field['value']['value']
                    symbol = get_symbol(val[:2])
                    parent_col = fetchAlias(join_schema.lower(), table_name=join_table.lower(),
                               col_name=val[3:].lower()).lower()
                    if parent_col == '':
                        parent_col = val[3:]
                    parent_col_list.append(parent_col)
                    parent_table_col = fetchAlias(parent_schema.lower(), table_name=parent_table.lower(),
                                            col_name=field['name']['value'].lower()).lower()
                    if parent_table_col == '':
                        parent_table_col = field['name']['value'].lower()
                    join_condition.append(
                        f"{parent_table}.{parent_table_col} {symbol} {join_table}.{parent_col}"
                    )

            else:
                raise Exception('Incorrect join condition')

            break  # stop after first valid join

    return join_type, ' AND '.join(join_condition), ', '.join(set(parent_col_list))


def traverse_selections(selectionSet, join_sql_ctc_list, parent_table=None, table_flag=0, parentSchemaNameOld=None):
    sqlQuery = "SELECT " if table_flag == 1 else "SELECT jsonb_build_object("
    join_query_list = []
    if parent_table is None:
        parentSchemaNameOld = fetchSchema(selectionSet['arguments'])
        parentSchemaNameReturned = fetchAlias(parentSchemaNameOld, table_name=selectionSet['name']['value'], col_name=selectionSet['name']['value'],
                   attribute='schema').lower()
        parentSchemaName = parentSchemaNameOld if parentSchemaNameReturned == '' else parentSchemaNameReturned

    if selectionSet['selection_set'] is None:
        raise Exception('Provide columns of the table that need to be fetched')

    for eachSelection in selectionSet['selection_set']['selections']:
        args = eachSelection.get('arguments', [])
        if args != []:
            schemaNameOld = fetchSchema(eachSelection['arguments'])
            schemaNameOld = 'public' if schemaNameOld == '' else schemaNameOld
            parentSchemaName = 'public' if parentSchemaName == '' else parentSchemaName
            join_table = fetchAlias(schemaNameOld, table_name=eachSelection['name']['value'], col_name=eachSelection['name']['value'], attribute='table').lower()
            join_table = eachSelection['name']['value'] if join_table == '' else join_table
            parent_table = fetchAlias(parentSchemaNameOld, table_name=selectionSet['name']['value'], col_name=selectionSet['name']['value'], attribute='table').lower()
            parent_table = selectionSet['name']['value'] if parent_table == '' else parent_table
            join_query, table_sql = traverse_selections(eachSelection, join_sql_ctc_list, parent_table=parent_table, table_flag=1, parentSchemaNameOld=parentSchemaNameOld)

            join_type, join_condition, join_col = get_join_condition_from_graphql(
                eachSelection['arguments'],
                parent_table=parent_table,
                join_table=join_table,
                parent_schema=parentSchemaNameOld,
                join_schema=schemaNameOld
            )

            schemaNameReturned = fetchAlias(schemaNameOld, table_name=join_table,
                                                  col_name=join_table,
                                                  attribute='schema').lower()
            schemaName = schemaNameOld if schemaNameReturned == '' else schemaNameReturned

            if schemaName:
                schemaAndTable = f'{schemaName}.{table_sql.lstrip()}'
            else:
                schemaAndTable = table_sql


            join_sql = f"""{join_table}_gqlbridge AS (
                SELECT {join_col} ,jsonb_agg(
                    jsonb_build_object({join_query[6:-2]})
                )
             FROM (SELECT * FROM {table_sql}) AS {join_table}
             GROUP BY {join_col}
            ) \n"""
            join_sql_ctc_list.append(join_sql)
            sqlQuery += f'\'{join_table}\', {join_table}_gqlbridge.jsonb_agg, \n'

            join_query_list.append(f"{join_type} {join_table}_gqlbridge ON {join_condition.replace(join_table+'.',join_table+'_gqlbridge.')}")
            continue

        col_sql = prepare_selection_string(eachSelection, 0, selectionSet['name']['value'], schema=selectionSet)
        sqlQuery += col_sql

    table_sql, tableName = prepare_selection_string(selectionSet, 1, selectionSet['name']['value'])
    if table_flag == 1:
        return sqlQuery, table_sql
    # schemaNameOld = fetchSchema(selection['arguments'])
    # schemaName = fetchAlias(schemaNameOld, table_name=tableNameOld, col_name=tableNameOld, attribute='schema').lower()
    # schemaName = schemaNameOld if schemaName == '' else schemaName
    # if schemaName != '':
    #     schemaAndTable = f'{schemaName}.{table_sql.lstrip()}'
    # else:
    schemaAndTable = table_sql
    sqlQuery = f"{sqlQuery[:-2]}) FROM (SELECT * FROM {schemaAndTable}) AS {tableName}"

    if table_flag == 0:
        if join_query_list:
            schemaName = fetchSchema(selectionSet['arguments'])
            if schemaName != '':
                schemaAndTable = f'{schemaName}.{table_sql.lstrip()}'
            else:
                schemaAndTable = table_sql
            sqlQuery = f'WITH {tableName} AS (SELECT * FROM {table_sql}),'+",\n  ".join(join_sql_ctc_list) + '\n' + sqlQuery
    if join_query_list:
        sqlQuery += " " + " ".join(join_query_list)

    return sqlQuery




def run_query(query: str) -> pd.DataFrame:
    conn_params = {
        "host": os.environ['DB_HOST'],
        "port": os.environ['DB_PORT'],
        "dbname": os.environ['DB_NAME'],
        "user": os.environ['DB_USER'],
        "password": os.environ['DB_PASSWORD']
    }
    conn_url = f'postgresql+psycopg2://{conn_params["user"]}:{conn_params["password"]}@{conn_params["host"]}:{conn_params["port"]}/{conn_params["dbname"]}'

    engine = create_engine(conn_url)
    with engine.connect() as conn:
        df: pd.DataFrame = pd.read_sql(text(query), conn)
    return df

def main(queryStr, alias_file_path=None):
    global join_query_list, alias_map, alias_data

    # Parse the query into an AST (Abstract Syntax Tree)
    try:
        if alias_file_path:
            with open(alias_file_path, "r") as alias_file_obj:
                alias_data = yaml.safe_load(alias_file_obj)
        parsedAst = parse(queryStr)

        # Print or inspect the AST

        graphqlDict = parsedAst.to_dict()
    except Exception as e:
        return {'Error': "Inncorrect Graphql query" + str(e)}

    definations = graphqlDict['definitions']
    final_dict = {}
    queries_count = 1

    for defination in definations:
        selectionSet = defination['selection_set']

        for selection in selectionSet['selections']:
            try:
                join_sql_ctc_list = []

                sqlQuery = traverse_selections(selection, join_sql_ctc_list)

                df = run_query(sqlQuery)

                df.drop_duplicates(inplace=True)
                final_dict[f'Query{queries_count}'] = df['jsonb_build_object'].to_list()
            except Exception as e:
                final_dict[f'Query{queries_count}'] = [{"error": f"{e.__dict__}"}]
            queries_count += 1
    return json.dumps(final_dict)

if __name__:
    # alias_map = {}
    # join_query_list = []
    alias_data = {'tables': {}}
    with open('graphql_query.txt', 'r') as file:
        queryStr = file.read()
    resultant_dict = main(queryStr,alias_file_path=None)
    # print(resultant_dict)