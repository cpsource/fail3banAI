import os
import sys

from enum import Enum
from typing import Union

from pydantic import BaseModel

import openai
from openai import OpenAI

from dotenv import load_dotenv

home = os.getenv('HOME')
project_root = os.getenv('FAIL3BAN_PROJECT_ROOT')
dotenv_file = f"{home}/.env"
load_dotenv(dotenv_file)
openai.api_key = os.getenv('OPENAI_API_KEY')

class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"


class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"


class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="


class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class DynamicValue(BaseModel):
    column_name: str


class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]


class Query(BaseModel):
    table_name: Table
    columns: list[Column]
    conditions: list[Condition]
    order_by: OrderBy


client = OpenAI()

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
        },
        {
            "role": "user",
            "content": "look up all my orders in may of last year that were fulfilled but not delivered on time",
        },
    ],
    tools=[
        openai.pydantic_function_tool(Query),
    ],
)

print(completion.choices[0].message.tool_calls[0].function.parsed_arguments)

res = "table_name=<Table.orders: 'orders'> columns=[<Column.id: 'id'>, <Column.status: 'status'>, <Column.expected_delivery_date: 'expected_delivery_date'>, <Column.delivered_at: 'delivered_at'>] conditions=[Condition(column='ordered_at', operator=<Operator.ge: '>='>, value='2023-05-01'), Condition(column='ordered_at', operator=<Operator.lt: '<'>, value='2023-06-01'), Condition(column='status', operator=<Operator.eq: '='>, value='fulfilled'), Condition(column='delivered_at', operator=<Operator.gt: '>'>, value=DynamicValue(column_name='expected_delivery_date'))] order_by=<OrderBy.asc: 'asc'>"

def query_to_sql(query: Query) -> str:
    # Convert table name and columns
    table = query.table_name.value
    columns = ", ".join([col.value for col in query.columns])
    
    # Convert conditions to WHERE clause
    conditions = " AND ".join([
        f"{cond.column} {cond.operator.value} '{cond.value}'"
        if not isinstance(cond.value, DynamicValue) else
        f"{cond.column} {cond.operator.value} {cond.value.column_name}"
        for cond in query.conditions
    ])
    
    # Order by clause
    order_by = f"ORDER BY {columns.split(',')[0]} {query.order_by.value}"
    
    # Final SQL query
    sql_query = f"SELECT {columns} FROM {table} WHERE {conditions} {order_by};"
    return sql_query
