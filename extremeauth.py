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
  
  services = {}
  
  def Authenticate(username, apikey):
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
    try:
      auth_data['token']
      try:
        services['token'] = auth_data['token']['id']
      except KeyError:
        print 'No auth token found'
        pass
    except KeyError:
      print 'No auth token found'
      pass
      
    # Pull DDI and add it to the dict.
      if 'tenant' in auth_data['token']:
        if 'id' in auth_data['token']['tenant']:
          services['account_id'] = auth_data['token']['tenant']['id']
    # Pull the default region
    if 'user' in auth_data:
      if 'RAX-AUTH: defaultRegion' in auth_data['user']:
        services['defaultRegion'] = auth_data['user']\
          ['RAX-AUTH: defaultRegion']

    # The following mess evaluates the remaining json in the serviceCatalog
    # section and adds it all to the dict.
    try:
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
    except KeyError:
      print 'No services found'
      pass
    
    return services

  services = Authenticate(args.username, args.apikey)
  
  for k, v in services.items():
    print k, "\t", v
  

if __name__== "__main__":
  main()
