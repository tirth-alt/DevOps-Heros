# Kubernetes Volumes

A container's filesystem is temporary. When the container restarts, anything written inside it is lost.
Volumes solve this by giving containers storage that lives outside the container itself.

| Type | Lifetime | Shared between | Typical use |
|---|---|---|---|
| emptyDir | Same as the Pod | Containers in one Pod | Cache, scratch space, sidecar sharing |
| hostPath | Same as the node | Pods on the same node | Node agents, log collectors, local testing |
| PersistentVolume + PVC | Independent of Pods | Pods that claim it | Databases, uploads, any stateful app |

---

## emptyDir

- Created empty when the Pod is scheduled onto a node.
- Every container in the Pod can mount it, so it is a simple way to share files.
- Deleted forever when the Pod is removed. It survives container restarts, not Pod deletion.
- `emptyDir.medium: Memory` stores it in RAM (tmpfs) for very fast scratch space.

Example: [emptydir-pod.yaml](emptydir-pod.yaml). An nginx Pod mounts an emptyDir at `/data`. A file written there is lost when the Pod is deleted and recreated.

```yaml
volumes:
  - name: shared
    emptyDir: {}
```

## hostPath

- Mounts a file or directory from the node's own filesystem into the Pod.
- Data survives Pod deletion, but only on that node. A Pod rescheduled elsewhere sees different data.
- It is a security risk because a Pod can read or change node files. Avoid it for normal apps.
- `type: DirectoryOrCreate` creates the directory if it does not exist.

Example: [hostpath-pod.yaml](hostpath-pod.yaml). A file written to `/data` inside the Pod appears on the node at `/tmp/hostpath-data`.

```yaml
volumes:
  - name: host-dir
    hostPath:
      path: /tmp/hostpath-data
      type: DirectoryOrCreate
```

## PersistentVolume (PV)

- A piece of storage in the cluster, created by an admin or by a provisioner.
- It is a cluster-wide object, not namespaced.
- Key fields:
  - **capacity**: how much storage it offers.
  - **accessModes**: `ReadWriteOnce` (one node), `ReadOnlyMany`, `ReadWriteMany`, `ReadWriteOncePod`.
  - **persistentVolumeReclaimPolicy**: `Retain` keeps the data after the claim is deleted. `Delete` removes the storage too.
  - **storageClassName**: which class it belongs to.

## PersistentVolumeClaim (PVC)

- A request for storage made by a user or app, inside a namespace.
- Kubernetes finds a PV that matches size, access mode and StorageClass, then **binds** them one-to-one.
- The Pod only refers to the PVC by name, so the app does not need to know where the storage really lives.

PV lifecycle: `Available` → `Bound` → `Released` (claim deleted) → reclaimed or deleted.

Example: [pv.yaml](pv.yaml), [pvc.yaml](pvc.yaml) and [pod.yaml](pod.yaml). A hand-made 1Gi PV `student-pv` is bound by the 500Mi claim `student-pvc`, and the Pod `storage-demo` mounts it at `/data`. Both use `storageClassName: manual`. Without it, minikube gives the PVC the default `standard` class and it never binds to `student-pv`.

## StorageClass

- Describes a "type" of storage, for example fast SSD, standard disk or network storage.
- Names a **provisioner** that knows how to create volumes, such as `ebs.csi.aws.com` on AWS or `k8s.io/minikube-hostpath` on minikube.
- `volumeBindingMode: WaitForFirstConsumer` delays creating the volume until a Pod uses it, so it lands in the right zone.
- One StorageClass can be marked `default`. A PVC with no class uses the default.

```bash
kubectl get storageclass
```

## Dynamic provisioning

- With static provisioning, an admin must create every PV in advance.
- With dynamic provisioning, the PVC names a StorageClass and the provisioner creates a matching PV automatically.
- The auto-created PV gets a name like `pvc-<uid>` and usually has reclaim policy `Delete`.

Example: [dynamic-pvc.yaml](dynamic-pvc.yaml). Only a 500Mi PVC is written. The PV appears by itself.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  storageClassName: standard
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 500Mi
```

## Static vs dynamic

| | Static | Dynamic |
|---|---|---|
| Who creates the PV | Admin, by hand | Provisioner, automatically |
| Needs a StorageClass provisioner | No | Yes |
| Scales to many apps | Poorly | Well |
| Typical in cloud clusters | Rare | Standard practice |
