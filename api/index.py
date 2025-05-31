from flask import Flask
import os
from flask import request, jsonify
import aiohttp
import asyncio
import logging
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)

#UNWORKING COOKIES JUST FOR DEMO
# cookies = {
#     'ndut_fmt': 'C96770F2F5849984C2BA2A3F6284E3769F4147D175CD113DA30A8F2DE4CCD1FF',
#     'ndus': 'YvdD63MteHuiw0IgOC3Kdp-b5nahyIkzD_XdJDj2',
#     '__bid_n': '1900b9f02442253dfe4207',
#     '__stripe_mid': 'f5763c3a-0bc5-455f-8bbc-ef5a3a30f25d212bf2',
#     '__stripe_sid': '74502fe5-8572-4d7d-8171-6b47b1c5faf170be67',
#     'browserid': 'ujWfJR9sAO3NO7oCPbQ5IF_P6feJPiSxonWQoahA05CtJ1XhBmDy8oEXuDs=',
#     'csrfToken': 'X-KjyUF6Ezr5GVv53zbJSTeh',
#     'lang': 'en',
#     'PANWEB': '1'
# }


#WORKING COOKIES
# cookies = {
#     'PANWEB': '1',
#     'browserid': '45Cbkepkx0J0bqgQi1e1ubtbstmebahkYOYm3ZWuIktZFHaUuRjvdeeHz24=',
#     'lang': 'en',
#     '__bid_n': '196b885ed7339790814207',
#     'ndut_fmt': '26BE3C564003BEB97F4ED69DEBD9974F6291C708F2B2B419F0B6282675131E1C',
#     '__stripe_mid': '31fc92f3-a12a-480f-9e44-53f30f08258a75588e',
#     'ndus': 'YdZTyX1peHuimlux_D6dLGQBeHmj0r3M3trkunHB',
#     'csrfToken': 'C84Gc54sleTMoZxBx24k4SM7',
# }

cookies = {
    'PANWEB': '1',
    '__bid_n': '1900b9f02442253dfe4207',
    '__stripe_mid': 'b85d61d2-4812-4eeb-8e41-b1efb3fa2a002a54d5',
    'ndus': 'YylKpiCteHuiYEqq8n75Tb-JhCqmg0g4YMH03MYD',
    'csrfToken': '_CFePPJLR7i9z5IPx1cQydow',
    'browserid': '3y0kiWkfKhPHtg5J8dZFSYtwNzncsGY7n3JOtIJsdZ6Wo4XfJxNeA28UtIE=',
    'lang': 'en',
    'ndut_fmt': '3ABC40FE764692D905796B3BF93947ADFDC570385C17E3A68137C9D7451429E0',
    '__stripe_sid': 'b2997993-3227-4e11-a688-c355d62839c678db3c',
}

#WORKING COOKIES
# cookies = {
#     'PANWEB': '1',
#     'browserid': 'p4nVrnlkUVKcnbbJHnIClAhSL5uXs01e-0svx0bm7KHLUB6wIVvCUNGLIpU=',
#     'lang': 'en',
#     '__bid_n': '1900b9f02442253dfe4207',
#     'ndut_fmt': '5E7E5AFA065E159EF56CFE164FCF084C72B603BE3611911C28550443BDC08A4B',
#     '__stripe_mid': 'b85d61d2-4812-4eeb-8e41-b1efb3fa2a002a54d5',
#     'ndus': 'YylKpiCteHuiYEqq8n75Tb-JhCqmg0g4YMH03MYD',
#     'csrfToken': 'zAVdnQAVegC92-ah6pmLf6Dl',
# }


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': '*/*',
    'Connection': 'keep-alive',
}



def find_between(string, start, end):
  start_index = string.find(start) + len(start)
  end_index = string.find(end, start_index)
  return string[start_index:end_index]


async def fetch_download_link_async(url):
  try:
      async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
          async with session.get(url) as response1:
              response1.raise_for_status()
              response_data = await response1.text()
              js_token = find_between(response_data, 'fn%28%22', '%22%29')
              #print(js_token)
              log_id = find_between(response_data, 'dp-logid=', '&')
             # print(log_id)

              if not js_token or not log_id:
                  return None

              request_url = str(response1.url)
              surl = request_url.split('surl=')[1]
              params = {
                  'app_id': '250528',
                  'web': '1',
                  'channel': 'dubox',
                  'clienttype': '0',
                  'jsToken': js_token,
                  'dplogid': log_id,
                  'page': '1',
                  'num': '20',
                  'order': 'time',
                  'desc': '1',
                  'site_referer': request_url,
                  'shorturl': surl,
                  'root': '1'
              }

              async with session.get('https://www.1024tera.com/share/list', params=params) as response2:
                  response_data2 = await response2.json()
                #   print(response_data2)
                  #print("res2", response_data2)
                  if 'list' not in response_data2:
                      return None

                  if response_data2['list'][0]['isdir'] == "1":
                      params.update({
                          'dir': response_data2['list'][0]['path'],
                          'order': 'asc',
                          'by': 'name',
                          'dplogid': log_id
                      })
                      params.pop('desc')
                      params.pop('root')

                      async with session.get('https://www.1024tera.com/share/list', params=params) as response3:
                          response_data3 = await response3.json()
                        #   print(response_data3)
                          #print("res3", response_data3)
                          if 'list' not in response_data3:
                              return None
                          return response_data3['list']
                  #print(response_data2['list'])
                  return response_data2['list']
  except aiohttp.ClientResponseError as e:
      print(f"Error fetching download link: {e}")
      return None


def extract_thumbnail_dimensions(url: str) -> str:
    """Extract dimensions from thumbnail URL's size parameter"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    size_param = params.get('size', [''])[0]
    
    # Extract numbers from size format like c360_u270
    if size_param:
        parts = size_param.replace('c', '').split('_u')
        if len(parts) == 2:
            return f"{parts[0]}x{parts[1]}"
    return "original"


async def get_formatted_size_async(size_bytes):
  try:
      size_bytes = int(size_bytes)
      size = size_bytes / (1024 * 1024) if size_bytes >= 1024 * 1024 else (
          size_bytes / 1024 if size_bytes >= 1024 else size_bytes
      )
      unit = "MB" if size_bytes >= 1024 * 1024 else ("KB" if size_bytes >= 1024 else "bytes")

      return f"{size:.2f} {unit}"
  except Exception as e:
      print(f"Error getting formatted size: {e}")
      return None

async def format_message(link_data):
  # Process thumbnails
    thumbnails = {}
    if 'thumbs' in link_data:
        for key, url in link_data['thumbs'].items():
            if url:  # Skip empty URLs
                dimensions = extract_thumbnail_dimensions(url)
                thumbnails[dimensions] = url
#   if link_data
    file_name = link_data["server_filename"]
    file_size = await get_formatted_size_async(link_data["size"])
    download_link = link_data["dlink"]
    sk = {
      'Title': file_name,
      'Size': file_size,
      'Direct Download Link': download_link,
      'Thumbnails': thumbnails
    }
    return sk

@app.route('/')
def hello_world():
  #result = bot.get_me()
  response = {'status': 'success', 'message': 'Working Fully',' Contact': '@GuyXD'}
  return response


@app.route(rule='/api', methods=['GET'])
async def Api():
    try:
        url = request.args.get('url', 'No URL Provided')
        logging.info(f"Received request for URL: {url}")
        link_data = await fetch_download_link_async(url)
        
        if link_data:
            formatted_files = []
            for item in link_data:
                # Get the highest quality thumbnail (url3 is usually the highest)
                thumbnail = item.get("thumbs", {}).get("url3", "")
                if not thumbnail:
                    # Fallback to other thumbnail versions if url3 doesn't exist
                    thumbnail = next((v for k, v in item.get("thumbs", {}).items() if v), ""
                
                file_info = {
                    "file_name": item.get("server_filename"),
                    "download_link": item.get("dlink"),
                    "file_size": await get_formatted_size_async(item.get("size", 0)),
                    "thumbnail": thumbnail
                }
                formatted_files.append(file_info)
            
            response = {
                'status': 'success',
                'files': formatted_files
            }
        else:
            response = {'status': 'error', 'message': 'No files found', 'ShortLink': url}
            
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'Link': url})

@app.route(rule='/help', methods=['GET'])
async def help():
    try:
        response = {'Info': "There is Only one Way to Use This as Show Below",
                    'Example': 'https://teraboxx.vercel.app/api?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA',
                    'Example2': 'https://teraboxx.vercel.app/api2?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA'}
        return jsonify(response)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        response = {'Info': "There is Only one Way to Use This as Show Below",
                    'Example': 'https://teraboxx.vercel.app/api?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA',
                    'Example2': 'https://teraboxx.vercel.app/api2?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA'}
        return jsonify(response)




async def get_formatted_size_async(size_bytes):
    try:
        size_bytes = int(size_bytes)
        size = size_bytes / (1024 * 1024) if size_bytes >= 1024 * 1024 else (
            size_bytes / 1024 if size_bytes >= 1024 else size_bytes
        )
        unit = "MB" if size_bytes >= 1024 * 1024 else ("KB" if size_bytes >= 1024 else "bytes")
        return f"{size:.2f} {unit}"
    except Exception as e:
        print(f"Error getting formatted size: {e}")
        return None


async def fetch_download_link_async2(url):
    try:
        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            async with session.get(url) as response1:
                response1.raise_for_status()
                response_data = await response1.text()
                
                # Extract jsToken & logid
                js_token = find_between(response_data, 'fn%28%22', '%22%29')
                log_id = find_between(response_data, 'dp-logid=', '&')

                if not js_token or not log_id:
                    return None

                request_url = str(response1.url)
                print(request_url)
                surl = request_url.split('surl=')[1]
                print(surl)

                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': request_url,
                    'shorturl': surl,
                    'root': '1'
                }

                async with session.get('https://www.1024tera.com/share/list', params=params) as response2:
                    response_data2 = await response2.json()

                    if 'list' not in response_data2:
                        return None

                    files = response_data2['list']

                    # If it's a directory, fetch contents
                    if files[0]['isdir'] == "1":
                        params.update({
                            'dir': files[0]['path'],
                            'order': 'asc',
                            'by': 'name',
                            'dplogid': log_id
                        })
                        params.pop('desc')
                        params.pop('root')

                        async with session.get('https://www.1024tera.com/share/list', params=params) as response3:
                            response_data3 = await response3.json()
                            if 'list' not in response_data3:
                                return None
                            files = response_data3['list']

                    # Fetch direct download links for each file
                    file_data = []
                    for file in files:
                        async with session.head(file["dlink"], headers=headers) as direct_link_response:
                            direct_download_url = direct_link_response.headers.get("location")

                        file_info = {
                            "file_name": file.get("server_filename"),
                            "link": file.get("dlink"),
                            "direct_link": direct_download_url,  # Extracted direct download link
                            "thumb": file.get("thumbs", {}).get("url3", "https://default_thumbnail.png"),
                            "size": await get_formatted_size_async(file.get("size", 0)),
                            "sizebytes": file.get("size", 0),
                        }
                        file_data.append(file_info)

                    return file_data

    except aiohttp.ClientResponseError as e:
        print(f"Error fetching download link: {e}")
        return None



@app.route(rule='/api2', methods=['GET'])
async def Api2():
    try:
        url = request.args.get('url', 'No URL Provided')
        logging.info(f"Received request for URL: {url}")

        link_data = await fetch_download_link_async2(url)

        if link_data:
            # Transform the data to match the desired format
            formatted_files = []
            for file in link_data:
                formatted_files.append({
                    "file_name": file.get("file_name"),
                    "download_link": file.get("direct_link"),  # Using the direct download link
                    "file_size": file.get("size"),
                    "thumbnail": file.get("thumb")
                })
            
            response = {
                'status': 'success',
                'files': formatted_files
            }
        else:
            response = {'status': 'error', 'message': 'No files found', 'ShortLink': url}

        return jsonify(response)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'Link': url})


