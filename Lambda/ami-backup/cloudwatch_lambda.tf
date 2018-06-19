data "archive_file" "init" {
  type        = "zip"
  source_dir = "${path.module}/ami-backup"
  output_path = "${path.module}/files/ami_backup.zip"
}

resource "aws_lambda_function" "ami_backup" {
    filename = "files/ami_backup.zip"
    function_name = "ami_backup"
    role = "${aws_iam_role.ami-backup-lambda.arn}"
    handler = "ami_backup.handler"
    runtime = "python2.7"
    timeout = 300
    source_code_hash = "${base64sha256(file("files/ami_backup.zip"))}"
}

resource "aws_cloudwatch_event_rule" "everyday_at_22" {
    name = "everyday-at-22"
    description = "Fires everyday at 22:00 IST"
    schedule_expression = "cron(30 16 * * ? *)"
}

resource "aws_cloudwatch_event_target" "everyday_at_22_target" {
    rule = "${aws_cloudwatch_event_rule.everyday_at_22.name}"
    target_id = "ami_backup"
    arn = "${aws_lambda_function.ami_backup.arn}"
    input = <<EOF
{
  "config_file": "backup.json"
}
EOF
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_ami_backup" {
    statement_id = "AllowBackupExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.ami_backup.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.everyday_at_22.arn}"
}
