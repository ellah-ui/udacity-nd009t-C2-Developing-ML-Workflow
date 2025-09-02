1.Classifier

import boto3
import json
import base64

# SageMaker runtime client
runtime = boto3.client("sagemaker-runtime")

# Replace with your endpoint name
ENDPOINT_NAME = "image-classification-2025-09-02-11-05-16-220"  

def lambda_handler(event, context):
    # Decode the base64 image
    image = base64.b64decode(event["image_data"])

    # Call the SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/x-image",
        Body=image
    )

    # Parse the predictions
    result = json.loads(response["Body"].read().decode("utf-8"))

    # Save results back into event
    event["inferences"] = result

    return event

2. Serial Image Data

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    A function to serialize target data from S3
    """
    # Pull key and bucket from the event
    key = event["s3_key"]
    bucket = event["s3_bucket"]

    # Download file to /tmp (only writable dir in Lambda)
    download_path = "/tmp/image.png"
    s3.download_file(bucket, key, download_path)

    # Read the file and encode it
    with open(download_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')  # ensure string

    # Add image data back into event
    event["image_data"] = image_data

    return {
        'statusCode': 200,
        'body': event
    }



3. Filter Lambda
import json

# Confidence threshold
THRESHOLD = 0.93

def lambda_handler(event, context):
    # Grab inferences from the event
    inferences = event["inferences"]

    # Check if any value exceeds the threshold
    meets_threshold = max(inferences) >= THRESHOLD

    if not meets_threshold:
        raise Exception(f"Confidence {max(inferences)} below threshold {THRESHOLD}")

    # If passes, return the event
    return event
