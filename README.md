# AWS Terraform Integration

Using Terraform we are using IaC principles to deploy a defined Python3 Lambda Function and an S3 Bucket

### Lambda Function

Uses a deployed trigger from main.tf to fire when a .fasta file is uploaded to the S3 bucket *aws-terraform-s3-generic-file-collector*

We use the .count function to determine all instances of a specified substring within the .fasta file. After counting we create a JSON file which is uploaded to the results folder in the S3 Bucket.

### TODO

- Improve security by obstracting access tokens
- Abstract out main.tf file and values
- Add parameterization for substring_to_search
- Improve error catching + reporting in Lambda function