from dataclasses import dataclass
import json
from typing import Optional, List


@dataclass
class Topic:
    arn: str
    name: str

@dataclass
class Queue:
    url: str
    arn: Optional[str] = None
    name: Optional[str] = None
    
@dataclass
class Subscription:
    topic_arn: str
    protocol: str
    endpoint: Optional[str]
    subscription_arn: Optional[str]
    filter_policy: Optional[dict] = None
    
def short_name_from_arn(arn: str) -> str:
    try:
        last = arn.split(":", 5)[-1]
        return last.split(":")[-1].split("/")[-1]
    except Exception:
        return arn

def list_sns_topics(sns, topic_arn: str = None) -> List[Topic]:

    if topic_arn:
        return [Topic(arn=topic_arn, name=short_name_from_arn(topic_arn))]

    topics: List[Topic] = []
    paginator = sns.get_paginator("list_topics")

    for page in paginator.paginate():
        for t in page.get("Topics", []):
            arn = t["TopicArn"]
            topics.append(Topic(arn=arn, name=short_name_from_arn(arn)))

    return topics

def get_subscription_attributes(sns, subscription_arn: str) -> dict:
    try:
        resp = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
        return resp.get("Attributes", {})
    except Exception:
        return {}

def list_topic_subscriptions(sns, topic_arn: str, include_attributes: bool = True) -> List[Subscription]:
    subs: List[Subscription] = []
    paginator = sns.get_paginator("list_subscriptions_by_topic")
    
    for page in paginator.paginate(TopicArn=topic_arn):
        for s in page.get("Subscriptions", []) or []:
            sub_arn = s.get("SubscriptionArn")
            proto = (s.get("Protocol") or "").lower()
            endpoint = s.get("Endpoint")
            
            if include_attributes and sub_arn and sub_arn != "PendingConfirmation":
                attrs = get_subscription_attributes(sns, sub_arn)
                filter_policy_str = attrs.get("FilterPolicy")
                filter_policy = None
                if filter_policy_str:
                    try:
                        filter_policy = json.loads(attrs["FilterPolicy"])
                        print("Filter policy for subscription", sub_arn, "is", filter_policy)
                    except Exception:
                        filter_policy = {"raw": attrs["FilterPolicy"]}
                        print("Could not parse filter policy for subscription", sub_arn, "as JSON, raw:", attrs["FilterPolicy"])
                subs.append(
                    Subscription(
                        topic_arn=topic_arn,
                        protocol=proto,
                        endpoint=endpoint,
                        subscription_arn=sub_arn,
                        filter_policy=filter_policy
                    )
                )
            else:
                subs.append(
                    Subscription(
                        topic_arn=topic_arn,
                        protocol=proto,
                        endpoint=endpoint,
                        subscription_arn=sub_arn,
                        filter_policy=None
                    )
                )
    return subs
        
## SQS helpers

def list_sqs_queues(sqs) -> List[Queue]:

    queues: List[Queue] = []
    paginator = sqs.get_paginator("list_queues")

    for page in paginator.paginate():
        for url in page.get("QueueUrls", []):
            queues.append(Queue(url=url))

    return queues


def get_queue_dlq_arn(sqs, queue_arn: str) -> Optional[str]:
    try:
        _,_,svc,region,account, name = queue_arn.split(":",5)
        if svc != "sqs":
            return None
        queue_url = f"https://sqs.{region}.amazonaws.com/{account}/{name}"
        print("\nFetching attributes for queue URL:", queue_url)
        attrs = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["RedrivePolicy"],
        ).get("Attributes", {})
        if not attrs.get("RedrivePolicy"):
            print(" No RedrivePolicy found")
            return None
        try:
            rp = json.loads(attrs["RedrivePolicy"])
            return rp.get("deadLetterTargetArn")
        except Exception:
            return None
    except Exception:
        return None
    
    
