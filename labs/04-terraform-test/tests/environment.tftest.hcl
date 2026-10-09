run "normalizes_case" {
  command = plan

  variables {
    environment = "DEV"
  }

  assert {
    condition     = output.normalized_environment == "dev"
    error_message = "The environment should be lowercase."
  }
}

run "rejects_invalid_environment" {
  command = plan

  variables {
    environment = "staging"
  }

  expect_failures = [var.environment]
}
