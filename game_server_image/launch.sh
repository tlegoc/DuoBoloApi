#!/bin/bash

while true; do { echo -e 'HTTP/1.1 200 OK\r\n'; echo 'ok'; } | nc -l -p 8080; done &

./DuoBoloEngine