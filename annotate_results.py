# coding=utf-8
# created Jan 11, 2020 by Ge Zhang
# generate annotation results from HTMLs
# see list of htmls on google doc (to_filter_3)
# compare results of 2 authors (Mike Merrill & Ge Zhang)


import os
from bs4 import BeautifulSoup, Tag
import pdb
import json

notebooks = ["nb_1090484.ipynb","nb_1240128.ipynb","nb_1033591.ipynb","nb_1242788.ipynb","nb_1004385.ipynb","nb_1025815.ipynb","nb_1185862.ipynb","nb_1157710.ipynb","nb_1024739.ipynb","nb_1051445.ipynb","nb_1073105.ipynb","nb_1066338.ipynb","nb_1221634.ipynb","nb_1053523.ipynb","nb_1235946.ipynb","nb_1059730.ipynb","nb_1123257.ipynb","nb_1006895.ipynb","nb_1043186.ipynb","nb_1112388.ipynb","nb_1002722.ipynb","nb_1064527.ipynb","nb_1089313.ipynb","nb_1184211.ipynb","nb_1183716.ipynb","nb_1163801.ipynb","nb_1058335.ipynb","nb_1242794.ipynb","nb_1088637.ipynb","nb_1234699.ipynb","nb_1090152.ipynb","nb_1231330.ipynb","nb_1149480.ipynb","nb_1172355.ipynb","nb_1143058.ipynb","nb_1203216.ipynb","nb_1102984.ipynb","nb_1215903.ipynb","nb_1071938.ipynb","nb_1109134.ipynb","nb_1202205.ipynb","nb_1000752.ipynb","nb_1156487.ipynb","nb_1170705.ipynb","nb_1143576.ipynb","nb_1249011.ipynb","nb_1026834.ipynb","nb_1151070.ipynb","nb_1116374.ipynb","nb_1022912.ipynb","nb_1226996.ipynb","nb_1236355.ipynb","nb_1189833.ipynb","nb_1058499.ipynb","nb_1195600.ipynb","nb_1005070.ipynb","nb_1176809.ipynb","nb_1103777.ipynb","nb_1198274.ipynb","nb_1212287.ipynb","nb_1245037.ipynb","nb_1180754.ipynb","nb_1215918.ipynb","nb_1108440.ipynb","nb_1183781.ipynb","nb_1228071.ipynb","nb_1026329.ipynb","nb_1221697.ipynb","nb_1122022.ipynb","nb_1222512.ipynb","nb_1138647.ipynb","nb_1118399.ipynb","nb_1108807.ipynb","nb_1218288.ipynb","nb_1054793.ipynb","nb_1183943.ipynb","nb_1234234.ipynb","nb_1089165.ipynb","nb_1105414.ipynb","nb_1005207.ipynb","nb_1161031.ipynb","nb_1062193.ipynb","nb_1227519.ipynb","nb_1046805.ipynb","nb_1068026.ipynb","nb_1138666.ipynb","nb_1103327.ipynb","nb_1222945.ipynb","nb_1159388.ipynb","nb_1031433.ipynb","nb_1096612.ipynb","nb_1098281.ipynb","nb_1193256.ipynb","nb_1011373.ipynb","nb_1034447.ipynb","nb_1163520.ipynb","nb_1223629.ipynb","nb_1050605.ipynb","nb_1068488.ipynb","nb_1147823.ipynb", ]

htmls = [nb.replace('.ipynb','.html') for nb in notebooks]


# path = '/homes/gws/gezhang/jupyter-notebook-analysis/backup_templates'
# path = '/homes/gws/gezhang/jupyter-notebook-analysis/templates'
path= './mike'
nb_path = '/projects/bdata/jupyter/_7_1'


files = os.listdir(path)
error_files = []
for  html,nb in zip(htmls, notebooks):
	if html not in files:
		error_files.append(html)
		continue
	# get annotate results
	with open(os.path.join(path, html),'r') as f:
		html_source = f.read()
	soup = BeautifulSoup(html_source)
	cells = soup.find_all("div", class_="inner_cell")
	origine_opts = [cell.find('option', {'selected': True})["value"] for cell in cells ]

	# get cells from ipynb
	with open(os.path.join(nb_path, nb),'r') as f:
		nb_content =json.load(f)
	nb_cells =nb_content["cells"]
	if html=='nb_1138647.html':
		nb_cells = nb_cells[:8]+nb_cells[9:]
	if len(cells)!=len(nb_cells):
		pdb.set_trace()

	# add results on nb_cells
	for opt,cell in zip(origine_opts,nb_cells):
		cell["stage"] = opt
	with open(os.path.join(path, html.replace('.html', '.json')), 'w') as fout:
		json.dump(nb_cells, fout,ensure_ascii=False)
	# pdb.set_trace()
print(error_files)
