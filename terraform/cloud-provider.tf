terraform {
    required_providers{
        google ={
            source = "hashicorp/google"
            version = "~> 5.0"
        }
    }
}

provider "google"{
    project = "gen-lang-client-0189309103"
    region = "us-west2"
    zone = "us-west2-a"
}