"""Fichero para pruebas de AframeXR"""

import webbrowser
import aframexr

url_data = aframexr.URLData('https://davidlab20.github.io/TFG/examples/data.json')
pieChartJSON = aframexr.Chart(url_data, position="0 5 -4").mark_arc().encode(color='model', theta='sales')
pieChartJSON.save('piechart.html')
