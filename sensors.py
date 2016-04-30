from flask import Flask, request, render_template
import serial
import datetime

app = Flask(__name__)
app.debug = False

@app.route("/")
def read_sensors():

  # reading data from the arduino through USB/Serial interface
  ser = serial.Serial('/dev/ttyACM0', 9600)
  ser.readline()
  str=ser.readline()
  ser.close()
  str_split = str.split(';')
  humidity = float(str_split[0])
  temp     = float(str_split[1])
  heat_idx = float(str_split[2])
  lux      = float(str_split[3])
  cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # rendering the page
  return render_template('sensors.html', temperature = temp, humidity = humidity,
                         heat_idx = heat_idx, luminosity = lux, cur_time = cur_time)

@app.route("/history", methods=['GET'])
def read_db():

  temperatures, humidities, heat_idx, luminosities, from_date_str, to_date_str = get_records()
  
  # rendering the page
  return render_template('sensors_history.html', temperatures = temperatures,
                         heat_index = heat_idx, humidities = humidities,
                         luminosities = luminosities,
                         temperatures_items = len(temperatures),
                         humidities_items = len(humidities),
                         heat_index_items = len(heat_idx),
                         luminosities_items = len(luminosities),
                         from_date = from_date_str, to_date = to_date_str)

def validate_date(a_date):
  try:
    datetime.datetime.strptime(a_date, '%Y-%m-%d %H:%M')
    return True
  except ValueError:
    try:
      datetime.datetime.strptime(a_date, '%Y-%m-%d')
      return True
    except ValueError:
      return False
    return False

def get_records():

  import sqlite3

  # get the from date value from the URL, if not provided take the current date at 00:00
  from_date_str = request.args.get('from', datetime.datetime.now().strftime('%Y-%m-%d 00:00'))
  # ... validate the date before sending it to the database
  if not validate_date(from_date_str):
    from_date_str = datetime.datetime.now().strftime('%Y-%m-%d 00:00')

  # get the to date value from the URL, if not provided take the current date at 00:00
  to_date_str = request.args.get('to', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
  # ... validate the date before sending it to the database
  if not validate_date(to_date_str):
    to_date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

  # getting the date from/to using the radio buttons
  # ... getting a string
  range_h_form = request.args.get('range_h','')
  # ... convert to int
  range_h_int = "nan"
  try:
    range_h_int = int(range_h_form)
  except:
    print "range_h_form not a number"

  # if range_h is defined, we use it instead of the from/to_date_str
  if isinstance(range_h_int, int):
    time_now = datetime.datetime.now()
    time_from = time_now - datetime.timedelta(hours = range_h_int)
    time_to = time_now
    from_date_str = time_from.strftime('%Y-%m-%d %H:%M')
    to_date_str = time_to.strftime('%Y-%m-%d %H:%M')
    if app.debug == True:
      print range_h_int
      print from_date_str
      print to_date_str

  # connect to database
  conn = sqlite3.connect('/var/www/sensors/sensors.db')
  curs = conn.cursor()

  curs.execute("SELECT * FROM temperatures WHERE date_time BETWEEN ? and ?", (from_date_str, to_date_str))
  temperatures = curs.fetchall()

  curs.execute("SELECT * FROM humidities WHERE date_time BETWEEN ? and ?", (from_date_str, to_date_str))
  humidities = curs.fetchall()

  curs.execute("SELECT * FROM heat_index WHERE date_time BETWEEN ? and ?", (from_date_str, to_date_str))
  heat_idx = curs.fetchall()

  curs.execute("SELECT * FROM luminosity WHERE date_time BETWEEN ? and ?", (from_date_str, to_date_str))
  luminosities = curs.fetchall()

  # closing the database connection
  conn.close()

  return [temperatures, humidities, heat_idx, luminosities, from_date_str, to_date_str]
  
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)

