import json
import os
import hashlib

import boto3
client = boto3.client('s3')

if __name__ == '__main__':
    
    for source_dir in ('youtube', 'youku'):
        for v in os.listdir(source_dir):
            m = hashlib.sha1()
            m.update(v.encode('utf8'))
            fn = m.hexdigest()+'.json'
            
            if os.path.exists('transcriptions/{}'.format(fn)):
                with open('transcriptions/{}'.format(fn)) as fd:
                    data = json.load(fd)
                    text = data['results']['transcripts'][0]['transcript']
                    lang = data['results']['language_code'][:2]

                    if lang not in ('ar', 'it', 'es', 'de', 'fr', 'en', 'zh'):
                        print("skipping {} because lang {} is not supported yet for rolex".format(v, lang))

                    # Grab S3 object.
                    obj = client.get_object(Bucket='repustate-rolex', Key=v)
                    metadata = obj['Metadata']

                    if 'youtube' == source_dir:
                        source = 'YouTube'
                        weight_args = {
                            'source':'youtube',
                            'comments':metadata['comments'],
                            'views':metadata['views'],
                        }
                    else:
                        source = 'Youku'
                        weight_args = {
                            'source':'youku',
                            'comments':metadata['comments'],
                        }

                    post_data = {
                        'text':text,
                        'lang':lang,
                        'url':metadata['url'],
                        'date':metadata['date'],
                        'source':source,
                        'weight_args':json.dumps(weight_args),
                    }
                    
                    requests.post('https://dashboard.repustate.com/add-data/3155/', post_data)
