#!/usr/bin/python

'''
Uses the "akamai property modify" CLI to updte the version notes instead. Akama CLI and property module should be installe for this to work.

USAGE: python3 add_pipeline_cli_comments.py <.edgerc section> <pipeline name> <environment> <version notes or comments>

EXAMPLE:
$ python3 add_pipeline_cli_comments.py akau_papi jaescalo.edge.akau.webperf.it dev 'My new comments'

'''

import requests, json, sys, os
from akamai.edgegrid import EdgeGridAuth,EdgeRc
import urllib
import subprocess
from urllib.parse import urljoin


# At this point there is an open version of the property open for edits. Using the Property-Manager CLI to retrieve its details
def property_cli_get_version_and_id(section_name, property_name):

    cli_output = subprocess.check_output(['akamai','property-manager','search',property_name,'--section',section_name,'-f','json'])
    cli_output_json = json.loads(cli_output)

    print('COLLECTING PROPERTY ACTIVATION DETAILS...', cli_output_json)

    for property_activation in cli_output_json:
        if (property_activation['stagingStatus'] == 'INACTIVE' and property_activation['productionStatus'] == 'INACTIVE'):
            property_version = property_activation['propertyVersion']

            print('PROPERTY VERSION:', property_version)

    return(property_version)


def update_property_notes(section_name, property_name, property_version, property_comments):
    print('UPDATING PROPERTY VERSION NOTES...')
    cli_output = subprocess.check_output(['akamai','property','modify',property_name,'--propver',str(property_version),'--notes',property_comments,'--section',section_name])

    return()


# Main function
def main():

    # The script execution should be: python3 add_papi_cli_comments.py <section> <pipeline name> <pipelne environment> <version notes or comments>
    section_name = str(sys.argv[1])
    pipeline_name = str(sys.argv[2])
    pipeline_environment = str(sys.argv[3])
    property_comments = str(sys.argv[4])
    property_name = pipeline_environment + '.' + pipeline_name

    global baseurl, session

    # Define the autorization parameters related to the .edgerc file
    rc_path = os.path.expanduser('~/.edgerc')
    edgerc = EdgeRc(rc_path)
    baseurl = 'https://%s' % edgerc.get(section_name, 'host')

    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(edgerc, section_name)

    property_version = property_cli_get_version_and_id(section_name, property_name)

    update_property_notes(section_name, property_name, property_version, property_comments)

# Main Program
if __name__ == "__main__":
    # Main Function
    main()
