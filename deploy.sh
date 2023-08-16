#!/bin/bash

cp -r static ~russ/hanover/.
cp -r templates ~russ/hanover/.
cp *.py ~russ/hanover/.
chown -R russ:russ ~russ/hanover/

systemctl restart flipdot
systemctl restart web.service
