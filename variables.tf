variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "aws_s3_bucket_name" {
  description = "AWS S3 Bucket Name"
  type        = string
  default     = "aws-terraform-s3-fasta-file-collector"
}

variable "lambda_zip_file_name" {
  description = "Lambda Zip File Name"
  type        = string
  default     = "lambda_function_payload.zip"
}

variable "lambda_function_name" {
  description = "Lambda Function Name"
  type        = string
  default     = "fastaFileParser"
}

variable "substring_to_search" {
  description = "Substring to search for in Lambda Function"
  type        = string
  default     = "AACGCT"
}
