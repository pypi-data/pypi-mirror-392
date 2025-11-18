import matplotlib.pyplot as plt
from .themes import get_theme

def bar(labels, values, title="Bar Chart", theme="default", save=False):
    th = get_theme(theme)
    plt.figure()
    plt.bar(labels, values, color=th["color"])
    plt.title(title, fontsize=th["title_size"])
    plt.ylabel("Value", fontsize=th["label_size"])
    plt.xlabel("Category", fontsize=th["label_size"])
    if save:
        plt.savefig(f"{title}.png")
    plt.show()


def line(labels, values, title="Line Chart", theme="default", save=False):
    th = get_theme(theme)
    plt.figure()
    plt.plot(labels, values, marker="o", linewidth=2)
    plt.title(title, fontsize=th["title_size"])
    if save:
        plt.savefig(f"{title}.png")
    plt.show()


def pie(labels, values, title="Pie Chart", theme="default", save=False):
    th = get_theme(theme)
    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title(title, fontsize=th["title_size"])
    if save:
        plt.savefig(f"{title}.png")
    plt.show()


def scatter(x, y, title="Scatter Plot", theme="default", save=False):
    th = get_theme(theme)
    plt.figure()
    plt.scatter(x, y, color=th["color"])
    plt.title(title, fontsize=th["title_size"])
    if save:
        plt.savefig(f"{title}.png")
    plt.show()


def histogram(values, bins=5, title="Histogram", theme="default", save=False):
    th = get_theme(theme)
    plt.figure()
    plt.hist(values, bins=bins, color=th["color"])
    plt.title(title, fontsize=th["title_size"])
    if save:
        plt.savefig(f"{title}.png")
    plt.show()
