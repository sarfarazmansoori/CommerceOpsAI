variable "aws_region" {
  description = "AWS region for CommerceOpsAI infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "allowed_api_cidr" {
  description = "Public IP CIDR allowed to access the CommerceOpsAI API"
  type        = string
}
