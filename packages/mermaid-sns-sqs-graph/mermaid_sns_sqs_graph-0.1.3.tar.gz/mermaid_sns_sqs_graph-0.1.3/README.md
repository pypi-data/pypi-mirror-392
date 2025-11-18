# Mermaid SNS SQS Graph

Generate clear, auto-generated Mermaid diagrams representing the relationships between **AWS SNS topics** and **SQS queues**.

## 📘 Overview

Mermaid SNS SQS Graph is a lightweight utility designed to help you visualize your AWS event-driven architecture. By scanning SNS topics and the SQS queues subscribed to them, this tool outputs a Mermaid diagram that clearly maps out message-flow relationships.

This is especially useful for:

* Understanding complex pub/sub architectures
* Documenting cloud infrastructure
* Troubleshooting message routing
* Onboarding new team members

## ✨ Features

* 🔍 Automatically discovers SNS → SQS connections
* 🖼️ Generates Mermaid-compliant graph syntax
* 📄 Easy to embed in docs, wikis, and architecture diagrams
* ⚡ Fast and AWS-native (uses AWS SDK)
* 🧩 Supports multiple subscriptions per topic
* 🔍 Automatically discovers SNS → SQS connections
* 🧵 Supports DLQ (Dead Letter Queue) mappings for SQS

## 🚀 Getting Started

Mermaid SNS SQS Graph is distributed as a **Python package**.

### 📦 Installation

### macOS

``` bash
pipx install mermaid-sns-sqs-graph
```

If you don't have **pipx** installed:

``` bash
brew install pipx
pipx ensurepath
source ~/.zshrc   # reload shell so pipx is available
```

### Windows

You can install using **pipx** or regular **pip**.

#### Using pipx (recommended):

1.  Install pipx (if not already installed):

    ``` powershell
    python -m pip install --user pipx
    pipx ensurepath
    ```

    Restart your terminal.

2.  Install the package:

    ``` powershell
    pipx install mermaid-sns-sqs-graph
    ```

#### Using pip:

``` powershell
pip install mermaid-sns-sqs-graph
```

------------------------------------------------------------------------

### 🔐 AWS Credentials Required

The utility requires valid AWS credentials with access to **SNS** and
**SQS**.

Ensure your AWS profile contains an **access key** and **secret key**:

``` bash
aws configure --profile default
```

Or replace `default` with a different profile name if needed.

# 🛠️ Usage

Once installed, run the tool from the command line:

``` bash
mermaid-sns-sqs-graph --region us-east-1 --profile default
```

This will scan all SNS → SQS connections in the specified AWS region and
output a Mermaid graph to your terminal.

Example output:

``` mermaid
graph TD;
  SNSTopicA --> SQSQueue1;
  SNSTopicA --> SQSQueue2;
  SNSTopicB --> SQSQueue3;
```

To save the graph into a file:

``` bash
mermaid-sns-sqs-graph --region us-east-1 --profile default --output architecture.md
```

------------------------------------------------------------------------

## ⚙️ Configuration Options

| Flag         | Required | Description |
|--------------|----------|-------------|
| `--region`   | Yes      | AWS region to query (e.g., `us-east-1`) |
| `--profile`  | Yes      | AWS CLI profile to use (must contain access key + secret key) |
| `--output`   | No       | Output Mermaid graph to a file instead of stdout |
| `--no_dlq`   | No       | Disable scanning of DLQ → Queue mappings |
| `--no_filters` | No     | Disable retrieving SNS subscription filter policies |
| `--sns_arn`  | No       | Query only a specific SNS topic ARN instead of all topics |


------------------------------------------------------------------------

## 🔍 Examples

### Generate the full graph for a region

``` bash
mermaid-sns-sqs-graph --region us-east-1 --profile prod
```

### Save output to a file

``` bash
mermaid-sns-sqs-graph --region us-west-2 --profile default --output infra_graph.md
```

### Disable DLQ mapping

``` bash
mermaid-sns-sqs-graph --region eu-central-1 --profile dev --no_dlq
```

### Disable SNS filter discovery

``` bash
mermaid-sns-sqs-graph --region ap-south-1 --profile default --no_filters
```

### Generate graph for a specific SNS topic

``` bash
mermaid-sns-sqs-graph --region us-east-1 --profile prod --sns_arn arn:aws:sns:us-east-1:123456789012:OrdersTopic
```
