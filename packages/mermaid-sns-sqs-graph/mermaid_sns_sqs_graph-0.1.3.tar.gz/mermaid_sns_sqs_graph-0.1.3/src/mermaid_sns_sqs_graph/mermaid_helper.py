from typing import List, Tuple
from .aws_helper import short_name_from_arn

def mermaid_id_from_arn(arn: str) -> str:
    return (
        arn.replace(":", "_")
        .replace("/","_")
        .replace("-","_")
        .replace("*", "star")
    )

def format_filter_label(fp: dict | None) -> str | None:
    if not fp:
        return None
    try:
        parts: List[str] = []
        for key, val in fp.items():
            vals = val if isinstance(val, list) else [val]
            parts.append(f"{key}={'|'.join(str(v) for v in vals)}")
        return ",".join(parts)
    except Exception:
        return None

# edges: List of (topic_arn, queue_arn)
def render_mermaid_diagram(topic_arns: List[str], edges: List[Tuple[str,str, str | None]], dlq_edges: List[Tuple[str,str]]) -> str:
    
    lines: List[str] =[]
    lines.append("graph LR")
    
    #topics (adds the SNS nodes to the diagram)
    for t in sorted(set(topic_arns)):
        tid = mermaid_id_from_arn(t)
        tlabel = f"SNS: {short_name_from_arn(t)}"
        lines.append(f" {tid}[\"{tlabel}\"]")

    print(f"\n Lines: {lines}")
    #  Lines: ['graph LR', ' arn_aws_sns_us_east_1_767397825521_gaurav_testing_topic["SNS: gaurav-testing-topic"]', ' arn_aws_sns_us_east_1_767397825521_zoho.fifo["SNS: zoho.fifo"]']

    # Queues (adds the SQS nodes to the diagram and the dlq also)
    queue_nodes = {q for _,q,_ in edges} | {dlq for _, dlq in dlq_edges}
    for q in sorted(queue_nodes):
        qid = mermaid_id_from_arn(q)
        qlabel = f"SQS: {short_name_from_arn(q)}"
        lines.append(f" {qid}[\"{qlabel}\"]")

    print(f"\n Lines: {lines}")

    # Edges
    for (t, q , label) in edges:
        tid = mermaid_id_from_arn(t)
        qid = mermaid_id_from_arn(q)
        if label:
            lines.append(f" {tid} -->|\"{label}\"| {qid}")
        else:
            lines.append(f" {tid} --> {qid}")

    print(f"\n Lines: {lines}")


    # DLQ
    for (q,dlq) in dlq_edges:
        src_id = mermaid_id_from_arn(q)
        dst_id = mermaid_id_from_arn(dlq)
        lines.append(f" {src_id} -. DLQ .-> {dst_id} ")

    print(f"\n Lines: {lines}")

    return "\n".join(lines) + "\n"
