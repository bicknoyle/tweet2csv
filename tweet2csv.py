#! /usr/bin/env python

import argparse, csv, codecs, cStringIO, sys, tweepy

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
        # Some s in row might not have encode method!!!
        self.writer.writerow([s.encode("utf-8") if hasattr(s, 'encode') else s for s in row])
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

parser = argparse.ArgumentParser(description="Query the Twitter search API and output results as csv")
parser.add_argument('query', metavar='QUERY', help="Query to send to Twitter search API. See https://dev.twitter.com/docs/using-search for example queries")
parser.add_argument('-c', '--columns', nargs='+', default=['id_str', 'from_user', 'created_at', 'text'], help="Columns to display")

csv_group = parser.add_argument_group('CSV options', 'Options for creating the CSV file')
csv_group.add_argument('-d', '--delimiter', default=',')
csv_group.add_argument('-l', '--line-terminator', default='\r\n')

options = parser.parse_args()

out_csv = UnicodeWriter(sys.stdout, delimiter=options.delimiter.decode('string_escape'), lineterminator=options.line_terminator.decode('string_escape'))

out_csv.writerow(options.columns)

api = tweepy.API()
# tweepy.Cursor = pagination
for tweet in tweepy.Cursor(api.search, q=options.query, rpp=100, result_type='recent').items():
    try:
        out_csv.writerow([getattr(tweet, column) for column in options.columns])
    except AttributeError as e:
        sys.stderr.write(str(e))
        sys.exit(1)
