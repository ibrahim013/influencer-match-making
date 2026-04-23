variable "name_prefix" {
  type = string
}

variable "price_class" {
  type        = string
  description = "CloudFront price class: PriceClass_All, PriceClass_200, PriceClass_100."
  default     = "PriceClass_100"
}
