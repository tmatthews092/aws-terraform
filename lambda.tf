# ----------------------------------------------------------------------------------------------------------------------
# DEPLOY THE LAMBDA FUNCTION, TRIGGER AND CLOUDWATCH LOG GROUP
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
  filename      = var.lambda_zip_file_name
  function_name = var.lambda_function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "main.lambda_handler"
  source_code_hash = data.archive_file.lambda.output_base64sha256
  runtime = "python3.10"

  environment {
    variables = {
      SUBSTRING_TO_SEARCH = var.substring_to_search
    }
  }
}

# Adding S3 bucket as trigger to my lambda and giving permissions
resource "aws_s3_bucket_notification" "aws_lambda_trigger" {
  bucket = var.aws_s3_bucket_name
  lambda_function {
    lambda_function_arn = aws_lambda_function.test_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".fasta"
  }
    depends_on = [aws_lambda_permission.allow_bucket]
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}
