import matplotlib.pyplot as plt
import matplotlib.image as image
from math import pi, radians, tan, sin, cos, acos
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


def azimuthal_north(lat, lon):
    # get polar coordinates
    # 512 is the number of pixels from the pole to the equator
    # hacky conversion lmao moment

    radius = 1024/pi
    rho = radius*(pi/2 - radians(lat))
    theta = radians(lon) - pi/2

    # convert to cartesian

    x = rho*cos(theta)
    y = rho*sin(theta)

    # adjust values to the coordinate system of images

    x += 1028
    y = 1028 - y

    data = image.imread("Azimuthal_N.jpg")
    plt.style.use("dark_background")
    fig, ax = plt.subplots()

    plt.plot(x, y, figure=fig, marker="v", color="red")
    plt.xticks(ticks=[0], labels="")
    plt.yticks(ticks=[0], labels="")
    ax.set_xlim([x - 250, x + 250])
    ax.set_ylim([y + 250, y - 250])
    plt.imshow(data, figure=fig)
    fig.set_size_inches(6, 6)
    save_figure(fig=fig, name="azimuthal_north.png")


def azimuthal_south(lat, lon):
    # get polar coordinates
    # 512 is the number of pixels from the pole to the equator
    # hacky conversion lmao moment

    radius = 1024/pi
    rho = radius*(pi/2 + radians(lat))
    theta = radians(lon) + pi/2

    # convert to cartesian

    x = -rho*cos(theta)
    y = rho*sin(theta)

    # adjust values to the coordinate system of images

    x += 1028
    y = 1028 - y

    data = image.imread("Azimuthal_S.jpg")
    plt.style.use("dark_background")
    fig, ax = plt.subplots()


    plt.plot(x, y, figure=fig, marker="v", color="red")
    plt.xticks(ticks=[0], labels="")
    plt.yticks(ticks=[0], labels="")
    ax.set_xlim([x - 250, x + 250])
    ax.set_ylim([y + 250, y - 250])
    plt.imshow(data, figure=fig)
    fig.set_size_inches(6, 6)
    save_figure(fig=fig, name="azimuthal_south.png")


