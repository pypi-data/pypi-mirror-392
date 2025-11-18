import os
from webshotapi import Client


if __name__ == "__main__":
    try:
        API_TOKEN = os.environ['WEBSHOTAPI_KEY']
        client = Client(API_TOKEN)
        result = client.pdf({
            'url': 'https://www.example.com',
            'remove_modals': True
        })

        if result.save('/tmp/test.pdf'):
            print("File saved")
        else:
            print("Error with save file")

    except Exception as e:
        print("Error:")
        print(e)



