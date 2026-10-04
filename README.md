# Sample Python App for AKS

A small FastAPI service with a health endpoint, a non-root Docker image, and a Helm chart for AKS.

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

Open `http://localhost:8000/` or check `http://localhost:8000/health`.

## Build and publish with GitHub Actions

The workflow in `.github/workflows/build-and-push-acr.yml` builds pull requests to `master`. On each push to `master`, it calculates and creates a SemVer tag (using conventional commit messages to determine the version bump), then publishes the image with both that release tag and the commit SHA. The image is not published for pull requests.

Configure these repository Actions secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

Configure these repository Actions variables:

- `ACR_NAME`, such as `acreusdev01` (the registry resource name, without `.azurecr.io`)
- `ACR_LOGIN_SERVER`, such as `acreusdev01.azurecr.io`

Create the GitHub Actions environment named `acr-publish`. Configure an Azure federated credential for this repository with subject `repo:<OWNER>/<REPO>:environment:acr-publish`, issuer `https://token.actions.githubusercontent.com`, and audience `api://AzureADTokenExchange`. Grant that identity the `AcrPush` role on the registry. The AKS cluster must also have permission to pull from the registry.

Each push to `master` creates the release tag and publishes it. To deploy that release, update the environment's `image.tag` in the infra repository to the generated tag. The tag action uses the conventional commit message to choose the bump (`fix:` for patch, `feat:` for minor, and a `BREAKING CHANGE:` footer for major); otherwise it defaults to patch.

The generated tag does not trigger a second workflow run. The image publish job uses the tag output from the version job in the same run.

To render the chart locally with development settings, clone the infra repository beside this repository and run:

```powershell
helm template sample-python-app ./helm/sample-python-app `
	--values ../sample-python-app-argocd/argocd/values/dev.yaml `
	--namespace default
```