# Useful Kubernetes commands

## Example use for interactive pods:

Create a Pod: 
```
kubectl create -f interactive.yaml
```

Checking pod status: 
```
kubectl get pods
```

Connecting to the pod: 
```
kubectl exec -it int bash
```

Run Jupyter: 
```
jupyter notebook --ip='0.0.0.0'
```

Port forwarding (in a new terminal): 
```
kubectl port-forward int 8888:8888
```

Delete the Pod: 
```
kubectl delete pod int
```

## Example use for jobs:

Get jobs: 
```
kubectl get jobs
```

Create a job: 
```
kubectl apply -f job.yaml
```

Status of the job: 
```
kubectl describe jobs/brev
```

Associated Pod:
```
kubectl get pods
```

Get output: 
```
kubectl -f logs pod-name
```

Delete the job: 
```
kubectl delete jobs/brev
```

Delete the pod: 
```
kubectl delete pod pod-name
```

## How to copy from storage to local disk:

Create a pod with mounted storage and then: 
```
kubectl cp NAMESPACE/POD_NAME/PERSISTENT_VOLUME_NAME/DIR .
```