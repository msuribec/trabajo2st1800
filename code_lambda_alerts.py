# ref: https://docs.aws.amazon.com/code-library/latest/ug/python_3_kinesis_code_examples.html
# ref: https://docs.aws.amazon.com/code-library/latest/ug/python_3_kinesis_code_examples.html#serverless_examples

import base64
import json
import boto3
import decimal
import random


def send_sms(message):
    sns = boto3.client('sns')
    sns.publish(
        TopicArn="arn:aws:sns:us-east-1:637423430172:test-topic",
        Message=message
    )

def lambda_handler(event, context):
    item = None
    dynamo_db = boto3.resource('dynamodb')
    table = dynamo_db.Table('stockAlerts')
    decoded_record_data = [base64.b64decode(record['kinesis']['data']) for record in event['Records']]
    deserialized_data = [json.loads(decoded_record) for decoded_record in decoded_record_data]

    with table.batch_writer() as batch_writer:
        for item in deserialized_data:
            stockCode = item['StockCode']
            orderDate = item['InvoiceDate']
            quantity = item['Quantity']
            description = item['Description']
            unitPrice = item['UnitPrice']
            country = item['Country'].rstrip()

            alert_message = f"Alert: {stockCode} quantity is {quantity} at {unitPrice} USD."
            send_sms(alert_message)

            batch_writer.put_item(                        
                Item = {
                                'stockCode': stockCode,
                                'OrderDate': orderDate,
                                'Quantity': decimal.Decimal(str(quantity)),
                                'Description': description,
                                'UnitPrice': decimal.Decimal(str(unitPrice)),
                                'Country': country
                        }
            )