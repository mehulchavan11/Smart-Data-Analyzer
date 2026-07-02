import matplotlib.pyplot as plt

def plot_chart(df, chart_type, x_col, y_col):
    plt.figure()

    if chart_type == "bar":
        plt.bar(df[x_col], df[y_col])

    elif chart_type == "line":
        plt.plot(df[x_col], df[y_col], marker='o')

    elif chart_type == "pie":
        plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%')

    plt.title(f"{chart_type.capitalize()} Chart")
    plt.xlabel(x_col)
    plt.ylabel(y_col)

    plt.show()