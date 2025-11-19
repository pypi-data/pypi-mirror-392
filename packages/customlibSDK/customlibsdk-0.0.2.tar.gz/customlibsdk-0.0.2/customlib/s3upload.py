import boto3
from botocore.exceptions import ClientError

def uploadPolicyToS3(
    
    policy_id:str,
    policy_file:bytes,
    bucket_name:str,
    region_name:str,
    content_type:str= 'application/pdf'
) -> bool :
  
  # policy_file is the policy document

  s3Client = boto3.client('s3',region_name=region_name)

  s3_key = f"policy_{policy_id}.pdf"
  
  try:
    s3Client.put_object(
      Bucket = bucket_name,
      Key = s3_key,
      Body = policy_file,
      Content_typ = content_type
    )
    
    print(f"Policy {policy_id} is successfully uploaded to S3 {bucket_name} bucket")
    
    return True
  except ClientError as e:
    print("Error in uploading document ",e)
    return False
  except Exception as e:
     print ("Unexpected exception, Please try again", e)
     return False
