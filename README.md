# appia-dev

## Service account key
This project uses a Google Cloud service account JSON key.
The file `gcp-sa.json` is ignored by git. Provide the JSON contents via the `GCP_SA_JSON` environment variable.

For local use, export it before running scripts:

```bash
export GCP_SA_JSON="$(cat /path/to/gcp-sa.json)"
```

In GitHub Actions, add a secret named `GCP_SA_JSON` with the same value.
