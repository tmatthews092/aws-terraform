# ----------------------------------------------------------------------------------------------------------------------
# PROVIDER CONFIGURATION
# ----------------------------------------------------------------------------------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-east-2"
}

# ----------------------------------------------------------------------------------------------------------------------
# CREATE A ZIP ARCHIVE FROM SOURCES
# ----------------------------------------------------------------------------------------------------------------------

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "python/main.py"
  output_path = "lambda_function_payload.zip"
}

# ----------------------------------------------------------------------------------------------------------------------
# CREATE A S3 BUCKET
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_s3_bucket" "bucket" {
  bucket = "aws-terraform-s3-generic-file-collector"

  tags = {
    Name        = "Generic File Collector"
    Environment = "Dev"
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# CREATE THE LAMBDA FUNCTION
# ----------------------------------------------------------------------------------------------------------------------

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.test_lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

resource "aws_lambda_function" "test_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = "lambda_function_payload.zip"
  function_name = "fastaFileParser"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "main.lambda_handler"
  source_code_hash = data.archive_file.lambda.output_base64sha256
  runtime = "python3.10"

  environment {
    variables = {
      foo = "bar"
    }
  }
}

# Adding S3 bucket as trigger to my lambda and giving the permissions
resource "aws_s3_bucket_notification" "aws_lambda_trigger" {
  bucket = "aws-terraform-s3-generic-file-collector"
  lambda_function {
    lambda_function_arn = aws_lambda_function.test_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".fasta"
  }
    depends_on = [aws_lambda_permission.allow_bucket]
}

# ----------------------------------------------------------------------------------------------------------------------
# CREATE AN IAM ROLE THAT WILL BE ATTACHED TO THE LAMBDA FUNCTION
# ----------------------------------------------------------------------------------------------------------------------

# AWS ROLE
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# CloudWatch
resource "aws_iam_policy" "fasta_file_parser_logging_policy" {
  name   = "fasta-file-parser-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:*"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# S3 Policy
resource "aws_iam_policy" "s3_policy" {
  name   = "s3-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "s3:*"
        ],
        Effect : "Allow",
        "Resource": "arn:aws:s3:::*"
      }
    ]
  })
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  managed_policy_arns = [
    aws_iam_policy.fasta_file_parser_logging_policy.arn, 
    aws_iam_policy.s3_policy.arn
  ]
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/fastaFileParser"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}
