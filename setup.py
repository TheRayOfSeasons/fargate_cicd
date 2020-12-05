import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="fargate_cicd",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "fargate_cicd"},
    packages=setuptools.find_packages(where="fargate_cicd"),

    install_requires=[
        "aws-cdk.core==1.76.0",
        "aws-cdk.aws-cloudformation==1.76.0",
        "aws-cdk.aws-codebuild==1.76.0",
        "aws-cdk.aws-codedeploy==1.76.0",
        "aws-cdk.aws-codepipeline==1.76.0",
        "aws-cdk.aws-codepipeline-actions==1.76.0",
        "aws-cdk.aws-ec2==1.76.0",
        "aws-cdk.aws-ecr==1.76.0",
        "aws-cdk.aws_ecs==1.76.0",
        "aws-cdk.aws_elasticloadbalancingv2==1.76.0",
        "aws-cdk.aws-iam==1.76.0",
        "aws-cdk.aws-rds==1.76.0",
        "aws-cdk.aws-route53==1.76.0",
        "aws-cdk.aws-s3==1.76.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
