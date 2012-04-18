#
#    Copyright (c) 2009 Matteo Balasso (m.balasso@scsolutions.it)
#    License: GNU GPLv3
#
#    This file is an extension of Pylot.
#    This program parse a xml file in order to create a .bat file to execute all tests 
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License 
#    for more details.
#
 
import xml.dom.minidom
import os
from datetime import datetime 

from scan_directory import scan_directory

try: 
    last_res_dir = open("./lastRun.txt","r").read()
    res_date = str(last_res_dir).split('/')[-1]    
    res_dir = open("./resultsDir.txt","r").read()
    
    img_dir = "../../imgs"
    
    print last_res_dir
    print res_date
    print res_dir
    
    dom = xml.dom.minidom.parse('./config.xml')
    testparams = dom.getElementsByTagName("TestResultParameter")

    res_params = {}
    res_params_type = {}
    res_params_title = {}

    for parameter in testparams:    
        if parameter.hasAttribute("Value") and parameter.getAttribute("Value") != "" and  parameter.hasAttribute("Name") and parameter.getAttribute("Name") != "":
            res_params[parameter.getAttribute("Name")] = float(parameter.getAttribute("Value"))
            
            if parameter.hasAttribute("Type") and parameter.getAttribute("Type") !="":
                 res_params_type[parameter.getAttribute("Name")] = parameter.getAttribute("Type")
            
            if parameter.hasAttribute("Title") and parameter.getAttribute("Title") !="":
                 res_params_title[parameter.getAttribute("Name")] = parameter.getAttribute("Title")
                 

    res_stats = scan_directory(theDirectory=last_res_dir, scanSub=True, key="statistics", ext=".txt", withPath=True, withExt=True)



    error = False

    

    html = """<html><title>Pylot Test Result Summary</title>"""
    html += """<link rel="stylesheet" type="text/css" href="../../pylot.css" title="default"/>"""  
    html += """\n<body><div id="wrapper-container">\n<div id="container">\n""" 
    html+= """<div id="header"><h1 class="left"><img src="%s/biomedtown.jpg" /></h1><h2 class="left">Pylot Test Result Summary</h2></div>""" % img_dir
    html += """<br /><span class="testDate"> Test Run :%s </span><br /> """ % res_date
    html += """<div class="testSummary"> <h4>Test Parameters</h4>\n <table>\n"""

    for par in res_params.keys():
        
        gt_lt = "&le;"            
        if res_params_type[par] == 'LowerBound':
            gt_lt = "&ge;"
        elif res_params_type == 'UpperBound':
            gt_lt = "&le;"                
        
        
        html += "<tr><th>%s</th> <td> %s %s </td> </tr>\n" % (res_params_title[par], gt_lt, res_params[par]  )

    html += "\n</table>\n</div>"

    html += """<div class="testResults"> <table id="listing"> <thead> <tr> <th> test name </th>"""
    for par in res_params.keys():
        html += """<th> %s </th> """ % (res_params_title[par]) 
        
    html += """ <th> detailed test result </th></tr> </thead> <tbody> """

    for stat_file in res_stats:
        stat = eval(open(stat_file,"r").read())
        
        
        res_html = stat_file.replace("statistics.txt","results.html")    
        
        print res_html
        
        html += "<tr>"
        
        test_title =  stat['test_name']
        
        html += """<td> <span class="testTitle"> %s</span></td>""" % (test_title)
        
        
        
        for par in res_params.keys():
            if stat.has_key(par):
                
                print "%s\t : %s = %s " % (par, res_params_type[par], res_params[par]  )
                print "\t\t\t\t%s" % stat[par]
                
                td_class = "green"

                
                if res_params_type[par] == 'LowerBound':
                    if float(stat[par]) < float(res_params[par]):
                        error = True
                        td_class = "red"
                elif res_params_type[par] == 'UpperBound':
                    if float(stat[par]) > float(res_params[par]):
                        error = True
                        td_class = "red"
                
                html += """<td class="%s"> %.2f </td>""" % (td_class, stat[par])
                
            else:
                html +=" <td />"
        
        html += """<td><a class="activea" href=".%s"><img src="%s/report.png" alt="report" title="detailed results page"/> </a></td>""" % (res_html.replace(last_res_dir,""), img_dir)
        
        html += "</tr>"

    html += """ </tbody> </table> </div></div></body></html>"""

    fhtml = open("%s/summary.html" % last_res_dir,"w")
    fhtml.write(html)
    fhtml.close()


    img_dir = "../imgs"
    


    html = """<html><title>Pylot Test Result Summary</title>"""
    html += """<link rel="stylesheet" type="text/css" href="../pylot.css" title="default"/>"""  
    html += """\n<body><div id="wrapper-container">\n<div id="container">\n""" 
    html += """<div id="header"><h1 class="left"><img src="%s/biomedtown.jpg" /></h1><h2 class="left">Pylot Test Results</h2></div>""" % img_dir
    html += """ <div class="testResults"> <table id="listing"><tbody>"""

    for d in os.listdir(res_dir):
        if not d.lower().count('cvs') and not d.lower().count('index.html'):
            html += """<tr>
                         <th>%s</th>
                         <td><a class="activea" href="./%s/summary.html"><img src="%s/report.png" alt="report" title="detailed results page"/> &nbsp;test summary</a>
                         </td></tr> """ % (d, d, img_dir)

    html += """ </tbody> </table> </div></div></body></html>"""

    
    
    
    fhtml = open("%s/index.html" % res_dir,"w")
    fhtml.write(html)
    fhtml.close()

    print "OK"
except:
    print "ERROR"

