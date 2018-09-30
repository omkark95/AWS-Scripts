resource "aws_iam_role" "ami-backup-retention-lambda" {
    name = "ami-backup-retention-lambda"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "ec2-retention-policy-doc" {
    statement {
        actions = [
            "ec2:*"
        ]
        resources = [
            "*"
        ]
    }
}

resource "aws_iam_policy" "ec2-access-policy" {
    name = "ec2-backup-retention-access-policy"
    path = "/"
    policy = "${data.aws_iam_policy_document.ec2-retention-policy-doc.json}"
}

resource "aws_iam_role_policy_attachment" "policy-attachment" {
    role       = "${aws_iam_role.ami-backup-retention-lambda.name}"
    policy_arn = "${aws_iam_policy.ec2-access-policy.arn}"
}
