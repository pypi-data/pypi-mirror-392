#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import requests

WORKFLOW_URL = "http://localhost:8080"
STATE_FILE = Path(".workflow-instance")


def save_instance_id(instance_id: str):
    STATE_FILE.write_text(instance_id)


def load_instance_id(provided: str | None) -> str:
    if provided:
        return provided
    if STATE_FILE.exists():
        return STATE_FILE.read_text().strip()
    raise RuntimeError("No instance_id provided and no cached instance found.")


def start_workflow(args):
    dialogue_rounds = args.dialogue_max_rounds
    if dialogue_rounds is None:
        dialogue_rounds = args.max_rounds
    if dialogue_rounds is None:
        dialogue_rounds = 4

    payload = {
        "podcast_name": args.podcast_name,
        "host": {"name": args.host_name, "voice": args.host_voice},
        "participants": [{"name": name} for name in args.participants],
        "dialogue_max_rounds": dialogue_rounds,
        "output_directory": args.output_directory,
        "audio_model": args.audio_model,
        "search_days": args.search_days,
        "search_max_results": args.search_max_results,
        "classify_batch_size": args.classify_batch_size,
        "download_batch_size": args.download_batch_size,
        "transcript_creation_batch_size": args.transcript_creation_batch_size,
        "episode_summary_batch_size": args.episode_summary_batch_size,
        "papers_storage_prefix": args.papers_storage_prefix,
        "download_timeout_seconds": args.download_timeout_seconds,
        "persist_papers_locally": args.persist_papers_locally,
        "indexes_storage_prefix": args.indexes_storage_prefix,
        "persist_index_locally": args.persist_index_locally,
        "transcripts_storage_prefix": args.transcripts_storage_prefix,
        "persist_transcripts_locally": args.persist_transcripts_locally,
        "markdowns_storage_prefix": args.markdowns_storage_prefix,
        "persist_markdowns_locally": args.persist_markdowns_locally,
        "recordings_storage_prefix": args.recordings_storage_prefix,
        "persist_recordings_locally": args.persist_recordings_locally,
        "episodes_storage_prefix": args.episodes_storage_prefix,
        "persist_episodes_locally": args.persist_episodes_locally,
    }
    resp = requests.post(f"{WORKFLOW_URL}/workflows/research-podcast", json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    instance_id = data["instance_id"]
    save_instance_id(instance_id)
    print(f"Workflow started: {instance_id}")
    return instance_id


def get_status(args):
    instance_id = load_instance_id(args.instance_id)
    resp = requests.get(f"{WORKFLOW_URL}/workflows/{instance_id}", timeout=30)
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def wait_for_completion(args):
    instance_id = load_instance_id(args.instance_id)
    timeout = args.timeout
    resp = requests.get(
        f"{WORKFLOW_URL}/workflows/{instance_id}/wait",
        params={"timeout": timeout},
        timeout=timeout + 30,
    )
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def terminate_workflow(args):
    instance_id = load_instance_id(args.instance_id)
    payload = {
        "output": args.output,
        "recursive": args.recursive,
    }
    resp = requests.post(
        f"{WORKFLOW_URL}/workflows/{instance_id}/terminate",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def main():
    parser = argparse.ArgumentParser(description="Workflow CLI helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start the research podcast workflow")
    start_parser.add_argument("--podcast-name", default="AI Security Voice")
    start_parser.add_argument("--host-name", default="Test Host")
    start_parser.add_argument("--host-voice")
    start_parser.add_argument("--participants", nargs="*", default=[])
    start_parser.add_argument("--dialogue-max-rounds", type=int, default=None)
    start_parser.add_argument("--max-rounds", type=int, default=None, help=argparse.SUPPRESS)
    start_parser.add_argument("--output-directory", default="output")
    start_parser.add_argument("--audio-model", default="eleven_flash_v2_5")
    start_parser.add_argument("--search-days", type=int, default=30)
    start_parser.add_argument("--search-max-results", type=int, default=5)
    start_parser.add_argument("--classify-batch-size", type=int, default=25)
    start_parser.add_argument("--download-batch-size", type=int, default=5)
    start_parser.add_argument("--transcript-creation-batch-size", type=int, default=5)
    start_parser.add_argument("--episode-summary-batch-size", type=int, default=3)
    start_parser.add_argument("--papers-storage-prefix", default="papers")
    start_parser.add_argument("--download-timeout-seconds", type=int, default=60)
    start_parser.add_argument(
        "--persist-papers-locally",
        dest="persist_papers_locally",
        action="store_true",
        default=False,
    )
    start_parser.add_argument("--indexes-storage-prefix", default="indexes")
    start_parser.add_argument(
        "--persist-index-locally",
        dest="persist_index_locally",
        action="store_true",
        default=True,
    )
    start_parser.add_argument(
        "--no-persist-index-locally",
        dest="persist_index_locally",
        action="store_false",
    )
    start_parser.add_argument("--transcripts-storage-prefix", default="transcripts")
    start_parser.add_argument(
        "--persist-transcripts-locally",
        dest="persist_transcripts_locally",
        action="store_true",
        default=True,
    )
    start_parser.add_argument(
        "--no-persist-transcripts-locally",
        dest="persist_transcripts_locally",
        action="store_false",
    )
    start_parser.add_argument("--markdowns-storage-prefix", default="markdowns")
    start_parser.add_argument(
        "--persist-markdowns-locally",
        dest="persist_markdowns_locally",
        action="store_true",
        default=True,
    )
    start_parser.add_argument(
        "--no-persist-markdowns-locally",
        dest="persist_markdowns_locally",
        action="store_false",
    )
    start_parser.add_argument("--recordings-storage-prefix", default="recordings")
    start_parser.add_argument(
        "--persist-recordings-locally",
        dest="persist_recordings_locally",
        action="store_true",
        default=True,
    )
    start_parser.add_argument(
        "--no-persist-recordings-locally",
        dest="persist_recordings_locally",
        action="store_false",
    )
    start_parser.add_argument("--episodes-storage-prefix", default="episodes")
    start_parser.add_argument(
        "--persist-episodes-locally",
        dest="persist_episodes_locally",
        action="store_true",
        default=True,
    )
    start_parser.add_argument(
        "--no-persist-episodes-locally",
        dest="persist_episodes_locally",
        action="store_false",
    )
    start_parser.set_defaults(func=start_workflow)

    status_parser = subparsers.add_parser("status", help="Check workflow status")
    status_parser.add_argument("--instance-id")
    status_parser.set_defaults(func=get_status)

    wait_parser = subparsers.add_parser("wait", help="Wait for workflow completion")
    wait_parser.add_argument("--instance-id")
    wait_parser.add_argument("--timeout", type=int, default=1800)
    wait_parser.set_defaults(func=wait_for_completion)

    terminate_parser = subparsers.add_parser("terminate", help="Terminate a workflow instance")
    terminate_parser.add_argument("--instance-id")
    terminate_parser.add_argument("--output", default=None, help="Optional output payload")
    terminate_parser.add_argument("--recursive", action="store_true", default=True)
    terminate_parser.add_argument("--no-recursive", dest="recursive", action="store_false")
    terminate_parser.set_defaults(func=terminate_workflow)

    args = parser.parse_args()
    try:
        result = args.func(args)
        if result and args.command == "start":
            print(f"Cached instance_id in {STATE_FILE}")
    except Exception as exc:
        print("Error:", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
