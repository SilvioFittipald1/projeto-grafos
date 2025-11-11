import sys
import os
# garante que 'src' está no path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
import viz

viz.plot_graph(None)
