# IAM role assumed by ECS tasks
resource "aws_iam_role" "ecs_task_execution" {
  name = "commerceops-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "commerceops-ecs-execution-role"
    Environment = "development"
  }
}

# Attach AWS-managed ECS task execution permissions
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role = aws_iam_role.ecs_task_execution.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM role assumed by the CommerceOpsAI application
resource "aws_iam_role" "ecs_task" {
  name = "commerceops-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "commerceops-ecs-task-role"
    Environment = "development"
  }
}

# Allow the application to write audit logs to its S3 bucket
resource "aws_iam_role_policy" "audit_s3_write" {
  name = "commerceops-audit-s3-write"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:PutObject"
        ]

        Resource = "${aws_s3_bucket.audit_logs.arn}/*"
      }
    ]
  })
}
