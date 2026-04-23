variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "alb_security_group_id" {
  type = string
}

variable "ecs_tasks_security_group_id" {
  type = string
}

variable "ecr_repository_url" {
  type = string
}

variable "image_tag" {
  type        = string
  description = "ECR image tag (e.g. git SHA)."
}

variable "container_environment" {
  type = list(object({
    name  = string
    value = string
  }))
  description = "Container environment variables (order preserved)."
  sensitive   = true
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "container_cpu" {
  type    = number
  default = 256
}

variable "container_memory" {
  type    = number
  default = 512
}
