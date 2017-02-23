#!/bin/bash

cd $STARDOG_HOME/bin
./stardog-admin server start --disable-security && ./stardog-admin db create -o reasoning.type=DL reasoning.sameas=FULL -n parlialytics 
