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
import sys
from datetime import datetime 

from scan_directory import scan_directory

try:
    try:
        result_dir = open("./resultsDir.txt","r").read()
    except:        
        f = open("./resultsDir.txt","w")
        f.write('./results')
        f.close()
        result_dir = './results'
    
    res_dir = "%s/%s" % (result_dir, str( datetime.now().date() )) 

    print res_dir

    pythoncmd = sys.executable

    command_lines = []

    dom = xml.dom.minidom.parse('./config.xml')
    testparams = dom.getElementsByTagName("TestCaseParameter")


    command_line = "%s run.py " % (pythoncmd)

    for parameter in testparams:
        
        if parameter.hasAttribute("Value") and parameter.getAttribute("Value") != "":
            command_line = "%s %s %s"  % (command_line, parameter.getAttribute("Directive"),parameter.getAttribute("Value"))

    print command_line

    my_testcases = scan_directory(theDirectory="%s/testcases"%(os.getcwd()), scanSub=True, key="", ext=".xml", withPath=False, withExt=True)


    print my_testcases

    for test in my_testcases:
        command_lines.append( "%s -n %s -x ./testcases/%s -o %s \n" % (command_line, test.replace(".xml",""), test, res_dir ) )

    command_lines.append("echo OK") 
    batfile = open("start.bat","w")

    batfile.writelines(command_lines)
    batfile.close()

    lastRun = open("lastRun.txt","w")
    lastRun.write(res_dir)
    lastRun.close()
    print "OK"

except:
    print "ERROR"
        



 
