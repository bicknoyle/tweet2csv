# tweet2csv

#### tweet2csv is a script written in Python to query Twitter's search API and dump the results to a csv.

## Example Usage

To get a list tweets mentioning @user:

    $ python tweet2csv.py "@user" > output.csv

## Rate Limits

Twitter's search API only returns up to 100 results per request. The
script will attempt to make multiple requests in order to get all
possible results, but Twitter imposes a [rate limit](https://dev.twitter.com/docs/rate-limiting#search)
on requests. So, if you're seeing failures like:

    $ python tweet2csv.py "@ladygaga"
    .
    .
    .
    (really long list of results)
    .
    .
    Exception when fetching url: HTTP Error 403: Forbidden

Use the delay switch (-D, --delay) in order to add some delay between
requests to the API

## Resources

* [Using the Twitter Search API](https://dev.twitter.com/docs/using-search)
* [GET search](https://dev.twitter.com/docs/api/1/get/search)