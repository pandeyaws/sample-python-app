# Sample Python App for AKS

A small FastAPI application with a built-in web dashboard, JSON status and health endpoints, a non-root Docker image, and a Helm chart for AKS.

## Repository layout

- `sample-python-app` contains the application, Dockerfile, and reusable Helm chart.
- `sample-python-app-argocd` contains the development Helm values and Argo CD application configuration.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/` for the web dashboard. The application status API is available at `http://localhost:8000/api/status`, and the health check is at `http://localhost:8000/health`.

## Run tests

Install the application and test dependencies, then run the test suite:

```powershell
python -m pip install -r requirements.txt 'httpx2>=2.0.0,<3.0.0' 'pytest>=8.0.0,<10.0.0' 'pytest-cov>=5.0.0,<8.0.0'
python -m pytest --junitxml=test-results.xml --cov=app --cov-fail-under=80 --cov-report=xml:coverage.xml --cov-report=term-missing
```

The command prints coverage in the terminal and writes JUnit results to `test-results.xml` and coverage details to `coverage.xml`. It fails if application coverage is below 80%. GitHub Actions runs the same command before building the image, then uploads those reports and `tests/test_main.py` as the `python-test-artifacts` artifact (retained for 14 days), even when tests fail. Download it from the workflow run's **Artifacts** section.

## Build and publish with GitHub Actions

The workflow in `.github/workflows/build-and-push-acr.yml` builds pull requests to `master`. On each push to `master`, it calculates and creates a SemVer tag (using conventional commit messages to determine the version bump), then publishes the image with both that release tag and the commit SHA. The image is not published for pull requests.

Configure these repository Actions secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ARGOCD_REPO_TOKEN` — a fine-grained personal access token with Contents read/write access to `pandeyaws/sample-python-app-argocd`.

Configure these repository Actions variables:

- `ACR_NAME`, such as `acreusdev01` (the registry resource name, without `.azurecr.io`)
- `ACR_LOGIN_SERVER`, such as `acreusdev01.azurecr.io`

Create the GitHub Actions environment named `acr-publish`. Configure an Azure federated credential for this repository with subject `repo:<OWNER>/<REPO>:environment:acr-publish`, issuer `https://token.actions.githubusercontent.com`, and audience `api://AzureADTokenExchange`. Grant that identity the `AcrPush` role on the registry. The AKS cluster must also have permission to pull from the registry.

Each push to `master` creates the release tag and publishes it. The workflow then updates the dev ApplicationSet's `targetRevision` in `pandeyaws/sample-python-app-argocd` to that tag and pushes the change to `master`. The ApplicationSet uses this revision for the Helm chart and image tag, and Argo CD's automated sync deploys it. The tag action uses the conventional commit message to choose the bump (`fix:` for patch, `feat:` for minor, and a `BREAKING CHANGE:` footer for major); otherwise it defaults to patch.

The generated tag does not trigger a second workflow run. The image publish job uses the tag output from the version job in the same run.

To render the chart locally with development settings, clone the infra repository beside this repository and run:

```powershell
helm template sample-python-app ./helm/sample-python-app `
	--values ../sample-python-app-argocd/argocd/values/dev.yaml `
	--namespace default
```