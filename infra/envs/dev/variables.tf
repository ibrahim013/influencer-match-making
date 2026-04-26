variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "name_prefix" {
  type    = string
  default = "matchmaking-dev"
}

variable "image_tag" {
  type        = string
  description = "Backend image tag in ECR (e.g. git SHA or latest)."
  default     = "latest"
}

variable "openai_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "pinecone_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "pinecone_index_name" {
  type    = string
  default = "influencer-creators"
}

variable "pinecone_environment" {
  type    = string
  default = ""
}

variable "pinecone_embedding_model" {
  type    = string
  default = "llama-text-embed-v2"
}

variable "competitor_list" {
  type    = string
  default = "Nike,Adidas,Puma,Reebok"
}

variable "openai_chat_model" {
  type    = string
  default = "gpt-4o"
}

variable "langsmith_tracing" {
  type    = string
  default = "false"
}

variable "langsmith_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "langsmith_project" {
  type    = string
  default = "matchmaking"
}

variable "extra_environment" {
  type = list(object({
    name  = string
    value = string
  }))
  default   = []
  sensitive = false
}
