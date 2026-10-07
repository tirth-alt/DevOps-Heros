# GitOps with Argo CD

**Name:** Tirth Shah · **Roll Number:** 10316

Argo CD keeps the cluster in sync with the Helm chart in Git. Nobody runs `helm upgrade` against production by hand.

## The full loop

```
git push ──► CI: test, scan, build, push images tagged with the commit SHA
                 │
                 └─► CI commits the new SHA into helm/stockwise/values-gitops.yaml  [skip ci]
                                     │
Argo CD (in the cluster) ◄── pulls ──┘  notices the commit, renders the chart, syncs
                 │
                 └─► Kubernetes rolls out the new pods
```

- **Git is the source of truth.** The running version is whatever SHA is in `values-gitops.yaml`.
- **Rollback is `git revert`** of the bump commit. Argo CD then deploys the previous SHA.
- **Self-heal** undoes any manual change in the cluster.
- **Prune** removes resources that were deleted from Git.
- The commit message contains `[skip ci]`, so the bump does not start the pipeline again.

## Files

| File | Purpose |
|---|---|
| `gitops/argocd-application.yaml` | Points Argo CD at `final-devops-project/helm/stockwise` on `main`, with `values.yaml` and `values-gitops.yaml` |
| `helm/stockwise/values-gitops.yaml` | Image tags (rewritten by CI) and the name of the database Secret |

## One-time setup

1. **Install Argo CD.**
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd --server-side --force-conflicts \
     -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   kubectl get pods -n argocd -w
   ```

2. **Let the cluster pull the images.** GHCR packages are private at first. On GitHub open your profile, then **Packages**, then `stockwise-backend` and `stockwise-frontend`, then **Package settings**, and set the visibility to **Public**. The other option is a pull secret listed under `imagePullSecrets` in `values-gitops.yaml`.

3. **Create the database Secret.** Argo CD renders the chart without cluster access, so it cannot generate and remember a random password. Create it once:
   ```bash
   kubectl create namespace stockwise
   kubectl create secret generic stockwise-db -n stockwise \
     --from-literal=postgres-password="$(openssl rand -hex 16)"
   ```

4. **Register the application.**
   ```bash
   kubectl apply -f final-devops-project/gitops/argocd-application.yaml
   kubectl get applications -n argocd -w
   ```
   It shows `Synced` and `Healthy` once the first CI run has written real image tags.

5. **Open the Argo CD UI.**
   ```bash
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```
   Open https://localhost:8080 and sign in as `admin`.

## Demo: a change flows through Git

1. Make a small change, for example the dashboard subtitle in `application/frontend/src/App.jsx`, then commit and push.
2. Watch the pipeline finish. The last job commits `gitops: deploy StockWise <sha> [skip ci]`.
3. In Argo CD the app goes `OutOfSync`, then `Synced`, and the new pods roll out.
   ```bash
   kubectl annotate application stockwise -n argocd argocd.argoproj.io/refresh=hard --overwrite
   kubectl get pods -n stockwise -w
   ```
4. To roll back, run `git pull`, then `git revert <bump commit>`, then `git push`.

The Argo CD screenshot is in the root README under "Screenshots to add".

## Validation

The Application manifest was checked against a real Argo CD installation with a server-side dry run:

```
$ kubectl apply --dry-run=server -f gitops/argocd-application.yaml
application.argoproj.io/stockwise created (server dry run)
```
