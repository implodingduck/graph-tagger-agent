variable "subscription_id" {
  type = string
  sensitive = true
}

variable "location" {
  type    = string
  default = "East US"
}

variable "gh_repo" {
  type = string
}

variable "graph_tenant_id" {
  type = string
  sensitive = true
}

variable "graph_client_id" {
  type = string
  sensitive = true
}

variable "graph_client_secret" {
  type = string
  sensitive = true  
}

variable "graph_dl_id" {
  type = string
  sensitive = true
}
