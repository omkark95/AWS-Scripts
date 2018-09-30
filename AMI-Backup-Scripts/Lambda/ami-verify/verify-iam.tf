resource "aws_iam_role" "ami-backup-verify-lambda" {
    name = "ami-backup-verify-lambda"
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

data "aws_iam_policy_document" "ec2-s3-ses-access-policy-doc" {
    statement =[{
        actions = [
            "ec2:Describe*",
            "ec2:Create*",
            "ses:*"
        ]
        resources = [
            "*"
        ]
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "${var.bucket}"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "${var.bucket}"
    }
    ]
}

resource "aws_iam_policy" "ec2-s3-ses-access-policy" {
    name = "ec2-verify-access-policy"
    path = "/"
    policy = "${data.aws_iam_policy_document.ec2-s3-ses-access-policy-doc.json}"
}

resource "aws_iam_role_policy_attachment" "policy-attachment" {
    role       = "${aws_iam_role.ami-backup-verify-lambda.name}"
    policy_arn = "${aws_iam_policy.ec2-s3-ses-access-policy.arn}"
}
