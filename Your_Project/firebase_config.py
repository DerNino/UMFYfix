import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Load Firebase credentials from Streamlit secrets
firebase_config = {
  "type": "service_account",
  "project_id": "umfy-29ddb",
  "private_key_id": "2dda4d0a53bcfe579296d793cc3570a92f29f483",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUjKlV/c+in9HY\nmMMcwlb097IfgPsEnNrC02QcXt3unCMlkZzQGdX/gibObvjqumCAsKcxzpp0KyvC\nDzdtoR4Y5X8qlUQWutbcoe52eB7gXM7vh6ABhKc0ACbYcyIv/waPt0hubz8TcX1r\nnrBrrLVaucaaLpn9cE1QNYwNcUCdAjKrOhCdgdj4ztlZfWTWFrrjcCSZBBitHukz\nUDuyTFl4gV9WTWAdGdbXSF4DJ02Vcu+CChrR4wIL4lCSdo/z5PAmeswgirLeTZmq\nO2cHvHIpeuGqfhgqzXx5m4L+ZUsl2j2k8wmxvl5rJCwmKAc0bidqqcCmLCaBsQPm\n/Qvj2R3tAgMBAAECggEAB2L6iqLyf7Ytw5+jrXBBIwZBbmKbWM6J7D/XDbgZQLkK\niwmIwCpWDfyv/E+KriAIFhjH/5Mz8qHbl6yVB4Jdp5mbL11jw4jqj+cMygmivhUE\nrzwnFIbpn42AYP6nTQwD4gKYUJwp3p15QfA5T+ldzT3z+7e52DSM4PerWAHGgj1w\nguLfHD/PyMcQ2heUiJ9qgSkl0mch1DdHBLeHW0FnSrdzTaHJwpBlzEprGZ1ocLme\nQEyuJRIatlekSsLVESS0pTQoIYi9WnJ/rGA2igPauJstRclr4XiwS7eSs/NXiHcD\nbEezYZCBZy/eeYHFvGMn4/yePDaivMzw5WlGm6HH2wKBgQDEgWBJwA19VbqE3S9I\nUROhti9uPMFjyvbJpY0EUBD44MM6xpe+RzWXqxew5o7j8E304mUcSG2lU65NVdLN\njqLCaSb4vMFaWCnQUZCIWYqBIfuMoModXyvcG2vDrMYzJiQ8dIJxUAg7cAU7HKM3\nnuSEmCwTIFTok7i3BwLAoZEBgwKBgQDBhlieTsb7m9Z/GkyR1vZ3kYsbIVxI0NcF\nsj98WK4arotNeCYRJcHdAKCI+TSTvZIYQjiQyblAWh4z75slE5dtoCV9qEwY+IdO\noED1DQiGK6DBCrIo487XJ6POfceDDy7K+c7FWNtPI+wach9c/4E1b251uOLOeiN6\nNpJnDHd3zwKBgGyd2pxJVOt/dG62V8lQT1qmekcju/2uFYVWRcEphIgcrK0TUpLx\nh3UDNEAq4LargFuovBzLCBhHTeQfWTsX6W0udEUvCG0oqEwmmY5UeBNytjmAMtfT\nYEn0ujdZi+B/562m9OcvRq2b+Lg41xsKb+O+vTYBPA2mgYZhkKrrY1yDAoGAbBCN\nI7lxu8aFvGv/HeEfuBz5xKiYU8DqkS+767/JWPTmrNfOyfx/iN10x4gBKA7PqeQw\nmglK/PhVrUK7K7UI9hpbVRPJipgdVnZ+T1h7zhBGsAU8/0BWnCZyfjgWVMUBqC5e\nnCzGKicxDIN1qAS1LhWPZQVdAVeKwBABKLH5dFkCgYEArwdSxRa5EB5a9Z/noGur\nvcrLlAKt1X6H1FavA/tb9rJhwPO+PC1zdf/0WCmtdz18n9OjQ4gQS/bT+sgQUxe2\nfr/6WY4TnUFfBz7ayxjJ4LI4v1JIGEsGOq5TQaqtr9osvrONT+KnI/+3EtlR+vPM\nIsrtD3kukmFETNenqK/Vqlo=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-gbags@umfy-29ddb.iam.gserviceaccount.com",
  "client_id": "108101333756973147933",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-gbags%40umfy-29ddb.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

db = firestore.client()
