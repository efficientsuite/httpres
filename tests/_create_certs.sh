#!/usr/bin/env bash

echo "WARNING: THIS MAY FAIL WHEN RUNNING GIT BASH"

# Variables
PASSWORD="test"
SUBJ_CA="/C=CA/ST=BC/L=Vancouver/O=EfficientSuite/OU=EfficientSuite Root CA/CN=localhost"
SUBJ_SERVER_A="/C=CA/ST=BC/L=Vancouver/O=EfficientSuite/OU=EfficientSuite Server Certificate/CN=localhost"
SUBJ_CLIENT_B="/C=CA/ST=BC/L=Vancouver/O=EfficientSuite/OU=EfficientSuite Client Certificate/CN=httpResClient"

# Reset
rm -rf demoCA

# OpenSSL likes having this dir struct by default.
mkdir -p demoCA/private demoCA/intermediate demoCA/certs demoCA/newcerts

# Index File: This file keeps track of issued certificates.
touch demoCA/index.txt

# Serial File: Holds the next serial number to be used for new certs. Start with a value like 1000.
echo 1000 > demoCA/serial

# Create a private key and self signed ca cert
openssl genrsa -des3 -out demoCA/private/ca.key -passout pass:$PASSWORD 2048
openssl req -new -x509 -days 365 -key demoCA/private/ca.key -out demoCA/certs/ca.crt -passin pass:$PASSWORD -subj "$SUBJ_CA" -verbose

echo "Creating Client Certificates"

# Issue server certificate
openssl genrsa -des3 -out demoCA/private/server.key -passout pass:$PASSWORD 2048
openssl req -new -key demoCA/private/server.key -out demoCA/certs/server.csr -passin pass:$PASSWORD -subj "$SUBJ_SERVER_A" -verbose
openssl ca -batch -in demoCA/certs/server.csr -out demoCA/certs/server.crt -cert demoCA/certs/ca.crt -keyfile demoCA/private/ca.key -passin pass:$PASSWORD

# Issue client certificate
openssl genrsa -des3 -out demoCA/private/client.key -passout pass:$PASSWORD 2048
openssl req -new -key demoCA/private/client.key -out demoCA/certs/client.csr -passin pass:$PASSWORD -subj "$SUBJ_CLIENT_B" -verbose
openssl ca -batch -in demoCA/certs/client.csr -out demoCA/certs/client.crt -cert demoCA/certs/ca.crt -keyfile demoCA/private/ca.key -passin pass:$PASSWORD

echo "Certificates created successfully. Running server to test with. Use the following CURL command to test the server:"
echo "curl -k --cert demoCA/certs/server.crt --key demoCA/private/server.key https://localhost:3000"
