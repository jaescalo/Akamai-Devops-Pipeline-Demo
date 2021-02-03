#!/usr/bin/python

'''
Uses API calls to update the rule tree with only the comments for the version notes.

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
            property_id = property_activation['propertyId']
            property_version = property_activation['propertyVersion']
            property_group_id = property_activation['groupId']
            property_contract_id = property_activation['contractId']

            print('PROPERTY ID:', property_id)
            print('PROPERTY VERSION:', property_version)
            print('PROPERTY GROUP ID:', property_group_id)
            print('PROPERTY CONTRACT ID:', property_contract_id)

    return(property_id, property_version, property_group_id, property_contract_id)


# Modify the rule tree to add the comments JSON element
def edit_rule_tree(property_comments, pipeline_name, pipeline_environment):
    comments = {"comments": property_comments}
    print('ADDING THE FOLLOWING COMMENTS JSON ELEMENT:', comments)

    json_file_path = './' + pipeline_name + '/dist/' + pipeline_environment + '.' + pipeline_name + '.papi.json'
    print('EXTRACTING RULE TREE FROM:', json_file_path)

    json_file = os.path.expanduser(json_file_path)

    with open(json_file, "r+") as file:
        data = json.load(file)
        data.update(comments)
        print('UPDATING THE RULE TREE WITH THE COMMENTS:', data)

    return(data)


# Update the rule tree which has the comments JSON element
def update_rule_tree(property_id, property_version, property_group_id, property_contract_id, new_rule_tree):
    new_rule_tree = json.dumps(new_rule_tree)
    api_endpoint = '/papi/v1/properties/' + property_id + '/versions/' + str(property_version) + '/rules?groupId=' + property_group_id + '&contractId=' + property_contract_id

    print('UPDATING COMMENTS THROUGH API CALL TO:', api_endpoint)
    headers = {'Content-Type':'Application/json'}
    result = session.put(urljoin(baseurl, api_endpoint), data=new_rule_tree, headers=headers)
    print('HTTP STATUS: ',result.status_code)
    print(json.dumps(result.json()))



# Main function
def main():

    # The script execution should be: python3 add_papi_cli_comments.py <section> <property name> <version notes or comments>
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

    property_id, property_version, property_group_id, property_contract_id = property_cli_get_version_and_id(section_name, property_name)

    new_rule_tree = edit_rule_tree(property_comments, pipeline_name, pipeline_environment)

    update_rule_tree(property_id, property_version, property_group_id, property_contract_id, new_rule_tree)



# Main Program
if __name__ == "__main__":
    # Main Function
    main()
