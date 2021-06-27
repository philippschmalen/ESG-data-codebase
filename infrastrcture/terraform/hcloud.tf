# Please do `export HCLOUD_TOKEN=...` before terraform init and terraform apply

terraform {
  required_providers {
    hcloud = {
      source = "terraform-providers/hcloud"
    }
  }
  required_version = ">= 0.13"
}

provider "hcloud" {}

resource "hcloud_server" "web" {
  name = "demo-server"
  image = "ubuntu-18.04"
  server_type = "cx11"
}

resource "hcloud_volume" "storage" {
  name = "demo_volume"
  size = 50
  server_id = hcloud_server.web.id
  automount = true
  format = "ext4"
}
