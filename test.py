import pandas as pd

# 读取JSON数据
json_data = {'name': ['John', 'Mary', 'Peter', '1'], 'age': [25, 30, 35]}
df = pd.DataFrame.from_dict(json_data, orient='index').transpose()

# 将数据存储到Excel表格中
writer = pd.ExcelWriter('data.xlsx', engine='openpyxl')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.book.save('data.xlsx')