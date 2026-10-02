# Sample Python App for AKS

A small FastAPI service with a health endpoint, a non-root Docker image, and a Helm chart for AKS.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/` or check `http://localhost:8000/health`.

## Build and push with GitHub Actions

The workflow in `.github/workflows/build-and-push-acr.yml` builds on pull requests to `main` and pushes an image tagged with the commit SHA on pushes to `main`.

Configure these repository Actions secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

Configure these repository Actions variables:

- `ACR_NAME`, such as `myregistry`
- `ACR_LOGIN_SERVER`, such as `myregistry.azurecr.io`

Configure an Azure federated credential for the GitHub repository with subject `repo:<OWNER>/<REPO>:ref:refs/heads/main`, issuer `https://token.actions.githubusercontent.com`, and audience `api://AzureADTokenExchange`. Grant that identity the `AcrPush` role on the registry. The AKS cluster must also have permission to pull from the registry.

## Build and publish

Sign in to Azure and Docker, and replace `<acr-name>` with your Azure Container Registry name:

```powershell
az acr login --name <acr-name>
docker build -t <acr-name>.azurecr.io/sample-python-app:v1 .
docker push <acr-name>.azurecr.io/sample-python-app:v1
```

Attach the registry to the AKS cluster if it is not already configured:

```powershell
az aks update --resource-group <resource-group> --name <cluster-name> --attach-acr <acr-name>
az aks get-credentials --resource-group <resource-group> --name <cluster-name>
```

Install or upgrade the chart with environment-specific values. For development, use a single replica and an internal `ClusterIP` Service:

```powershell
helm upgrade --install sample-python-app ./helm/sample-python-app `
	--values ./helm/sample-python-app/environments/development.yaml `
	--namespace default `
	--set image.repository=<acr-name>.azurecr.io/sample-python-app `
	--set image.tag=v1
kubectl rollout status deployment/sample-python-app
kubectl port-forward service/sample-python-app 8080:80
```

Then open `http://localhost:8080/` or `http://localhost:8080/health`.

For production, use the LoadBalancer Service and production resource settings:

```powershell
helm upgrade --install sample-python-app ./helm/sample-python-app `
	--values ./helm/sample-python-app/environments/production.yaml `
	--namespace default `
	--set image.repository=<acr-name>.azurecr.io/sample-python-app `
	--set image.tag=v1
kubectl rollout status deployment/sample-python-app
kubectl get service sample-python-app --watch
```

When the Service has an external IP, open `http://<external-ip>/` or `http://<external-ip>/health`.

To remove the release, run `helm uninstall sample-python-app --namespace default`.