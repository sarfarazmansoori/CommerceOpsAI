# Security group for the CommerceOpsAI API
resource "aws_security_group" "api" {
  name        = "commerceops-api-sg"
  description = "Restricted security group for CommerceOpsAI API"
  vpc_id      = aws_vpc.main.id

  # Allow API traffic only from the developer's public IP
  ingress {
    description = "Allow API access from developer IP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["223.238.161.238/32"]
  }

  # Allow outbound traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "commerceops-api-sg"
    Environment = "development"
  }
}
