import os
from webshotapi import Client


if __name__ == "__main__":
    try:

        API_TOKEN = os.environ['WEBSHOTAPI_KEY']
        client = Client(API_TOKEN)

        result = client.video_json({
            'url': 'https://www.example.com',
            'scrolling_enable': True,
            'video_duration': 7,
            'remove_modals': True, # Remove cookies popup with AI
        })

        print(result['url'])
        print(result)

    except Exception as e:
        print("Error:")
        print(e)
    #print(result)



