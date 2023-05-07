"""
Lambda Function 1: serializeImageData
A lambda function that copies an object from S3, base64 encodes it, and 
then return it (serialized data) to the step function as `image_data` in an event.
"""

import json
import boto3
import base64

# A low-level client representing Amazon Simple Storage Service (S3)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input (You may also check lambda test)
    key = event['s3_key']                               ## TODO: fill in
    bucket = event['s3_bucket']                         ## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:          # Read binary file
        image_data = base64.b64encode(f.read())      # Base64 encode binary data ('image_data' -> class:bytes)

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    
   
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,      # Bytes data
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }






"""
ImageClassifier : Lambda function to predict image classification
"""
import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-05-06-11-50-56-463"
runtime = boto3.client("runtime.sagemaker")

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event["image_data"])

    # Instantiate a Predictor
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT,
                                    ContentType='image/png',
                                    Body=image) ## TODO: fill in
    # For this model the IdentitySerializer needs to be "image/png"
    #predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    inferences = json.loads(response['Body'].read().decode())

    # We return the data back to the Step Function
    event["inferences"] = inferences
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }


##filterInferences

import json

THRESHOLD = 0.93

class ThresholdConfidenceNotMetException(Exception):
    pass

def lambda_handler(event, context):
    # Grab the inferences from the event
    inferences = event['inferences'] 

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(x > THRESHOLD for x in inferences) 

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    # if meets_threshold:
    #     pass
    # else:
    #     raise ThresholdConfidenceNotMetException("Confidence score below threshold")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }