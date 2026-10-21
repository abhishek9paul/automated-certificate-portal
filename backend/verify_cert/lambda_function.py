import json
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'Certificates'

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters') or {}
        cert_id = query_params.get('id')

        if not cert_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Query parameter 'id' is required"})
            }

        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={'cert_id': cert_id})

        if 'Item' in response:
            item = response['Item']
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "VALID",
                    "cert_id": item['cert_id'],
                    "recipient_name": item['name'],
                    "course": item['course'],
                    "date_issued": item['date_issued'],
                    "certificate_url": item['s3_url'],
                    "sha256_hash": item['sha256_hash']
                })
            }
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "INVALID",
                    "message": "Certificate ID not found or has been revoked."
                })
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }