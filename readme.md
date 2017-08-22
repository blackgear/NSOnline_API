# NSOnline API

- Login.py: get your session\_token with username and password
- NSOnline.py: NSOnline core api wrapper

# TODO

- [x] Login NSOnline with username and password
- [x] API https://app.splatoon2.nintendo.net/api/data/stages
- [x] API https://app.splatoon2.nintendo.net/api/festivals/active
- [x] API https://app.splatoon2.nintendo.net/api/schedules
- [x] API https://app.splatoon2.nintendo.net/api/records
- [x] API https://app.splatoon2.nintendo.net/api/timeline
- [x] API https://app.splatoon2.nintendo.net/api/onlineshop/merchandises
- [x] API https://app.splatoon2.nintendo.net/api/onlineshop/order
- [x] API https://app.splatoon2.nintendo.net/api/results

# Example
This example shows how to use NSOnline core api to get the last 50 game data.

	#!/usr/bin/env python
	# -*- coding: utf-8 -*-

	from NSOnline import Splatoon

	def main():
	    Session_token = ''
	    splatoon = Splatoon(Session_token)
	    print(splatoon.get_results())

	if __name__ == '__main__':
	    main()

## LICENSE

The MIT License

Copyright (c) 2017 Daniel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
