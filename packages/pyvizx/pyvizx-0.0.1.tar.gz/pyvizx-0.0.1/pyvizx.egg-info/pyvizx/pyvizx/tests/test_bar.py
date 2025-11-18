from pyvizx.charts import bar

def test_bar_chart():
    bar(["A","B","C"], [1,2,3], save=False)
