"""Fichero para pruebas de AframeXR"""

import webbrowser
import aframexr

data = aframexr.URLData('https://github.com/davidlab20/TFG/raw/main/examples/data.json')
chart1 = aframexr.Chart(data, position='-2 0.5 -6').mark_bar().encode(x=aframexr.X('model', axis=False), y='sales')
print(chart1.to_dict())
print(chart1.to_html())
#chart1.save('test.html')
#webbrowser.open_new_tab('test.html')
