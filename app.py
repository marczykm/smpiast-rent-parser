import sys
import requests
import getopt
from lxml import html
from pushbullet import Pushbullet

def usage():
	print 'app.py -u <username> -p <password>'

def main(argv):
	username = None
	password = None

	try:
		opts, args = getopt.getopt(argv, "hu:p:", ["username=","password="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ('-u', '--username'):
			username = arg
		elif opt in ('-p', '--password'):
			password = arg

	if len(sys.argv) < 4:
		usage()
		sys.exit(2)

	session_requests = requests.session()
	login_url = "https://www.smpiast.com.pl"

	payload = {
		"username": username,
		"password": password,
		"login": "Zaloguj"
	}

	session_requests.post(
		login_url,
		data = payload,
		headers = dict(referer=login_url)
	)

	url = "https://www.smpiast.com.pl/ebom/saldo/"
	result = session_requests.get(
		url,
		headers = dict(referer=url)
	)

	tree = html.fromstring(result.content)

	last_summary_raw = tree.xpath("//table[@class='balance_table table']/tr[2]/td/text()")

	last_summary = dict(
		date=last_summary_raw[0],
		title=last_summary_raw[1],
		calculation=last_summary_raw[2],
		payment=last_summary_raw[3],
		balance=last_summary_raw[4]
	)

	try:
		f = open('last_title', 'r+')
	except IOError:
		print 'no file'
		f = open('last_title', 'w+')

	got_new = f.readline().strip()!=last_summary['title'].strip() 
	if got_new:
		# send notification
		pb_file = open('pb_api_key', 'r')
		pb_api_key = pb_file.read()
		pb_file.close()
		pb = Pushbullet(pb_api_key)
		pb.push_note("SM Piast", 'Tytul: ' + last_summary['title'] + '\n' + 'Saldo: ' + last_summary['balance'])
		f.close()
		f = open('last_title', 'w+')
		f.write(last_summary['title'])
	f.close()

	print('Downloaded last summary:')
	print(last_summary)

if __name__ == "__main__":
	main(sys.argv[1:])