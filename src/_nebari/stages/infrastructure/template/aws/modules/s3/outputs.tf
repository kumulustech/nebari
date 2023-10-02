output "credentials" {
  description = "Important credentials for connecting to S3 bucket"
  value = {
    bucket             = aws_s3_bucket_versioning.main.bucket
    bucket_domain_name = aws_s3_bucket_versioning.main.bucket_domain_name
    arn                = aws_s3_bucket_versioning.main.arn
  }
}
