"""
    ArcGIS License Server monitor

    This runs as a standalone webserver that queries the ArcGIS
    license server and returns either HTML or JSON.
    Add "?f=json" to the query to get JSON.
"""
import sys, os
from flask import Flask, request
from read_lmutil import ReadLmutil
import json

app = Flask(__name__)

def generate_html(data_dict):
    """ Generate the contents of a simple web page from lmutil. """

    msg = ''
    msg += "Product: <b>%s</b>" %  data_dict['vendor']
    msg += '<br />'
    msg += "License server version: <b>%s</b> <br />" % data_dict['version']
    
    msg += ('<table border=1>\n')
    msg += ("<tr> <th>License</th> <th>Total</th> <th>In use</th> <th>Users</th> </tr>\n")

    for license in data_dict['licenses']:
        users = '<table>'
        total = license['total']
        in_use = license['in_use']
        for info in license['users']:
            users += '<tr><td>%s</td><td>%s</td><td>%s</tr>' % (
                info['name'], info['computer'], info['start'])
        users += '</table>'
        productname = license['productname']
        if in_use:
            # flag ALL LICENSES IN USE here by making them RED
            flag = 'green' if in_use < total else 'red'
            productname = '<font color="' + flag + '"><B>' + productname + '</B>'
        msg += '<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> </tr>\n' % (productname,
                     license['total'], in_use, users)
    msg += ('</table>')

    return msg


def generate_json(data_dict):
    return json.dumps(data_dict)


@app.route('/')
def f_html():
    """ Return output from lmstat """
    data_dict = ReadLmutil.read()

    # Select JSON or HTML as output
    format = request.args.get('f')
    if format and format.lower()=='json':
        return generate_json(data_dict)

    # Default is HTML
    return generate_html(data_dict)


if __name__ == '__main__':

    print("Test run, to confirm everything works before starting server.")
    data_dict = ReadLmutil.read()
    print(generate_json(data_dict))

    print("Starting service.")
    app.run(host = '0.0.0.0', debug = False)

# That's all!
