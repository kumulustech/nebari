output "credentials" {
  description = "Resources from terraform-state"
  value = {
    bucket_arn = aws_s3_bucket_versioning.terraform-state.arn
    dynamo_arn = aws_dynamodb_table.terraform-state-lock.arn
  }
}
