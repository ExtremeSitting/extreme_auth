#!/usr/bin/python

import requests
import json
import argparse

def main():

  parser = argparse.ArgumentParser(description='Usage: %prog [username] \
      [apikey] [region] options')
  parser.add_argument("-u",
                          "--username",
                          metavar="USERNAME",
                          help="API Username",
                          type=str,
                          required=True,
                          action="store")
  parser.add_argument("-a",
                          "--apikey",
                          metavar="APIKEY",
                          help="API Username",
                          type=str,
                          required=True,
                          action="store")
  parser.add_argument("-r",
                          "--region",
                          metavar="REGION",
                          help="Provisioning location",
                          type=str,
                          required=True,
                          action="store",
                          choices=["DFW", "ORD"])

  args = parser.parse_args()

  # re-assign arg returns
  username = args.username
  apikey = args.apikey
  region =  args.region
  # Initialize the all knowing endpoint dict
  services = {}
  
  def Authenticate(username, apikey, services):
    # Auth!
    payload = { "auth":{
                "RAX-KSKEY:apiKeyCredentials":{
                    "username":username,"apiKey":apikey} } }
    headers = {'content-type': 'application/json'}
    r = requests.post('https://auth.api.rackspacecloud.com/v2.0/tokens',
                        data=json.dumps(payload), headers=headers)
    auth_data = json.loads(r.text)[u'access']
    
    # Now to parse the mass of crap we just got.
    
    # Pull the token and add it to the services dict.
    if 'token' in auth_data:
        if 'id' in auth_data['token']:
            services['token'] = auth_data['token']['id']
    # Pull DDI and add it to the dict.        
    if 'tenant' in auth_data['token']:
      if 'id' in auth_data['token']['tenant']:
        services['account_id'] = auth_data['token']['tenant']['id']

    # The following mess evaluates the remaining json in the serviceCatalog
    # section and adds it all to the dict.
    if 'serviceCatalog' in  auth_data:
      products = auth_data['serviceCatalog']
      for service in range(len(products)):
          if len(products[service]['endpoints']) > 1:
            for dc in range(len(products[service]['endpoints'])):
              if products[service]['name'] not in services:
                services[products[service]['name']] = \
                        [(products[service]['endpoints'][dc]['region'], \
                        products[service]['endpoints'][dc]['publicURL'])]
              else:
                services[products[service]['name']].append(\
                    (products[service]['endpoints'][dc]['region'], \
                    products[service]['endpoints'][dc]['publicURL']))
          else:
            services[products[service]['name']] = \
                      products[service]['endpoints'][0]['publicURL']
    return services

  Authenticate(username, apikey, services)
  
  for k, v in services.items():
    print k, "\t", v
  

if __name__== "__main__":
  main()
