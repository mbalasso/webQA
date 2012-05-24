from lxml import etree
import sys
from xmlrpclib import Server
import urllib
import urllib2
import cookielib
from MultiPartForm import MultiPartForm
from cStringIO import StringIO
import datetime

plone_heading = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
      lang="en"
      metal:use-macro="here/main_template/macros/master"
      i18n:domain="plone">

      <metal:block fill-slot="top_slot"
               tal:define="dummy python:request.set('disable_border',1)" /> 

      <body>
      <div metal:fill-slot="main">"""

w3c_heading = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>W3C Link Checker: http://www.biomedtown.org</title>
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<meta name="generator" content="W3C-checklink/4.5 [4.154] libwww-perl/5.808" />
<link rel="stylesheet" type="text/css" href="http://validator.w3.org/docs/linkchecker.css" />
</head>
<body><div id="banner"><h1 id="title"><a href="http://www.w3.org/" title="W3C"><img alt="W3C" id="logo" src="http://validator.w3.org/images/no_w3c.png" /></a>
<a href="http://validator.w3.org/docs/checklink.html"><span>Link Checker</span></a></h1>
<p id="tagline">Check links and anchors in Web pages or full Web sites</p></div>
<div id="main">
""" 

footer = """</div><!-- main -->
<ul class="navbar" id="menu">

  <li><a href="http://validator.w3.org/docs/checklink.html" accesskey="3" title="Documentation for this Link Checker Service">Docs</a></li>
  <li><a href="http://search.cpan.org/dist/W3C-LinkChecker/" accesskey="2" title="Download the source / Install this service">Download</a></li>
  <li><a href="http://validator.w3.org/docs/checklink.html#csb" title="feedback: comments, suggestions and bugs" accesskey="4">Feedback</a></li>
  <li><a href="http://validator.w3.org/" title="Validate your markup with the W3C Markup Validation Service">Validator</a></li>
</ul>
<div>
<address>
W3C Link Checker<br /> version 4.5 (c) 1999-2009 W3C

</address>
</div>
</body>
</html>
"""

blacklist = ['?None&month:int=', '?currentDate=', '/RSS', '/image/', 'mail_password_form?userid=', 'externalEdit_', 'select_all_icon.gif', '/calendar.css', '/calendar.js', '/dhtml.js', '/month.css','discussionitem_icon.gif','portlet.js','jquery-1.3.2.js','jquery.cookie.js','jquery.corner.js',
'jquery.validate.js','biomedtown.org/news','biomedtown.org/accessibility-info','biomedtown.org/sitemap','biomedtown.org/what','biomedtown.org/author','biomedtown.org/contact-info','biomedtown.org/login.png','biomedtown.org/privacy_statement','biomedtown.org/events','biomedtown.org/Members',
'biomedtown.org/login_form','biomedtown.org/favicon','biomedtown.org/search_form','biomedtown.org/search.png','www.biomedtown.org/icon_export_ical.png','www.biomedtown.org/icon_export_vcal.png','additional-methods.js','defaultUser.gif','image_icon.gif','enter.png','target.png',
'home.png','citizenimage.png','join_form','application','image_icon.gif','search?Creator=','biomedtown.css','prefs_fckeditor_member','prefs_contact_info','password_form','search_icon.gif','text.png','www.biomedtown.org/message_inbox','enabling_cookies','fcTopic_icon_noans.gif','fcFolder_icon.gif','fcForum_icon.gif','user_profile','folder.gif','folder_icon.gif',
'pdf.png','ppt.png','doc.png','message_send_form','personalize_form','pdf_icon.gif','zip.png','tar.png','file_icon.gif','topic_icon.gif','exe.png','add_image.png','http://www.biomedtown.org/biomed_town/folder_contents']

        

if __name__ == "__main__":

    #f = open("bt_broken_link_check.xml",'r')    
    f = open("linkchecker-out.xml","r")

    broken_links = {}
    
    dom = etree.fromstring( f.read() )
    
    urls = []
    

    for url_nod in dom.iter():
        if url_nod.tag == 'urldata':
            parent = ''
            url = ''
            result = ''
            for nod in url_nod.iter():
                if nod.tag == 'realurl':
                    url = nod.text
                if nod.tag == 'parent':
                    parent = nod.text
                if nod.tag == 'valid':
                    result = nod.get("result",'')

            if result.count('404'):
                if not urls.count(url):
                    urls.append(url)
                if not broken_links.has_key(parent):
                    broken_links[parent] = []
                broken_links[parent].append(url)


    ###################################################################
    # STANDARD REPORT
    ###################################################################
    
    #change stdout and print to a file
    fout = open('checklink_output.html','w')

    original_stdout = sys.stdout

    sys.stdout = fout
    
    #print plone_heading
    print w3c_heading

    

    print '<h4> There is a total of %d broken links </h4> ' % len( urls ) 
    print '<dl>'
    for page in broken_links.keys():
        print '<dt> <h3> <a href="' + page + '" >'+ page +'</a></h3> </dt>'
        for b in broken_links[page]:
            print '<dd><a href="' + b +'" >' + b + '</a></dd>'
    print '</dl>'

    print footer
    
    sys.stdout = original_stdout
    fout.close()

    ###################################################################
    # BUILDING REPORT
    ###################################################################
    
    
    # get biomedtown building list
    biomedtown = Server('https://testuser:6w8DHF@www.biomedtown.org/portal_towntool/')
    buildings = biomedtown.getBuildingList()

    for building in buildings:
        buildings[building]['URL'] = buildings[building]['URL'].replace("http://","https://")
        
    
    #count total building broken links 
    building_broken_links = [] 
    for building in buildings.keys():
        buildings[building]['BL'] = {}
        for page in broken_links.keys():
            for b in broken_links[page]:
                if str(b).count(buildings[building]['URL']) or str(b).count(buildings[building]['URL'].replace('/biomed_town','')):
                    if not buildings[building]['BL'].has_key(page):
                        buildings[building]['BL'][page] = []
                    buildings[building]['BL'][page].append(b)
        
        if len(buildings[building]['BL'].values() ):                
            for page in buildings[building]['BL'].keys():                
                for b in buildings[building]['BL'][page]:
                    if not building_broken_links.count( page ):
                        building_broken_links.append(page)
                    

    #change stdout and print to a file
    fout = open('checklink_building.html','w')



    


    sys.stdout = fout
    print w3c_heading
    
    print '<h4> There is a total of %d broken links </h4> ' % len( building_broken_links ) 

    for building in buildings.keys():
        buildings[building]['BL'] = {}
        for page in broken_links.keys():
            for b in broken_links[page]:
                if str(b).count(buildings[building]['URL']) or str(b).count(buildings[building]['URL'].replace('/biomed_town','')):
                    if not buildings[building]['BL'].has_key(page):
                        buildings[building]['BL'][page] = []
                    buildings[building]['BL'][page].append(b)
        
        if len(buildings[building]['BL'].values() ):        
            print '<h2>', buildings[building]['Title'], '</h2>'
            print '<dl>'
            for page in buildings[building]['BL'].keys():
                print '<dt><h3><a href="' + page +'" >' + page + '</a></h3></dt>'
                for b in buildings[building]['BL'][page]:
                    print '<dd><a href="' + b +'" >' + b + '</a></dd>'
        
        
            
            print '</dl>'

    print """
</div>
</body>
</html>
"""

    fout.close()    
    sys.stdout = original_stdout
    
    
    ###################################################################
    # PUBLISH RESULT TO BIOMEDTOWN
    ###################################################################
    
    bt_url = 'https://www.biomedtown.org'

    username = 'testuser'
    password = '6w8DHF'
    url = bt_url + '/login_form'

    values = {'form.submitted':'1',
              'cookies_enabled':'1',
              'js_enabled':'1',
              'login_name': str( username ),
              '__ac_name': str( username ),
              '__ac_password':str( password ),
              'bt_privacy_acceptance':'accept', # fix for Biomedtown Portal Only
              }

    headers = { 'Content-Type' :'application/x-www-form-urlencoded'}


    cj = cookielib.CookieJar()           
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler(debuglevel=0))

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)

    response = opener.open(req)
    response.read()
    
    # we are now logged in
    
    now = datetime.datetime.now()
    timestamp = "%s-%s-%s-%s" % ( now.year, now.month, now.day, now.toordinal() ) 
    
    for file_to_publish in []:#['checklink_building.html','checklink_output.html']:
    
        url = bt_url + "/biomed_town/City_Hall/Planning/broken_links/createObject?type_name=File"
        req = urllib2.Request(url)
        
        response = opener.open(req)
        response.read()
        
        # we have created a new file
        
        url = response.url #portal_factory url    
        print url
        
        headers = { 'Content-Type' :'application/x-www-form-urlencoded'}
        
        form = MultiPartForm()
        if file_to_publish.count("building"):
            form.add_field('id', 'interna_broken_link_%s' % timestamp)
            form.add_field('title', 'Internal Broken Link Report %s-%s-%s' % (now.year, now.month, now.day) )
        else:
            form.add_field('id', 'total_broken_link_%s' % timestamp)
            form.add_field('title', 'Total Broken Link Report %s-%s-%s' % (now.year, now.month, now.day) )
            
        form.add_field('form_submit', 'Save')
        form.add_field('form.submitted','1')
        
        # Add the file
        f = open(file_to_publish,'r')
        form.add_file('file_file', 'checklink_output.html', fileHandle = f )
        f.close()

        # Build the request
        req = urllib2.Request(url)
        req.add_header('User-agent', 'PyMOTW (http://www.doughellmann.com/PyMOTW/)')
        body = str(form)
        req.add_header('Content-type', form.get_content_type())
        req.add_header('Content-length', len(body))
        req.add_data(body)
        
        response = opener.open(req)        
        response.read()
    
    
    ###################################################################
    # DASHBOARD STATUS CONTROL
    ###################################################################


    # dashboard must be set to red if exists a biomedtown internal bronken link

    bt_base_url = "www.biomedtown.org"
    failure = False

    for broken_links in broken_links.values():
        for broken_link in broken_links:
            if broken_link.count( bt_base_url ) :
                failure = True
                break

    if failure:
        print "KO"
    else:
        print "OK" 
