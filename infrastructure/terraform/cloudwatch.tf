# CloudWatch log group for CommerceOpsAI
resource "aws_cloudwatch_log_group" "commerceops" {
  name              = "/commerceops/api"
  retention_in_days = 7

  tags = {
    Name        = "commerceops-api-logs"
    Environment = "development"
    Project     = "CommerceOpsAI"
  }
}
