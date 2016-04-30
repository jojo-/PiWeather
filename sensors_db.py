#!/usr/bin/env/python

import serial
import datetime
import sqlite3

def log_readings():

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

  conn = sqlite3.connect('/var/www/sensors/sensors.db')
  curs = conn.cursor()

  curs.execute("""INSERT INTO temperatures values((?), (?), (?))""",
               (cur_time, "dht22", temp))
  if humidity > 20:
    curs.execute("""INSERT INTO humidities values((?), (?), (?))""", 
                 (cur_time, "dht22", humidity))
  curs.execute("""INSERT INTO heat_index values((?), (?), (?))""", 
               (cur_time, "dht22", heat_idx))

  curs.execute("""INSERT INTO luminosity values((?), (?), (?))""", 
               (cur_time, "temt6000", lux))

  conn.commit()
  conn.close()

if __name__ == "__main__":
  log_readings()
