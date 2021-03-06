# Multi-workspace CICD Demo

This is a sample project for Databricks, generated via the `dbx init` command.

While using this project, you need Python 3.X, dbx as well as `pip` or `conda` for package management.

**👉 Bricksters only** : 
The slide deck for this demo repository is on [this link](https://bit.ly/3zZBEPw)

## Forks

If you have forked this repo, please make sure you set up 3 branches `dev`, `staging`, `main` as well as the following secrets or environment variables on your CI provider :
- `DATABRICKS_HOST` & `DATABRICKS_TOKEN` for the **staging** Databricks workspace 
- `DATABRICKS_HOST_PROD` & `DATABRICKS_TOKEN_PROD` for the **production** Databricks workspace 

... On Github these secrets would be set up on **Settings** > **Secrets** > **Actions** 

All your Databricks workspaces must have a pre-existing table called `hive_metastore.default.turbines`
that follows the schema of the sample dataset provided in [tests/unit/data](https://github.com/RaniaBenman/demo-cicd-ide-multiws/tree/dev/tests/unit/data). You can rename this table in the [conf/test/sample.yml](https://github.com/RaniaBenman/demo-cicd-ide-multiws/blob/dev/conf/test/sample.yml) file.

If you're interested in [**Interactive execution and development from a local environment**](#interactive-execution-and-development-from-a-local-environment), please make sure to create on your **Dev** Databricks workspace, a cluster that fits the criteria described in that section.

**👉 Bricksters only** : 
You don't have to go through **any** of this, please simply request access to this demo (repository + workspaces) by contacting the creator of this repository.

## Testing and releasing via CI pipeline

The Github Actions of this repository are already preconfigured :
- to trigger the CI pipeline upon the merging and pushing of code into the `staging` branch (from the `dev` branch). The CI pipeline is a general testing pipeline that consists of Unit tests (which will run on a VM), as well as integration tests (which will run on the **staging** Databricks workspace)
- to trigger the release pipeline, not upon merging into the `main` branch from `staging`, but upon the creation of a release and tagging the new code version on the `main` branch:
```
git tag -a v<your-project-version> -m "Release tag for version <your-project-version>"
git push origin --tags
```

## Interactive execution and development from a local environment

In order to launch this application remotely from your local environment and outside of this automation chain, please make sure to set up the following :
1. With Databricks CLI, create a profile using your credentials from the **Dev** Databricks workspace
2. In the `.dbx/project.json` file, replace the profile name of the dev environment configuration by the one you declared in step 1
3. `dbx` expects that the cluster for interactive execution already exists on the **Dev** Databricks workspace and that it supports `%pip` and `%conda` magic [commands](https://docs.databricks.com/libraries/notebooks-python-libraries.html). This cluster's name is passed as the `cluster-name` parameter, as illustrated in the commands bellow.

4. Job configurations for application execution and test execution are already provided to you in the `conf/deployment.yml`
5. Execute your code remotely on the **Dev** Databricks workspace by launching either one of the following commands from your local terminal after replacing *neutral* with the name of your cluster :

```dbx execute --environment=dev --cluster-name="neutral" --job=demo-cicd-ide-multiws```

```dbx execute --environment=dev --cluster-name="neutral" --job=demo-cicd-ide-multiws-integration-test```

```dbx execute --environment=dev --cluster-name="neutral" --job=demo-cicd-ide-multiws-notebook```

**👉 Bricksters only** : 
No need to replace the name. This cluster has already been set up for you and **is** called *neutral*.

**Note** : Multiple users also can use the same cluster for development. Libraries will be isolated per each execution context.

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
