#!/usr/bin/python

import requests
import json
import argparse
import pprint


def main():

    parser = argparse.ArgumentParser(description='Usage: %prog [username] \
        [apikey] [region] options')
    parser.add_argument(
        '-u', '--username', metavar='USERNAME', help='API Username', type=str,
        required=True, action='store')
    parser.add_argument(
        '-a', '--apikey', metavar='APIKEY', help='API Username', type=str,
        required=True, action='store')

    args = parser.parse_args()

    services = {}

    def Authenticate(username, apikey):
        # Auth!
        # This may be changed over to httplib in the near future.
        payload = {
            'auth': {'RAX-KSKEY:apiKeyCredentials': {'username': username,
            'apiKey': apikey}}}
        headers = {'content-type': 'application/json'}
        response = requests.post(
            'https://auth.api.rackspacecloud.com/v2.0/tokens',
            data=json.dumps(payload), headers=headers)
        auth_data = json.loads(response.text)[u'access']

        # Now to parse the mass of crap we just got.
        #
        # Pull the token and id and add it to the services dict.
        try:
            auth_data['token']
            try:
                auth_data['token']['id'] and auth_data['token']['tenant']
                services['token'] = auth_data['token']['id']
                services['account_id'] = auth_data['token']['tenant']
            except KeyError:
                print 'Id and Tenant unavailable.'
                pass
        except KeyError:
            print 'Token data not found.'
            pass

        # Pull the default region
        try:
            auth_data['user']
            try:
                services['defaultRegion'] = auth_data['user'][
                'RAX-AUTH:defaultRegion']
            except KeyError:
                print 'No default region found.'
                pass
        except KeyError:
            print 'No user data available.'
            pass

        # The following mess evaluates the remaining json in the serviceCatalog
        # section and adds it all to the dict.
        try:
            products = auth_data['serviceCatalog']
            for service in range(len(products)):
                if len(products[service]['endpoints']) > 1:
                    for dc in range(len(products[service]['endpoints'])):
                        if products[service]['name'] not in services:
                            services[products[service]['name']] = \
                                [(products[service]['endpoints'][dc]['region'],
                                    products[service]['endpoints'][dc][
                                        'publicURL'])]
                        else:
                            services[products[service]['name']].append(
                                (products[service]['endpoints'][dc]['region'],
                                    products[service]['endpoints'][dc][
                                        'publicURL']))
                else:
                    services[products[service]['name']] = \
                        products[service]['endpoints'][0]['publicURL']
        except KeyError:
            print 'No services found'
            pass

        return services
        
        
    def list_servers(services):
        headers = {
            'X-Auth-Token': services['token'],
                'Content-Type': 'application/json'}
        response = requests.get(services['cloudServers'] + '/servers/detail',
            headers=headers)
        server_list = json.loads(response.text)
        return server_list

    services = Authenticate(args.username, args.apikey)
    server_list = list_servers(services)['servers']

    table = PrettyTable('Slice ID', 'Name', 'Image ID', 'Flavor ID')
    table.set_field_align('Slice ID', 'l')
    for server in     

    for server in range(0,len(server_list),1):
        print 'Slice ID:\t%s\nName:\t%s\nStatus:\t%s\n' % \
            (server_list[server]['id'], server_list[server]['name'],
                server_list[server]['status'])

if __name__ == '__main__':
    main()
