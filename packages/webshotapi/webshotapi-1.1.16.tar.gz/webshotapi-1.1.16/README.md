# WebShotApi.com API client for Python

Capture and store website snapshots effortlessly with our SaaS service. 
Use our AI unique algorithm for remove cookies and popup banner before take screenshot.
Save images in popular formats such as JPG, PNG, WEBP and PDF. 
Additionally, extract selectors for every HTML element, 
complete with coordinates and CSS styles post-browser rendering. 


Full documentation about our api you can find in this website [Website screenshot API DOCS](https://webshotapi.com/docs/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/webshotapi) to install our client in Python.

```bash
pip install webshotapi
```

OR
```bash
pip3 install webshotapi
```

# Remove cookies popup before take sceenshot
![Remove cookies before take screenshot](https://raw.githubusercontent.com/webshotapi/webshotapi-website-screenshot-php-client/6681d3d38ea13391a30b2e43b8c37191e2d41bef/images/remove-cookies-before-take-screenshot.png)

Effortlessly remove annoying cookies pop-ups before capturing stunning screenshots. 
Let our advanced AI algorithm transform the way you visualize websites, ensuring a cookie-free snapshot every time! [Read more](http://webshotapi.com/blog/remove-cookies-before-take-screenshot/)


# API KEY
Api key you can generate after register.
[https://dashboard.webshotapi.com/api_keys](https://dashboard.webshotapi.com/api_keys)

# Usage

### Take screenshot video
Example gif:
[![](https://raw.githubusercontent.com/webshotapi/php-client/63375165338d074d9b54a076977b489a6d913d2b/images/stripe-video.gif)](https://raw.githubusercontent.com/webshotapi/php-client/63375165338d074d9b54a076977b489a6d913d2b/images/stripe-video.gif)

Link to example mp4: https://github.com/webshotapi/php-client/raw/c77cb5a3d84b58a2dfd92ba30ed6850f83d7a52e/images/stripe-video.mp4

```python
from webshotapi import Client
import os

if __name__ == "__main__":
    try:
        TOKEN = os.getenv('WEBSHOTAPI_KEY','YOUR TOKEN HERE')
        client = Client(TOKEN)

        result = client.video({
            'url': 'https://www.stripe.com',
            'remove_modals': True,
            'scrolling_enable': True,
            'scrolling_algorithm': "ease_in_quad",
            'scrolling_scroll_delay': 500,
            'scrolling_scroll_distance': 1000,
            'scrolling_scroll_duration': 1500,
        })

        if result.save('/tmp/testa.mp4'):
            print("File saved")
        else:
            print("Error with save file")

    except Exception as e:
        print("Error:")
        print(e)
```

### Take screenshot and save jpg to file
```python
from webshotapi import Client
import os

if __name__ == "__main__":
    try:
        TOKEN = os.getenv('WEBSHOTAPI_KEY','YOUR TOKEN HERE')
        client = Client(TOKEN)
        
        result = client.screenshot({
             'url': 'https://www.example.com',
             'remove_modals': True
        })

        if result.save('/tmp/testa.jpg'):
            print("File saved")
        else:
            print("Error with save file")

    except Exception as e:
        print("Error:")
        print(e)
```

### Take screenshot and save PDF to file
You can convert your html page to PDF. For example you can prepare html invoice template and convert that website to PDF
```python
from webshotapi import Client
import os

if __name__ == "__main__":
    try:
        TOKEN = os.getenv('WEBSHOTAPI_KEY','YOUR TOKEN HERE')
        client = Client(TOKEN)
        
        result = client.pdf({ 
            'url': 'https://www.example.com'
        })

        if result.save('/tmp/test.pdf'):
            print("File saved")
        else:
            print("Error with save file")

    except Exception as e:
        print("Error:")
        print(e)
```

### Extract words map and HTML elements with css styles after rendering
Revolutionize your web development experience with our unparalleled software. Extract all selectors for HTML elements, complete with CSS styles, post-browser rendering. Furthermore, delve into the intricate details by extracting words along with their precise position data (x, y, width, height, offset from the previous word). This invaluable information allows you to construct a comprehensive words map of the entire website. Elevate your understanding and efficiency in website analysis and development like never before!
#### Sample script:
```python
from webshotapi import Client
import os

if __name__ == "__main__":
    try:
        TOKEN = os.getenv('WEBSHOTAPI_KEY','YOUR TOKEN HERE')
        client = Client(TOKEN)

        #send request
        result = client.extract({
            'url': 'https://www.example.com',
            'extract_elements': True,
            'extract_style': 1,
            'extract_words': True,
            'extract_html': True,
            'extract_text': True
        })
        
        #print json data from result
        print(result)
        print(result['html'])

    except Exception as e:
        print("Error:")
        print(e)
```
#### Results

```json
{
 "elements": [
      {
         "xpath": "/html[1]",
         "css_selector": "html",
         "x": 0,
         "y": 0,
         "width": 1920,
         "height": 413,
         "style": {
            "visibility": "visible",
            "display": "block",
            "fontWeight": "400",
            "backgroundImage": "none",
            "backgroundColor": "rgba(0, 0, 0, 0)",
            "cursor": "auto",
            "fontSize": "16px",
            "color": "rgb(0, 0, 0)",
            "position": "static",
            "textDecoration": "none solid rgb(0, 0, 0)",
            "textDecorationLine": "none",
            "textDecorationColor": "rgb(0, 0, 0)",
            "textDecorationStyle": "solid",
            "textDecorationThickness": "auto",
            "bottom": "auto",
            "top": "auto",
            "left": "auto",
            "right": "auto",
            "zIndex": "auto",
            "opacity": "1",
            "backgroundRepeat": "repeat",
            "borderWidth": "0px",
            "textAlign": "start",
            "marginLeft": "0px",
            "marginRight": "0px",
            "marginTop": "0px",
            "marginBottom": "0px",
            "paddingLeft": "0px",
            "paddingRight": "0px",
            "paddingTop": "0px",
            "paddingBottom": "0px",
            "overflow": "visible",
            "textIndent": "0px",
            "textTransform": "none",
            "letterSpacing": "normal",
            "fontFamily": "\"Times New Roman\""
         },
         "attributes": {}
      }
  ],
  "words": [
     {
         "word": "permission.",
         "position": {
            "x": 660,
            "y": 231,
            "width": 92,
            "height": 19
         },
         "word_index": 26,
         "xpath": "/html[1]/body[1]/div[1]/p[1]",
         "offset": 145
      }
  ],
  "page_properties": {
      "viewport": {
         "width": 1920,
         "height": 1080
      },
      "document": {
         "width": 1920,
         "height": 1080
      }
   },
  "html": "<!doctype html><html lang='en' dir='ltr'><head><base hr...",
  "text": "Welcome in our page\nToday is Monday...",
  "screenshot_url": "https://api.webshotapi.com/v1/screenshot/?token=....&width=1920&height=960",
  "status_code": 200
}

```

## API docs
Full documentation about our api you can find in this website [API DOCS](https://webshotapi.com/docs/sdk/python/)

## About our service
You can use our service with free plan with 100 free requests 

## License
[MIT](https://choosealicense.com/licenses/mit/)