module "network" {
  source      = "../../modules/network"
  name_prefix = var.name_prefix
}

module "ecr" {
  source      = "../../modules/ecr"
  name_prefix = var.name_prefix
}

module "rds" {
  source                 = "../../modules/rds"
  name_prefix            = var.name_prefix
  private_subnet_ids     = module.network.private_subnet_ids
  vpc_security_group_ids = [module.network.rds_security_group_id]
}

module "frontend" {
  source      = "../../modules/frontend"
  name_prefix = var.name_prefix
}

locals {
  cors_allow_origins = join(",", compact([
    "https://${module.frontend.cloudfront_domain_name}",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
  ]))
}

module "apprunner" {
  source             = "../../modules/apprunner"
  name_prefix        = var.name_prefix
  ecr_repository_url = module.ecr.repository_url
  image_tag          = var.image_tag
  # Private subnets + NAT: connector ENIs need a route to the internet for SaaS APIs (Pinecone, OpenAI).
  vpc_connector_subnet_ids         = module.network.private_subnet_ids
  vpc_connector_security_group_ids = [module.network.apprunner_connector_security_group_id]

  container_environment = concat(
    [
      { name = "DATABASE_URL", value = module.rds.database_url },
      { name = "CORS_ALLOW_ORIGINS", value = local.cors_allow_origins },
      { name = "OPENAI_API_KEY", value = var.openai_api_key },
      { name = "PINECONE_API_KEY", value = var.pinecone_api_key },
      { name = "PINECONE_INDEX_NAME", value = var.pinecone_index_name },
      { name = "PINECONE_ENVIRONMENT", value = var.pinecone_environment },
      { name = "PINECONE_EMBEDDING_MODEL", value = var.pinecone_embedding_model },
      { name = "COMPETITOR_LIST", value = var.competitor_list },
      { name = "OPENAI_CHAT_MODEL", value = var.openai_chat_model },
      { name = "LANGSMITH_TRACING", value = var.langsmith_tracing },
      { name = "LANGSMITH_API_KEY", value = var.langsmith_api_key },
      { name = "LANGSMITH_PROJECT", value = var.langsmith_project },
    ],
    var.extra_environment,
  )
}
