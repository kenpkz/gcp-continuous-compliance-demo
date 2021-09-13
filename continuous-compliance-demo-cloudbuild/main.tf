terraform {
  backend "gcs" {
    bucket = "zken-tfstate"
    prefix = "env/dev"
  }
}

provider "google" {
  project = "${var.project}"
  region = "${var.region}"
}
