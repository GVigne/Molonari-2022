import numpy as np
from matplotlib import pyplot as plt 
import matplotlib.cm as cm 
from geometry import Column

column = Column('configColumn.json')
n=column.ncells
x = np.linspace(0, 1, 1) 
z = np.linspace(0, column.depth/column.ncells, column.ncells) 
X, Z = np.meshgrid(x, z) 

Val = X * np.sinc(z) 

plt.pcolormesh(X, Z, Val, cmap = cm.gray) 
#plt.pcolormesh(X, Z, Val) 
plt.show()

h =plt.hist2d(x, y)
plt.colorbar(h[3])