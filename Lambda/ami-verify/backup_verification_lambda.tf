data "archive_file" "init" {
  type        = "zip"
  source_dir = "${path.module}/ami-backup-verify"
  output_path = "${path.module}/files/ami_backup_verify.zip"
}

resource "aws_lambda_function" "ami_backup" {
    filename = "files/ami_backup_verify.zip"
    function_name = "ami_backup_verify"
    role = "${aws_iam_role.ami-backup-verify-lambda.arn}"
    handler = "ami_backup.handler"
    runtime = "python2.7"
    timeout = 300
    source_code_hash = "${base64sha256(file("files/ami_backup_verify.zip"))}"
}

resource "aws_cloudwatch_event_rule" "everyday_at_23" {
    name = "everyday-at-23-ami-backup-verify"
    description = "Fires everyday at 23:00 IST"
    schedule_expression = "cron(30 17 * * ? *)"
}

resource "aws_cloudwatch_event_target" "everyday_at_23_target" {
    rule = "${aws_cloudwatch_event_rule.everyday_at_23.name}"
    target_id = "ami_backup_verify"
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
    source_arn = "${aws_cloudwatch_event_rule.everyday_at_23.arn}"
}
