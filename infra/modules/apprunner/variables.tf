variable "name_prefix" {
  type = string
}

variable "ecr_repository_url" {
  type        = string
  description = "ECR repository URL without tag (e.g. 123.dkr.ecr.us-east-1.amazonaws.com/matchmaking-dev-backend)."
}

variable "image_tag" {
  type = string
}

variable "container_environment" {
  type = list(object({
    name  = string
    value = string
  }))
  sensitive = true
}

# Public subnets: connector ENIs need a route to the internet (OpenAI/Pinecone) without a NAT.
variable "vpc_connector_subnet_ids" {
  type        = list(string)
  description = "Subnets for the VPC connector (use public subnets when no NAT gateway)."
}

variable "vpc_connector_security_group_ids" {
  type = list(string)
}
