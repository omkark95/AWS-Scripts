data "archive_file" "init" {
  type        = "zip"
  source_dir = "${path.module}/ami-retention"
  output_path = "${path.module}/files/ami_retention.zip"
}

resource "aws_lambda_function" "ami_retention" {
    filename = "files/ami_retention.zip"
    function_name = "ami_retention"
    role = "${aws_iam_role.ami-backup-retention-lambda.arn}"
    handler = "ami_retention.handler"
    runtime = "python2.7"
    timeout = 300
    source_code_hash = "${base64sha256(file("files/ami_retention.zip"))}"
}

resource "aws_cloudwatch_event_rule" "everyday_at_23_30" {
    name = "everyday-at-23-30-ami-retention"
    description = "Fires everyday at 23:30 IST"
    schedule_expression = "cron(30 18 * * ? *)"
}

resource "aws_cloudwatch_event_target" "everyday_at_23_30_target" {
    rule = "${aws_cloudwatch_event_rule.everyday_at_23_30.name}"
    target_id = "ami_retention"
    arn = "${aws_lambda_function.ami_retention.arn}"
    input = <<EOF
{
  "config_file": "retention.json"
}
EOF
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_ami_retetion" {
    statement_id = "AllowRetentionExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.ami_retention.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.everyday_at_23_30.arn}"
}
