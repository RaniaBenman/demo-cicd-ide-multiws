# Multi-workspace CICD Demo

This is a sample project for Databricks, generated via the `dbx init` command.

While using this project, you need Python 3.X, dbx as well as `pip` or `conda` for package management.

**👉 Bricksters only** : 
The slide deck for this demo repository is on [this link](https://bit.ly/3zZBEPw)

## Forks

If you have forked this repo, set the following secrets or environment variables on your CI provider. (e.g: On Github that would be **Settings** > **Secrets** > **Actions**)  :
- `DATABRICKS_HOST` & `DATABRICKS_TOKEN` for the **staging** Databricks workspace 
- `DATABRICKS_HOST_PROD` & `DATABRICKS_TOKEN_PROD` for the **production** Databricks workspace 

## Testing and releasing via CI pipeline

The Github Actions of this repository are already preconfigured :
- to trigger the CI pipeline upon the merging and pushing of code into the `staging` branch. The CI pipeline is a general testing pipeline that consists of Unit tests (which will run on a VM), as well as integration tests (which will run on the **staging** Databricks workspace)
- to trigger the release pipeline upon the creation of a release and tagging the new code version on the `main` branch:
```
git tag -a v<your-project-version> -m "Release tag for version <your-project-version>"
git push origin --tags
```

## Interactive execution and development from a local environment

In order to launch this application remotely from your local environment and outside of its automation chain, make sure to set up the following :
1. With Databricks CLI, create a profile using your credentials from the Dev Databricks workspace
2. In the `.dbx/project.json` file, edit the profile name in the the dev environment configuration, using the same profile name you declared in step 1
3. `dbx` expects that the cluster for interactive execution mentioned in the `cluster-name` parameter exists on the **Dev** Databricks workspace and it supports `%pip` and `%conda` magic [commands](https://docs.databricks.com/libraries/notebooks-python-libraries.html).
5. Job configurations for application execution and test execution are already provided to you in the `conf/deployment.yml`, so feel free to launch either one of the following commands from your terminal:

```dbx execute --environment=dev --cluster-name="neutral" --job=demo-cicd-ide-multiws```

```dbx execute --environment=dev --cluster-name="neutral" --job=demo-cicd-ide-multiws-integration-test```

```dbx execute --environment=dev --cluster-name="neutral" --job=demo-cicd-ide-multiws-notebook```

Multiple users also can use the same cluster for development. Libraries will be isolated per each execution context.

---------

## Installing project requirements

```bash
pip install -r unit-requirements.txt
```

## Install project package in a developer mode

```bash
pip install -e .
```

## Testing

For local unit testing, please use `pytest`:
```
pytest tests/unit --cov
```

For an integration test on interactive cluster, use the following command:
```
dbx execute --cluster-name=<name of interactive cluster> --job=demo-covea-ide-gitinit-sample-integration-test
```

For a test on an automated job cluster, deploy the job files and then launch:
```
dbx deploy --jobs=demo-covea-ide-gitinit-sample-integration-test --files-only
dbx launch --job=demo-covea-ide-gitinit-sample-integration-test --as-run-submit --trace
```

## Preparing deployment file

Next step would be to configure your deployment objects. To make this process easy and flexible, we're using YAML for configuration.

By default, deployment configuration is stored in `conf/deployment.yml`.

## Deployment for Run Submit API

To deploy only the files and not to override the job definitions, do the following:

```bash
dbx deploy --files-only
```

To launch the file-based deployment:
```
dbx launch --as-run-submit --trace
```

This type of deployment is handy for working in different branches, not to affect the main job definition.

## Deployment for Run Now API

To deploy files and update the job definitions:

```bash
dbx deploy
```

To launch the file-based deployment:
```
dbx launch --job=<job-name>
```

This type of deployment shall be mainly used from the CI pipeline in automated way during new release.


## Testing and releasing via CI pipeline

- To trigger the CI pipeline, simply push your code to the repository. If CI provider is correctly set, it shall trigger the general testing pipeline
- To trigger the release pipeline, get the current version from the `demo_cicd_ide_multiws/__init__.py` file and tag the current code version:
```
git tag -a v<your-project-version> -m "Release tag for version <your-project-version>"
git push origin --tags
```
