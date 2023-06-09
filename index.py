import boto3
import os
import aws_encryption_sdk
from aws_encryption_sdk.identifiers import CommitmentPolicy


def decryption(event, context):
    s3 = boto3.client('s3')

    # Set up to handle S3 Create Object Triggers
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    destination_key = 'decrypted/' + key

    client = aws_encryption_sdk.EncryptionSDKClient(
        commitment_policy=CommitmentPolicy.FORBID_ENCRYPT_ALLOW_DECRYPT
    )

    kms_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(
        key_ids=[os.environ['KMS_KEY']] # This is defined in template.yml. You can change it there
    )

    file_obj = s3.get_object(
        Bucket=bucket,
        Key=key
    )['Body']

    with client.stream(
        mode='d',
        source=file_obj,
        key_provider=kms_key_provider
    ) as decryptor:
        s3.upload_fileobj(decryptor, bucket, destination_key)

    print('File Decrypted Here:\nBucket: ' + bucket + '\nKey: ' + destination_key)
    return "success"