from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from .aws_helper import get_queue_dlq_arn, list_sns_topics , list_topic_subscriptions
from .mermaid_helper import format_filter_label, render_mermaid_diagram

import boto3

@dataclass
class CliArgs:
    region: str
    profile: Optional[str] = None
    output: Optional[str] = None
    no_filters: bool = False
    no_dlq: bool = False
    sns_arn: Optional[str] = None

def parse_args(argv=None) -> CliArgs:
    p = argparse.ArgumentParser(description="Render SNS->SQS connection as a Mermaid graph")
    p.add_argument("--region", required=True, help="AWS region to query")
    p.add_argument("--profile", required=True, help="AWS profile to use")
    p.add_argument("--output", help="Mermaid output file")
    p.add_argument("--no_dlq", help="Disable DLQ connections", default=False)
    p.add_argument("--no_filters", help="Disable all filters", default=False)
    p.add_argument("--sns_arn", help="Specify a specific SNS topic ARN", default=None)

    args = p.parse_args(argv)
    
    print("Generating Mermaid graph for SNS to SQS connections in region:", args.region)
    
    return CliArgs(
        region=args.region,
        profile=args.profile,
        output=args.output,
        no_dlq=args.no_dlq,
        no_filters=args.no_filters,
        sns_arn=args.sns_arn
    )
    
def main(argv=None):
    args = parse_args(argv)
    print("CLI OK — parsed params:")
    print(f" region: {args.region}")
    print(f" profile: {args.profile}")
    print(f" output: {args.output}")

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    sns = session.client("sns", region_name=args.region)
    sqs = session.client("sqs", region_name=args.region)
    

    print("fetching SNS topics...")
    topics = list_sns_topics(sns, topic_arn=args.sns_arn)
    edges: List[Tuple[str,str]] = []
    queue_qrns: Set[str] = set()
    
    print(f"found {len(topics)} topics")
    for t in topics:
        sqs_subs = list_topic_subscriptions(sns, t.arn, include_attributes=not args.no_filters)
        print(f" topic {t.arn} has {len(sqs_subs)} subscriptions")
        for s in sqs_subs:
            if (getattr(s, "protocol", "").lower() != "sqs") or (not s.endpoint):
                continue
            label = None
            if not args.no_filters:
                label = format_filter_label(getattr(s, "filter_policy", None))
            edges.append((t.arn, s.endpoint, label))
            queue_qrns.add(s.endpoint)
    
    # Get DLQ edges
    dlq_edges: List[Tuple[str,str]] = []
    if not args.no_dlq:
        print("fetching DLQ info for SQS queues...", queue_qrns)
        for qarn in sorted(queue_qrns):
            dlq_arn = get_queue_dlq_arn(sqs, qarn)
            print("DLQ for", qarn, "is", dlq_arn)
            if dlq_arn:
                dlq_edges.append((qarn, dlq_arn))
    else:
        print("Skipping DLQ edges as per CLI param")
        

    print(f"\n Topics: {topics}")
    print(f"\n Edges: {edges}")
    print(f"\n DLQ Edges: {dlq_edges}")
    # Render Mermaid diagram
    mermaid = render_mermaid_diagram(
        topic_arns=[t.arn for t in topics],
        edges=edges,
        dlq_edges=dlq_edges
    )
    
    header = [
        "%% Mermaid diagram of SNS to SQS connections",
        f"%% Region: {args.region}",
        "",
    ]
    
    text = "\n".join(header) + mermaid
    
    # Write to file
    
    
    if args.output:
        write_mermaid_to_file(text, args.output)
    else:
        print("Printing Mermaid diagram to console:")
        print(text)

    if not edges:
        print("No SNS to SQS subscriptions found.")
        
    return 0

def write_mermaid_to_file(mermaid: str, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(mermaid)
    print(f"Mermaid diagram written to {output_file}")

if __name__ == "__main__":
    raise SystemExit(main())