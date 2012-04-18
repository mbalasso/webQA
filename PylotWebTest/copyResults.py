import xml.dom.minidom
import os
import shutil

try:
	all_res_dir = open("./resultDir.txt","r").read().rstrip('\n')
	last_res_dir = open("./lastRun.txt","r").read().rstrip('\n')
	res_dir=last_res_dir.split('/')[-1:][0]

	dom = xml.dom.minidom.parse(all_res_dir+"/index.html")
	tbody= dom.getElementsByTagName('tbody')[0]


	img_dir = "../imgs"


	htmlAppend = """ <tr><th>%s</th><td><a class="activea" href="./%s/summary.html"><img src="%s/report.png" alt="report" title="detailed results page" />test summary</a></td></tr> """ % (res_dir, res_dir, img_dir)

	childNode = xml.dom.minidom.parseString("<html>"+htmlAppend+"</html>")

	##Add last run Test in index.html
	tbody.insertBefore(childNode.getElementsByTagName('tr')[0],dom.getElementsByTagName('tr')[0])

	##move results dir to destination dir
	shutil.copytree(last_res_dir, all_res_dir+"/"+res_dir)

	#update main index.html
	fhtml = open("%s/index.html" % all_res_dir,"w")
	fhtml.write(dom.toprettyxml())
	fhtml.close()

	print "OK"
except:
	print "ERROR"