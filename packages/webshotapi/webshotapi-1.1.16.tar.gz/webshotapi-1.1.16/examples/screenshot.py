import os
from webshotapi import Client


if __name__ == "__main__":
    try:

        API_TOKEN = os.environ['WEBSHOTAPI_KEY']
        client = Client(API_TOKEN)

        result = client.screenshot({
            'url': 'https://www.cnn.com',
            'remove_modals': True, # Remove cookies popup with AI
        })

        if result.save('/tmp/test.jpg'):
            print("File saved")
        else:
            print("Error with save file")

    except Exception as e:
        print("Error:")
        print(e)
    #print(result)



