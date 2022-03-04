"""
Parse the output from the lmutil program.
"""
import sys, os, subprocess
import re
from datetime import datetime, timezone
from config import Config

# Define the regular expressions used to parse the output of lmstat.
re_daemon = re.compile(r'\s*(\w+)\: UP (.*)')
re_Users_of = re.compile(r'^Users of (\S+):.* of (\d+).* of (\d+).*')
re_user_info = re.compile(r'\s+(\S+)\s+(\S+).*start\s+(.*)')

# The timestamps are in such a stupid format that I opted to not parse them.
# "Fri 7/12 8:42" -- no year! stupid. -- no timezone, also stupid.
timeformat = "%a %m/%d %H:%M"

sillynames = {
    'ARC/INFO': 'ArcGIS Desktop Advanced',
    'Editor': 'ArcGIS Desktop Editor',
    'Viewer': 'ArcGIS Desktop Basic',
    'desktopAdvP': 'ArcGIS Pro Advanced',
    'desktopStdP': 'ArcGIS Pro Standard',
    'desktopBasicP': 'ArcGIS Pro Basic',
    '3DAnalystP': '3D Analyst Pro',
    'spatialAnalystP': 'Spatial Analyst Pro',
    'networkAnalystP': 'Network Analyst Pro',
    'ArcStorm': 'ArcStorm',
    'ArcStormEnable': 'ArcStorm "enable"',
    'Grid': 'Spatial Analyst',
    'MrSID': 'MrSID add on',
    'TIFFLZW': 'LZW add on for TIFF',
    'VBA': 'VisualBasic',
    'Plotting': 'ArcPlot extension',
}

class ReadLmutil(object):

    @staticmethod
    def parse_lmutil(fp):

        # The file is organized into sections based on product.
        # In each product section there can be a list of users with licenses in use
        # so that's how the data returned is organized.
        # It's up to the caller to sort it out into other report formats.

        # TODO add complicated logic here to figure out if the license was checked out
        # in a previous year.
        now = datetime.now()
        thisyear = now.year

    # A bit of documentation
    #    data ={
    #        "vendor":  "Vendor not found",  # normally ARCGIS
    #        "version": "Version not found", # a string like v11.16.2
    #        "licenses": [] # a list of licenses supported by this lmmgrd
    #    }
    #    license = {
    #        "productname": "",  # eg ARC/INFO
    #        "total": 0,
    #        "in_use": 0,
    #        "users": []
    #    }
    #    user = {  # a list of users currently using licenses
    #            "name": "unknown",   # user's name
    #            "computer": "pw1234",  # name issued to client computer
    #            "start": None,       # datetime when check out occurred.
    #    }

        # Stash data here as it is collected
        data = {}
        licenses = []  # A list of licenses
        userinfo = [] # A list of users for the current license
        license = {} # A single license record

        for r in fp.readlines():
            # We use leading whitespace so only strip on the right
            if type(r) == type(''):
                # reading from file
                line = r.rstrip()
            else:
                # reading from subprocess
                line = str(r, encoding='utf-8').rstrip()
            #print(line)

            # Vendor daemon status section shows,
            # this is ARCGIS and a version number.
            mo = re_daemon.search(line)
            if mo:
                data['vendor'] = mo.group(1)
                data['version'] = mo.group(2)
                continue

            mo = re_Users_of.search(line)
            if mo:
                if 'productname' in license:
                    #print(license['productname'])
                    # We are starting a new license section
                    # so we need to add the previous to our list
                    # and we need to attach the userinfo, if any
                    license['users'] = userinfo
                    licenses.append(license)
                    license = {}

                license_type = mo.group(1)
                if license_type in sillynames:
                    license_type = sillynames[license_type]
                issued = mo.group(2)
                in_use = mo.group(3)
    #            print(license_type, issued, in_use)
                license = {
                    'productname': license_type,
                    'total':  int(issued),
                    'in_use': int(in_use),
                }

                userinfo = [] # Clear out previous userinfo and start fresh
                continue

            mo = re_user_info.search(line)
            if mo:
                start = mo.group(3)
#                dt = datetime.strptime(start, timeformat).replace(year=thisyear, microsecond=0, second=0)
                userinfo.append({
                    'name': mo.group(1),
                    'computer': mo.group(2),
                    'start': start
                })

        # Catch whatever's left
        if 'productname' in license:
            # We are starting a new license section
            # so we need to add the previous to our list
            # and we need to attach the userinfo, if any
            license['users'] = userinfo
            licenses.append(license)

        # Replace placeholder data with real data
        data['licenses'] = licenses

        return data

    @staticmethod
    def get_fp():

        if Config.TEST_MODE:
            test_file = 'lmstat.txt'    
            fp = open(test_file, 'r', encoding='utf-8')
        else:
            # Create a pipe to talk to lmutil
            print(Config.LMUTIL)
            p = subprocess.Popen(Config.LMUTIL, stdout=subprocess.PIPE, bufsize=1)
            fp = p.stdout

        return fp

    @staticmethod
    def read():
        fp = ReadLmutil.get_fp()
        data_dict = ReadLmutil.parse_lmutil(fp)
        fp.close()
        return data_dict

if __name__ == '__main__':

    import pprint

#    for e in os.environ: print(e, os.environ.get(e))

    data_dict = ReadLmutil.read()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data_dict)

# That's all!
