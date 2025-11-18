# pve-cloud-backup

python package and docker image that form the base for backing up pve cloud k8s namespaces, aswell as git repos and nextcloud namespaces

inside the pve_cloud collection the version of the backup python package is HARDCODED! (`playbooks/setup_backup_daemon.yaml`)

## Releasing to pypi manually

```bash
pip install build twine
rm -rf dist
python3 -m build
python3 -m twine upload dist/*
```

## Docker hub push manually

```bash
VERSION=$(grep -E '^version *= *"' pyproject.toml | sed -E 's/^version *= *"(.*)"/\1/')
docker build -t tobiashvmz/pve-cloud-backup:$VERSION .
docker push tobiashvmz/pve-cloud-backup:$VERSION
```

## PVE Cloud dependency locations

* Dockerfile