# AWS Deployment

This folder contains the scripts I use to stand up an Amazon EKS cluster, install the required tooling (`aws`, `kubectl`, `eksctl`), and deploy the Dapr-based workflow stack.

## Folder layout

```
deploy/cloud/aws/
├── README.md # this guide
├── scripts/
│ ├── install_tools.sh # optional helper to install/verify CLIs
│ ├── check_permissions.sh # verifies IAM permissions before deployment
│ ├── create_cluster.sh # creates/updates an EKS cluster with eksctl
| |-- create_s3_bucket.sh #creates S3 bucket
└── manifests/
```

---

## 1. Prerequisites

- AWS account with IAM permissions to create EKS clusters, node groups, IAM roles, and networking (AdministratorAccess is easiest for experimentation)
- macOS/Linux shell with `curl`, `bash`, and `tar`
- Docker image registry push permissions (e.g., Amazon ECR) if you plan to deploy containerized workflow services
- Dapr CLI (`brew install dapr/tap/dapr-cli` or see [https://docs.dapr.io/getting-started/install-dapr-cli/](https://docs.dapr.io/getting-started/install-dapr-cli/))

---

## 2. Install platform CLIs

AWS officially documents each installer:

- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html  
- kubectl: https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html  
- eksctl: https://eksctl.io/introduction/#installation  

If you just want a quick sanity check on macOS with Homebrew, run:

```bash
./deploy/cloud/aws/scripts/install_tools.sh
```

The script will install (or verify) aws, kubectl, eksctl, and helm. Adjust it if you prefer another package manager.

## 3. Verify AWS permissions (important before cluster creation)

Before creating an EKS cluster, verify that your IAM user or role has the correct permissions.
This helps avoid errors like:

```
AccessDeniedException: User arn:aws:iam::<account-id>:user/roberto
is not authorized to perform: eks:DescribeClusterVersions
```

### Step 1 — Enable permission simulation in the AWS Console

1. Go to the AWS Management Console -> IAM -> Users.
2. Select your IAM user (e.g., roberto).
3. Under Permissions, click Add permissions -> Attach policies directly.
4. Search for and attach the following:
  * `IAMReadOnlyAccess`
  * `AmazonS3FullAccess`
  * `CloudFormationFullAccess`
  * `AmazonEC2FullAccess`
  * `AmazonEC2ContainerRegistryFullAccess`
  * `AmazonEKSFullAccess`
  * `AmazonEKSClusterPolicy`
  * `AmazonEKSServicePolicy`
5. Also add a custom inline policy that includes at least:

```json
{
  "Effect": "Allow",
  "Action": "iam:SimulatePrincipalPolicy",
  "Resource": "*"
}
```

This allows the script to run AWS's built-in IAM policy simulator.

### Step 2 — Run the permissions check script

```bash
./deploy/cloud/aws/scripts/check_permissions.sh
```

If everything is allowed, you’ll see:

```
✅ All simulated actions are ALLOWED
```

If you see ❌ actions denied, the script will list the specific missing permissions and how to enable them.

## 4. Configure AWS credentials

```bash
aws configure
# or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION env vars
```

Verify identity:

```bash
aws sts get-caller-identity
```

If needed, refresh your session token:

```bash
aws sts get-session-token --duration-seconds 3600
```

## 5. Create an EKS cluster

Once permissions are confirmed, run:

```bash
export AWS_REGION=us-east-1
export CLUSTER_NAME=aisv-dev
./deploy/cloud/aws/scripts/create_cluster.sh
```

Verify kubectl context:

```bash
kubectl config current-context
```

Verify connectivity after creation:

```bash
kubectl get nodes
```

## Step 6. Configure security group rule for Dapr side-car communication

To allow the Dapr side-car injected into your Kubernetes pods to communicate properly (for example for service invocation, state management, etc.), you must ensure that your EKS cluster’s worker/security group allows inbound traffic on port 4000 from itself. This is a networking requirement per the Dapr-on-EKS guidance. 

### Steps

1. Identify the security group attached to your EKS worker nodes or the cluster’s networking interfaces:

```bash
aws eks describe-cluster --region ${AWS_REGION} --name ${CLUSTER_NAME} \
  --query "cluster.resourcesVpcConfig.clusterSecurityGroupId" --output text
```

Suppose the returned value is `sg-0123456789abcdef`.

2. Add an inbound rule so your cluster nodes (and side-cars) can talk to each other on port 4000:

```bash
aws ec2 authorize-security-group-ingress \
  --region ${AWS_REGION} \
  --group-id sg-0123456789abcdef \
  --protocol tcp \
  --port 4000 \
  --source-group sg-0123456789abcdef
```

(Replace `sg-0123456789abcdef` with your actual security group ID.)

> Why this matters: Without this rule, Dapr side-cars may not be able to communicate internally, and you might see failures during injection or service invocation. 

## Step 7. Ensure a default StorageClass is present in the cluster

A default StorageClass is used in Kubernetes when a PersistentVolumeClaim (PVC) does not specify a storage class. Many Dapr workloads (e.g., the scheduler, state stores, etc.) assume a default class is available. AWS EKS version 1.30+ does not automatically set one for you.

### Steps

1. Check which StorageClasses exist and which (if any) is marked default:

```bash
kubectl get storageclass
```

You might get something like this:

```
NAME   PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
gp2    kubernetes.io/aws-ebs   Delete          WaitForFirstConsumer   false                  13m
```

2. If you don’t see a `(default)` label next to any of the listed storage classes, it means that no `StorageClass` is currently set as the default. Kubernetes uses the default class automatically whenever a `PersistentVolumeClaim` doesn't explicitly specify one.

To make an existing storage class (for example, `gp2`) the default, run:

```bash
kubectl patch storageclass gp2 \
  -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
(Replace gp2 with your storage class name if different.)

You should get the following:

```
storageclass.storage.k8s.io/gp2 patched
```

If you check again:

```bash
kubectl get storageclass
```

You should ge the following:

```        
NAME            PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
gp2 (default)   kubernetes.io/aws-ebs   Delete          WaitForFirstConsumer   false                  18m
```

For more custom setups (e.g., using gp3, EBS CSI, or other provisioner), you might create a full StorageClass manifest.

> Why this matters: Without a default StorageClass, PVCs that don’t explicitly specify a class may remain pending. This can break dynamic provisioning for Dapr or other applications.

## 8. Install Dapr in the cluster

Install Dapr on your cluster by running:


```bash
dapr init -k
```

This installs the Dapr control plane into the dapr-system namespace and waits for pods to become ready.

You will get the following:

```
⌛  Making the jump to hyperspace...
ℹ️  Note: To install Dapr using Helm, see here: https://docs.dapr.io/getting-started/install-dapr-kubernetes/#install-with-helm-advanced

ℹ️  Container images will be pulled from Docker Hub
✅  Deploying the Dapr control plane with latest version to your cluster...
✅  Deploying the Dapr dashboard with latest version to your cluster...
✅  Success! Dapr has been installed to namespace dapr-system. To verify, run `dapr status -k' in your terminal. To get started, go here: https://docs.dapr.io/getting-started
```

Verify Dapr Installation by running this command.

```bash
dapr status -k
```

You will get the following:

```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED              
dapr-placement-server  dapr-system  True     Running  1         1.16.2   1m   2025-11-08 00:13.11  
dapr-dashboard         dapr-system  True     Running  1         0.15.0   1m   2025-11-08 00:13.12  
dapr-sidecar-injector  dapr-system  True     Running  1         1.16.2   1m   2025-11-08 00:13.11  
dapr-operator          dapr-system  True     Running  1         1.16.2   1m   2025-11-08 00:13.11  
dapr-sentry            dapr-system  True     Running  1         1.16.2   1m   2025-11-08 00:13.11  
dapr-scheduler-server  dapr-system  True     Running  3         1.16.2   1m   2025-11-08 00:13.11 
```

## 9. Install Redis state store for workflows

Dapr Workflow needs a durable state store. The easiest option in this guide is a Redis instance deployed via the Bitnami Helm chart, followed by a Dapr component that points at it.

1. Install Redis (one time):

```bash
helm install dapr-redis oci://registry-1.docker.io/bitnamicharts/redis \
  --namespace default \
  --wait
```

This creates the `dapr-redis` Secret plus Services such as `dapr-redis-master`.

Helm names the release dapr-redis (unless you add --generate-name). To see the resources it created and confirm hostnames/secrets:

```bash
helm list -n default
```

Inspect the generated Secret (contains the password):

```bash
kubectl get secret dapr-redis -n default -o yaml
```

Check the Service names you’ll usually get dapr-redis-master and dapr-redis-replicas:

```bash
kubectl get svc -n default | grep redis
```

2. Apply the preconfigured component so Dapr knows how to reach Redis:

```bash
kubectl apply -f deploy/cloud/aws/components/redis.yaml
```

The component (`deploy/cloud/aws/components/redis.yaml`) references `dapr-redis-master.default.svc.cluster.local:6379` and the password stored in the Helm-generated `dapr-redis` Secret. Adjust the file if you install Redis elsewhere.

3. Confirm the component is registered (optional but recommended):

```bash
kubectl get components.dapr.io -n default
kubectl describe components.dapr.io workflowstatestore -n default
```

The describe output should list the `redisHost`, `redisPassword` secret reference, and `actorStateStore: true`. Once you apply this component, restart your `deepbrief` deployment (or reapply manifests) so the Dapr sidecars pick up the new state store.

## 10. Provision an S3 bucket for workflow artifacts

If you do not already have an S3 bucket for transcripts/audio, create one now (or skip if you prefer to reuse an existing bucket). Bucket names are globally unique, so pick something unlikely to collide (the helper script suggests `deepbrief-$USER-<timestamp>` by default).

1. Use the helper script to create a uniquely named bucket (defaults to `deepbrief-$USER-<timestamp>` if no name is provided). You can pass an explicit name or supply a prefix with `--prefix` to have a random suffix appended automatically. The script honors `AWS_REGION`, defaulting to `us-east-1`.

```bash
# explicit name (must be globally unique)
./deploy/cloud/aws/scripts/create_s3_bucket.sh my-unique-bucket

# or let the script append a random suffix to your prefix
./deploy/cloud/aws/scripts/create_s3_bucket.sh --prefix podcast

# or rely on the default deepbrief-$USER-<timestamp>
./deploy/cloud/aws/scripts/create_s3_bucket.sh
```

2. Update `deploy/cloud/aws/components/s3.yaml`:
   - Set the `bucket` metadata value to the bucket name from step 1.
   - Leave `region` as-is (or change it if you chose a different region).

3. After you complete the next section (secrets), apply the S3 binding component so Dapr can use it:

```bash
kubectl apply -f deploy/cloud/aws/components/s3.yaml
```

This component pulls AWS credentials from the Kubernetes secret you create in Step 11, so make sure your `.env` includes `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` before applying it.

## 11. Provide application secrets (OpenAI, ElevenLabs, etc.)

The FastAPI service relies on several API keys (OpenAI, ElevenLabs) plus any other configuration you want to pass via environment variables. Store them in a single `.env` file and turn it into a Kubernetes Secret that the Deployment can consume.

1. Create a `.env` file (for example, under `deploy/cloud/aws/.env`) with the required keys:

```env
OPENAI_API_KEY=sk-your-key
OPENAI_API_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret
```

If you already configured the AWS CLI, you can retrieve these values via:

```bash
aws configure get aws_access_key_id
aws configure get aws_secret_access_key
```

2. Turn that file into a Kubernetes secret (re-run whenever the `.env` changes):

```bash
kubectl delete secret deepbrief-secrets -n default --ignore-not-found
kubectl create secret generic deepbrief-secrets \
  --from-env-file=deploy/cloud/aws/.env \
  --namespace default \
  --dry-run=client -o yaml | kubectl apply -f -
```

3. Verify the secret (optional):

```bash
kubectl get secret deepbrief-secrets -n default -o yaml
```

The `deepbrief` Deployment consumes this secret via `envFrom`, so every key becomes an environment variable inside the pod. Whenever you add or change entries in `.env` (OpenAI, ElevenLabs, S3 credentials, etc.), rerun the secret command above and recycle the pods so they pick up the updates:

```bash
kubectl rollout restart deployment/deepbrief -n default
kubectl rollout status deployment/deepbrief -n default
```

Dapr components can also reference this same secret via `secretKeyRef` (for example, `deploy/cloud/aws/components/s3.yaml` reads `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`). Keep all sensitive values in `.env` so they are managed in one place.

## 12. Build Docker Image of App Locally with Docker Compose:

change your current directory to `deploy/cloud/aws`

```bash
docker-compose -f docker-compose.yaml build --no-cache
```

## 13 Push Docker Image to Amazon ECR

1. Create ECR repository (if not already created):

```bash
aws ecr create-repository --repository-name deepbrief --region us-east-1
```

2. Authenticate Docker to ECR:


```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

3. Tag your image:

```bash
docker tag localhost:5001/deepbrief:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepbrief:latest
```

4. Push your image:

```bash
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepbrief:latest
```

5. Update your Kubernetes manifest to use the ECR image URL:

```yaml
image: <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepbrief:latest
```

Replace `<account-id>` with your AWS account ID. You can wind your AWS account ID locally running the following:

```bash
aws sts get-caller-identity --query Account --output text
```

## 14. Deploy Workflow App

Start with the provided namespaces:

```bash
kubectl apply -f deploy/cloud/aws/manifests/
```

## 15. Check Pod Status

Check pods status:

```bash
kubectl get pods -n default
kubectl get pods -l app=deepbrief -n default --watch
```

Check deployment status:

```bash
kubectl get deployments -n default
```

Check service status:

```bash
kubectl get svc -n default
```

For more details, describe the pod:

```bash
kubectl describe pod <pod-name> -n default
```

Need to copy the pod name quickly? Use:

```bash
kubectl get pods -l app=deepbrief -n default -o name
```

View logs for your app container:

```bash
kubectl logs <pod-name> -n default -c deepbrief
```

Replace <pod-name> with the actual pod name from step 1.

You can also tail the logs:

```bash
kubectl logs -f <pod-name> -n default -c deepbrief
```

## 16. Port Forward

Open a local tunnel from `localhost:8080` to the service’s port `80`. While it runs, that terminal shows `Forwarding from 127.0.0.1:8080…` and holds the session open. When you’re done, press `Ctrl+C` in that same terminal to stop port-forwarding immediately. Many folks keep it in a dedicated terminal tab so their main shell stays free.

```bash
kubectl port-forward svc/deepbrief 8080:80 -n default
```

## 17. Redeploy the app after code changes

Whenever you change the FastAPI service or its dependencies, rerun the same build/push workflow from steps 12 and 13, then recycle the Deployment so the new image is pulled. (The commands are repeated here for convenience.)

```bash
# from the deploy/cloud/aws/ directory
docker-compose -f docker-compose.yaml build deepbrief --no-cache

aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag localhost:5001/deepbrief:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepbrief:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepbrief:latest

kubectl rollout restart deployment/deepbrief -n default

# In another terminal
kubectl get pods -l app=deepbrief -n default --watch
```

`kubectl rollout restart` triggers the rolling update, while the watch command streams real-time pod events. Keep both running so you immediately see readiness probe failures or config errors.

```bash
# Watch pod creation/termination
kubectl get pods -l app=deepbrief -n default --watch

# In another split/terminal, grab crash details if a pod restarts
kubectl logs pod/<pod-name> -n default -c deepbrief --previous
kubectl describe pod/<pod-name> -n default

# Need the exact pod name?
kubectl get pods -l app=deepbrief -n default -o name
```

Once the new pod shows up in the watch output (and is `READY 2/2`), tail its live logs:

```bash
kubectl logs -f pod/<new-pod-name> -n default -c deepbrief --since=30s
```

If you prefer, you can also reapply the manifests instead of issuing a rollout restart. This reapplies any YAML edits and naturally triggers a rolling update when pod specs change:

```bash
kubectl apply -f deploy/cloud/aws/manifests/
```

When the pods report `READY 2/2` and port-forwarding no longer errors with `connection refused`, the new version is running.

## 18. Clean up

```bash
eksctl delete cluster --name "${CLUSTER_NAME}" --region "${AWS_REGION}"
```

This removes the cluster and managed node groups.
Don’t forget to delete any ECR repositories or S3 buckets you created manually.

## ✅ Summary flow

1. Enable IAM simulation permission in the AWS Console.
2. Run `check_permissions.sh` — verify access.
3. Fix any missing EKS/IAM/EC2/CFN permissions.
4. Run `create_cluster.sh` — create the cluster.
5. Run `bootstrap_dapr.sh` — install Dapr.
6. Deploy your workloads.
