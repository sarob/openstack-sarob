# Copyright 2013 Yahoo! Inc. All Rights Reserved
# Copyright 2013 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


'''
The code must executed within ./openstack-manuals/doc/training-manuals/sources/. Requirement
that pandoc-1.12.0.2 is installed on the local system and that the path to pandoc is
part of the user profile. Find pandoc here http://johnmacfarlane.net/pandoc/installing.html.
The code will automagically create the 6 'core' openstack repositories and convert the
rst docs to xml. The script has four parts: create_repo, pull_repo_updates, convert_rst,
and rst_xml_cleanup.
* create_repo: clones the nova, glance, cinder, neutron, swift, keystone, and horizon
    repositories into the directory above openstack-manuals repository. It is assumed
    this is where repositories belong on the local system.
* pull_repo_updates: Intended that all the local repositories are to be pulled for updates
    before starting a new branch.
* convert_rst: use pandoc to convert the rst to docbook 4.5 xml. Copy over images as well.
* rst_xml_cleanup: convert docbook 4.5 xml to docbook 5.0 along with some cleanup of poorly
    formatted tags.
'''


import os
import re
import sys


def create_repo(directory):
    #clone remote to local repo root, ignore error if exist
    os.chdir("../../../../")
    for x in directory:
        os.system("git clone https://github.com/openstack/" + x + ".git")


def pull_repo_updates(directory):
    #pull remote repo updates
    for x in directory:
        os.chdir("./" + x)
        os.system("git pull origin master")
        os.chdir("../")
    os.chdir(sys.path[0])


def convert_rst(directory):
    #walk repo doc source converting rst to training-guide source sudo rst-xml
    docs_location = ["/doc/source/devref/", "/doc/source/", "/doc/source/devref/", "/doc/source/devref/", "/doc/source/", "/doc/source/", "/doc/source/"]
    for y in range(0, len(directory)):
        print("start convert rst: " + directory[y])
        os.system("rm -R " + directory[y])
        try:
            #use try for when the remove directory fails
            os.mkdir("./" + directory[y])
        except OSError:
                pass
        os.chdir(directory[y])
        #os.system("cp -R ../../../../../" + directory[y] + "/doc/source/images " + "./images/")
        for x in os.listdir("../../../../../" + directory[y] + docs_location[y]):
                x = x.split(".rst")
                os.system("pandoc ../../../../../" + directory[y] + docs_location[y] + x[0] + ".rst -f rst -t docbook -s -o " + x[0] + ".rst-xml")
        os.chdir("../")
        print("completed convert rst: " + directory[y])


def rst_xml_cleanup(directory):
    #reformat rst xml output with some reformatting
    for z in range(0, len(directory)):
        os.chdir("./" + directory[z])
        print("rst to xml cleanup in directory " + directory[z])
        for x in os.listdir("./"):
            infile = open(x)
            outfilename = infile.name.split(".rst-xml")
            outfile = open(outfilename[0] + ".xml", "w+")
            #header of new xml file
            startfile = 1
            outfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            outfile.write("  <section xmlns=\"http://docbook.org/ns/docbook\"\n")
            outfile.write("  xmlns:xi=\"http://www.w3.org/2001/XInclude\"\n")
            outfile.write("  xmlns:xlink=\"http://www.w3.org/1999/xlink\"\n")
            outfile.write("  version=\"5.0\"\n")
            for line in infile:
                #keep reading until first title found, which should be the article title
                match1 = re.search(r'(<title>)(.*)(</title>)', line)
                if match1:
                    title = match1.group(2)
                    xml_section_name = match1.group(2)
                    xml_section_name = xml_section_name.replace(" ", "-")
                    outfile.write("  xml:id=\"" + xml_section_name + "\">\n")
                    outfile.write("<title>" + title + "</title>\n")
                    break
            #copy rest of file
            for line in infile:
                #convert match to function call
                match2 = re.search(r'(</article)(.*)', line)
                match3 = re.search(r'(</sect)([0-9])(.*)', line)
                match5 = re.search(r'(<sect)([0-9])(.*)(id)(.*)', line)
                match6 = re.search(r'(.*)(<ulink url)(.*)', line)
                match7 = re.search(r'(.*)(<para>)(.*)', line)
                match9 = re.search(r'(.*)(</ulink>)(.*)', line)
                match10 = re.search(r'(.*)(<ulink url)(.*)(</ulink>)(.*)', line)
                if match2:
                    #remove article tag
                    continue
                elif match7 and startfile == 1:
                    #wrap orphaned paragraphs at the beginning of the file
                    outfile.write("<section xml:id=\"page-abstract\">\n")
                    outfile.write("<title>Page Abstract</title>\n")
                    outfile.write("<para>")
                    for line in infile:
                        #will need to add match for ulink here as well
                        #regex function call be the best solution
                        match82 = re.search(r'(.*)(</para>)(.*)(sect)(.*)(id)(.*)', line)
                        match51 = re.search(r'(.*)(sect)(.*)(id)(.*)', line)
                        if not match51 and not match82:
                            outfile.write(line)
                        elif match82:
                            #complete wrap orphaned paragraphs
                            #startfile = 0
                            outfile.write("### match82 ###")
                            outfile.write("</para>" + "\n")
                            outfile.write("</section>\n")
                            outfile.write("<section xml:id" + match81.group(7) + "\n")
                            break
                        elif match51:
                            #complete wrap orphaned paragraphs
                            startfile = 0
                            #outfile.write("### match51 ###")
                            outfile.write("</section>\n")
                            outfile.write("<section xml:id" + match51.group(5) + "\n")
                            break
                elif match5:
                    #convert sect* to section
                    outfile.write("<section xml:id" + match5.group(5) + "\n")
                elif match3:
                    #convert sect* to section
                    outfile.write("</section" + match3.group(3) + "\n")
                elif match10:
                    #convert ulink url to link xlink:href
                    outfile.write(match10.group(1) + "<link xlink:href" + match10.group(3) + "</link>" + match10.group(5) + "\n")
                elif match6:
                    #convert ulink url to link xlink:href
                    outfile.write(match6.group(1) + "<link xlink:href" + match6.group(3) + "\n")
                elif match9:
                    #convert ulink url to link xlink:href
                    outfile.write(match9.group(1) + "</link>" + match9.group(3) + "\n")
                else:
                    outfile.write(line)
            outfile.write("</section>\n")
            infile.close()
            outfile.close()
        os.system("rm *.rst-xml")
        os.chdir("../")


repo = ['nova', 'glance', 'cinder', 'neutron', 'swift', 'keystone', 'horizon']

create_repo(repo)
pull_repo_updates(repo)
convert_rst(repo)
rst_xml_cleanup(repo)