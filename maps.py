import matplotlib.pyplot as plt
import matplotlib.image as image
from math import pi, radians, tan
from utils import save_figure


def cylindrical(lat, lon):
    """
    Plots a point on a mercator (cylindrical) projection of the map
    """
    data = image.imread("mercator.jpg")
    plt.style.use("dark_background")
    fig, ax = plt.subplots()
    x = (2056 / (2 * pi)) * radians(lon) + 1029
    y = 1028 - (2056 / (2 * pi)) * tan(radians(lat))
    plt.plot(x, y, figure=fig, marker="v", color="red")
    plt.xticks(ticks=[0], labels="")
    plt.yticks(ticks=[0], labels="")
    ax.set_xlim([x - 250, x + 250])
    ax.set_ylim([y + 250, y - 250])
    plt.imshow(data, figure=fig)
    fig.set_size_inches(6, 6)
    save_figure(fig=fig, name="mercator_plot.png")


