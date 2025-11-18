import pandas as pd
from .charts import bar

def excel_to_chart(path, col_x, col_y, title="Excel Chart", theme="default", save=False):
    df = pd.read_excel(path)
    x = df[col_x].tolist()
    y = df[col_y].tolist()
    bar(x, y, title=title, theme=theme, save=save)
