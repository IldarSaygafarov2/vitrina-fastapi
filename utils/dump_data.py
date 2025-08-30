import re
import json

sql_file = "../backup.sql"
tables = {}

insert_re = re.compile(r"INSERT INTO (\w+) .*?VALUES\s*(.*);", re.IGNORECASE | re.DOTALL)

with open(sql_file, "r", encoding="utf-8") as f:
    sql = f.read()

for match in insert_re.finditer(sql):
    table = match.group(1)
    values = match.group(2).strip()

    rows = []
    for row in values.split("),("):
        row = row.strip("() ")
        rows.append(row.split(","))

    if table not in tables:
        tables[table] = []
    tables[table].extend(rows)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(tables, f, ensure_ascii=False, indent=2)
