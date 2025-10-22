# The configuration for the `remote` backend.
terraform {
  backend "remote" {
    # The name of your Terraform Cloud organization.
    organization = "disposable-org"

    # The name of the Terraform Cloud workspace to store Terraform state files in.
    workspaces {
      name = "hack-a-product-gemini"
    }
  }
}
