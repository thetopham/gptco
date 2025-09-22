# Minimal stub: load sources from YAML and print actions.
import sys, yaml, json

def main(path):
    with open(path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    print("[ingest] would ingest:", json.dumps(cfg, indent=2))

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "configs/rag/sources.yaml"
    main(p)
