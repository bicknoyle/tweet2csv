#! /usr/bin/env python

import argparse, csv, codecs, cStringIO, json, sys, time, urllib, urllib2

# From: http://docs.python.org/library/csv.html
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

parser = argparse.ArgumentParser(description="Query the twitter search API")
parser.add_argument('query', metavar='QUERY')
parser.add_argument('-c', '--columns', nargs='+', default=['id_str', 'from_user', 'created_at', 'text'])
parser.add_argument('-d', '--delay', type=int)


options = parser.parse_args()

out_csv = UnicodeWriter(sys.stdout)

params = {
  'q' : options.query,
  'rpp' : 100, #max allowed by Twitter API
  'result_type' : 'recent'
}
qs = '?' + urllib.urlencode(params)
api_url = 'https://search.twitter.com/search.json'

while True:
    try:
      response = urllib2.urlopen(api_url+qs)
    except urllib2.HTTPError as e:
      sys.stderr.write('Exception when fetching url: ' + str(e))
      sys.exit(1)

    data = json.loads(response.read())
    if 'results' in data:
        for tweet in data['results']:
            try:
                out_csv.writerow([tweet[column] for column in options.columns])
            except KeyError as e:
                print "Column %s doesn't seem to exist!" % (str(e))
                sys.exit(1)

    if 'next_page' in data:
        qs = data['next_page']
        if options.delay:
            time.sleep(options.delay)
    else:
        break
