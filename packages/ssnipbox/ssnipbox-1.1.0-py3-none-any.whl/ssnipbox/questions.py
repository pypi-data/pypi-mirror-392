# questions.py
# Produces runnable code strings for Q1..Q13.
# Each function returns a triple-quoted string containing a self-contained script.

def q1():
    return '''\
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

np.random.seed(0)

cluster1 = np.random.normal(loc=[5, 5, 5], scale=1.0, size=(100, 3))
cluster2 = np.random.normal(loc=[0, 0, 0], scale=1.0, size=(100, 3))
cluster3 = np.random.normal(loc=[-5, -5, -5], scale=1.0, size=(100, 3))

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(cluster1[:, 0], cluster1[:, 1], cluster1[:, 2],
           color='red', marker='o', s=50, edgecolor='black', alpha=0.8, label='Cluster 1')

ax.scatter(cluster2[:, 0], cluster2[:, 1], cluster2[:, 2],
           color='green', marker='^', s=50, edgecolor='black', alpha=0.8, label='Cluster 2')

ax.scatter(cluster3[:, 0], cluster3[:, 1], cluster3[:, 2],
           color='blue', marker='s', s=50, edgecolor='black', alpha=0.8, label='Cluster 3')

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Scatter Plot of Random Clusters")
ax.legend()

plt.tight_layout()
plt.show()
'''

def q2():
    return '''\
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(0)

mean = [170, 65]
std_h = 10
std_w = 12
rho = 0.6
cov = [[std_h**2, rho * std_h * std_w],
       [rho * std_h * std_w, std_w**2]]

data = np.random.multivariate_normal(mean, cov, size=1000)
height = data[:, 0]
weight = data[:, 1]

sns.set(style="white")
g = sns.jointplot(x=height, y=weight, kind="kde", fill=True, cmap="mako")

g.set_axis_labels("Height (cm)", "Weight (kg)")
plt.suptitle("Joint Distribution of Height and Weight", y=1.02)

plt.tight_layout()
plt.show()
'''

def q3():
    return '''\
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

sns.set_style("whitegrid")

x = np.arange(1, 10.01, 0.01)
pdf = norm.pdf(x, loc=5.3, scale=1)

plt.plot(x, pdf, color='black')
plt.xlabel("Heights")
plt.ylabel("Probability Density")
plt.title("Normal Distribution PDF")

plt.tight_layout()
plt.show()
'''

def q4():
    return '''\
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(0)

mean = [0, 0]
cov = [[3, 1],
       [1, 2]]

data = np.random.multivariate_normal(mean, cov, size=2000)
x = data[:, 0]
y = data[:, 1]

plt.figure(figsize=(8, 6))

sns.kdeplot(x=x, y=y, fill=True, cmap="viridis", thresh=0, levels=100)
sns.kdeplot(x=x, y=y, color="k", linewidth=1, levels=10)

plt.grid(True)
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Bivariate Gaussian Density and Contour Plot")

plt.tight_layout()
plt.show()
'''

def q5():
    return '''\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

x = pd.Series([1, 2, 3, 4, 5, 6, 7])
y = pd.Series([1, 2, 3, 4, 3, 5, 4])

corr = x.corr(y)
print("Pearson Correlation:", corr)

plt.figure(figsize=(8, 6))
plt.scatter(x, y, label="Data Points")

m, b = np.polyfit(x, y, 1)
plt.plot(x, m * x + b, color="red", label="Best-fit Line")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Correlation and Scatter Plot")
plt.legend()

plt.tight_layout()
plt.show()
'''

def q6():
    return '''\
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)
n = 5000
theta = np.random.uniform(0, 2 * np.pi, n)
r = np.random.normal(loc=5, scale=0.5, size=n)

x = r * np.cos(theta)
y = r * np.sin(theta)

plt.figure(figsize=(8, 6))
hb = plt.hexbin(x, y, gridsize=50, cmap='Blues', bins='log')
cbar = plt.colorbar(hb)
cbar.set_label("log10(N)")

hist, xedges, yedges = np.histogram2d(x, y, bins=200, density=True)
xcenters = (xedges[:-1] + xedges[1:]) / 2
ycenters = (yedges[:-1] + yedges[1:]) / 2
X, Y = np.meshgrid(xcenters, ycenters)

plt.contour(X, Y, hist.T, levels=6, colors='k', linewidths=1)

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Hexbin Density Plot with Contours of Noisy Circular Data")
plt.axis('equal')
plt.tight_layout()
plt.show()
'''

def q7():
    return '''\
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

marks = np.random.normal(loc=70, scale=10, size=1000)

plt.figure(figsize=(8, 6))
plt.hist(marks, bins=10, color='skyblue', edgecolor='black')

plt.xlabel("Marks")
plt.ylabel("Number of Students")
plt.title("Distribution of Student Exam Marks")

plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
'''

def q8():
    return '''\
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# Great circle between New York and London
ny = (-74.0060, 40.7128)   # (lon, lat)
ldn = (-0.1278, 51.5074)   # (lon, lat)

center_lon = (ny[0] + ldn[0]) / 2
center_lat = (ny[1] + ldn[1]) / 2

fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.Orthographic(center_lon, center_lat))

ax.stock_img()
ax.coastlines()

# Great circle line (geodetic transform)
ax.plot([ny[0], ldn[0]], [ny[1], ldn[1]], 'r-', lw=2, transform=ccrs.Geodetic())
ax.plot(ny[0], ny[1], 'ro', transform=ccrs.Geodetic())
ax.plot(ldn[0], ldn[1], 'ro', transform=ccrs.Geodetic())

ax.text(ny[0], ny[1], "New York", ha='right', fontsize=10, color='black', transform=ccrs.Geodetic())
ax.text(ldn[0], ldn[1], "London", ha='left', fontsize=10, color='black', transform=ccrs.Geodetic())

plt.title("Great Circle Between New York and London", fontsize=14)
plt.tight_layout()
plt.show()
'''

def q9():
    return '''\
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
lats = np.random.uniform(-90, 90, 500)
lons = np.random.uniform(-180, 180, 500)
mags = np.random.uniform(2, 8, 500)

fig = plt.figure(figsize=(15, 7))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

ax.stock_img()
ax.coastlines()

sc = ax.scatter(lons, lats, c=mags, s=(mags - 1)**2, cmap='hot_r', alpha=0.7, transform=ccrs.PlateCarree())
cbar = plt.colorbar(sc, ax=ax, pad=0.02, shrink=0.6)
cbar.set_label("Magnitude")

plt.title("Simulated Earthquake Locations", fontsize=16)
plt.tight_layout()
plt.show()
'''

def q10():
    return '''\
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.Mercator())

ax.set_global()
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='white')
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth=1)

gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
gl.top_labels = False
gl.right_labels = False

plt.title("World Map (Mercator Projection) with Coastlines and Country Borders")
plt.tight_layout()
plt.show()
'''

def q11():
    return '''\
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10, 12))
ax = plt.axes(projection=ccrs.Mercator())

ax.set_extent([-20, 55, -40, 40], crs=ccrs.PlateCarree())
ax.stock_img()
ax.coastlines(resolution='50m')
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor='beige', alpha=0.3)

plt.title("Africa Topography with Shaded Relief", fontsize=16)
plt.tight_layout()
plt.show()
'''

def q12():
    return '''\
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(15, 8))
ax = plt.axes(projection=ccrs.Robinson())

ax.set_global()
ax.stock_img()
ax.coastlines()

cities = [
    ("New York", 40.71, -74.01),
    ("London", 51.50, -0.12),
    ("Paris", 48.85, 2.35),
    ("Tokyo", 35.68, 139.69),
    ("Sydney", -33.87, 151.21),
    ("Rio de Janeiro", -22.90, -43.17),
    ("Moscow", 55.75, 37.61),
    ("Cairo", 30.04, 31.23),
    ("Toronto", 43.65, -79.38),
    ("Mumbai", 19.07, 72.87)
]

for name, lat, lon in cities:
    ax.plot(lon, lat, 'o', color='red', markersize=5, transform=ccrs.Geodetic())
    ax.text(lon + 3, lat + 3, name, transform=ccrs.Geodetic(), fontsize=9)

plt.title("Major World Cities on Robinson Projection", fontsize=14)
plt.tight_layout()
plt.show()
'''

def q13():
    return '''\
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

proj = ccrs.LambertConformal(central_longitude=-96, central_latitude=39,
                             standard_parallels=(33, 45))

fig = plt.figure(figsize=(12, 10))
ax = plt.axes(projection=proj)

ax.set_extent([-170, -50, 5, 75], crs=ccrs.PlateCarree())
ax.stock_img()
ax.coastlines(resolution='50m', linewidth=1)
ax.add_feature(cfeature.BORDERS, linewidth=1)

states = cfeature.NaturalEarthFeature(
    'cultural', 'admin_1_states_provinces_lines', '50m',
    edgecolor='black', facecolor='none'
)
ax.add_feature(states, linewidth=0.5)

gl = ax.gridlines(draw_labels=True, linestyle='--', linewidth=0.5, color='gray')
gl.top_labels = False
gl.right_labels = False

plt.title("North America - Lambert Conformal Projection", fontsize=16)
plt.tight_layout()
plt.show()
'''

# Optional convenience list
__all__ = [f"q{i}" for i in range(1, 14)]
