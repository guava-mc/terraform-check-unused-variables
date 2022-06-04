resource "aws_instance" "test" {
  ami           = "hi-mom"
  instance_type = "${var.one}-${aws_instance.test.ami}"

  tags = {
    Name = "ExampleAppServerInstance"
  }
}
