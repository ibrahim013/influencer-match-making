# Trust for pulling images from ECR
data "aws_iam_policy_document" "apprunner_access_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "access" {
  name               = "${var.name_prefix}-apprunner-access"
  assume_role_policy = data.aws_iam_policy_document.apprunner_access_assume.json

  tags = {
    Name = "${var.name_prefix}-apprunner-access"
  }
}

resource "aws_iam_role_policy_attachment" "access_ecr" {
  role       = aws_iam_role.access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# Task role: optional but needed if referenced; some accounts require a role for VPC egress
data "aws_iam_policy_document" "apprunner_instance_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["tasks.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "instance" {
  name               = "${var.name_prefix}-apprunner-instance"
  assume_role_policy = data.aws_iam_policy_document.apprunner_instance_assume.json

  tags = {
    Name = "${var.name_prefix}-apprunner-instance"
  }
}

resource "aws_apprunner_vpc_connector" "main" {
  vpc_connector_name = "${var.name_prefix}-connector"
  subnets            = var.vpc_connector_subnet_ids
  security_groups    = var.vpc_connector_security_group_ids
}

locals {
  environment_map = { for e in var.container_environment : e.name => e.value }
}

resource "aws_apprunner_service" "api" {
  service_name = "${var.name_prefix}-api"

  source_configuration {
    auto_deployments_enabled = false
    image_repository {
      image_identifier      = "${var.ecr_repository_url}:${var.image_tag}"
      image_repository_type = "ECR"
      image_configuration {
        port                          = "8000"
        runtime_environment_variables = local.environment_map
      }
    }
    authentication_configuration {
      access_role_arn = aws_iam_role.access.arn
    }
  }

  instance_configuration {
    instance_role_arn = aws_iam_role.instance.arn
    cpu               = "0.25 vCPU"
    memory            = "0.5 GB"
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/healthz"
    interval            = 20
    timeout             = 10
    healthy_threshold   = 1
    unhealthy_threshold = 3
  }

  network_configuration {
    ingress_configuration {
      is_publicly_accessible = true
    }
    egress_configuration {
      egress_type       = "VPC"
      vpc_connector_arn = aws_apprunner_vpc_connector.main.arn
    }
  }

  tags = {
    Name = "${var.name_prefix}-apprunner"
  }
}
