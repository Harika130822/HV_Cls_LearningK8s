# Session 05: Production Scaling Patterns

This session completes the Kubernetes scaling story after Session 04.

Session 04 taught:

```text
HPA changes Pod replica count.
VPA changes or recommends Pod CPU and memory requests.
```

This session adds the production pieces:

- Memory-based HPA.
- Custom and external metric HPA.
- ResourceQuota and LimitRange guardrails.
- PodDisruptionBudget with VPA and node disruption.
- Cluster Autoscaler.
- Karpenter.
- EKS Auto Mode compute scaling.
- Pending Pods triggering new Nodes.
- A production scaling checklist.

## Complete Scaling Model

```text
Application demand
  -> HPA adds or removes Pods
    -> Scheduler tries to place Pods on Nodes
      -> Pending Pods appear if existing Nodes are full
        -> EKS Auto Mode, Karpenter, or Cluster Autoscaler adds Nodes
          -> Scheduler places Pending Pods

Resource usage history
  -> VPA recommends or applies better CPU and memory requests
    -> Requests affect scheduling
    -> Requests also affect HPA percentage calculations

Namespace policy
  -> LimitRange provides defaults and min/max rules
  -> ResourceQuota caps total namespace consumption

Availability policy
  -> PodDisruptionBudget limits voluntary disruption
  -> Node drains, VPA evictions, and node consolidation must respect availability
```

## Scaling Types

| Layer | Kubernetes object or tool | What changes |
| --- | --- | --- |
| Pod replicas | HorizontalPodAutoscaler | Deployment/StatefulSet replica count |
| Pod size | VerticalPodAutoscaler | Container CPU/memory requests |
| Namespace capacity | ResourceQuota | Total allowed namespace usage |
| Default resources | LimitRange | Default/min/max requests and limits |
| App disruption | PodDisruptionBudget | Allowed voluntary Pod evictions |
| Node count with ASGs | Cluster Autoscaler | EC2 Auto Scaling Group desired capacity |
| Just-in-time Nodes | Karpenter | NodeClaims/EC2 instances |
| Managed EKS compute | EKS Auto Mode | AWS-managed Nodes and NodePools |

## Sub-Session Order

Follow the sub-sessions in this order:

1. `subsessions/01-resource-guardrails`: create Namespace, LimitRange, and ResourceQuota.
2. `subsessions/02-memory-hpa`: scale a Deployment using memory utilization.
3. `subsessions/03-custom-external-metrics-hpa`: learn custom and external metric HPA patterns.
4. `subsessions/04-pdb-and-vpa-safety`: protect autoscaled workloads from voluntary disruption.
5. `subsessions/05-node-autoscaling`: demonstrate Pending Pods and node autoscaler responses.
6. `subsessions/06-production-checklist`: tie everything into an operational checklist.

## Prerequisites

For the full session:

- A working Kubernetes cluster.
- `kubectl` configured.
- Metrics Server installed.
- Optional: VPA installed for the VPA safety example.
- Optional: Prometheus plus a custom metrics adapter for custom metric HPA.
- Optional: EKS Auto Mode, Karpenter, or Cluster Autoscaler for node scaling.

Check the current cluster:

```bash
kubectl version
kubectl get nodes
kubectl top nodes
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl api-resources | grep -E "horizontalpodautoscalers|verticalpodautoscalers|poddisruptionbudgets|resourcequotas|limitranges"
```

## Apply Order

From `sessions/05-production-scaling`:

```bash
kubectl apply -f subsessions/01-resource-guardrails/
```

Then run each sub-session separately. Do not apply the entire session folder at once because some examples are provider-specific or require CRDs such as VPA, Karpenter, or EKS Auto Mode NodePools.

## Cleanup

From `sessions/05-production-scaling`:

```bash
kubectl delete -f subsessions/05-node-autoscaling/01-pending-pods-inflate.yml --ignore-not-found
kubectl delete -f subsessions/05-node-autoscaling/02-auto-mode-inflate.yml --ignore-not-found
kubectl delete -f subsessions/04-pdb-and-vpa-safety/ --ignore-not-found
kubectl delete -f subsessions/03-custom-external-metrics-hpa/ --ignore-not-found
kubectl delete -f subsessions/02-memory-hpa/ --ignore-not-found
kubectl delete -f subsessions/01-resource-guardrails/ --ignore-not-found
```

Provider-specific node autoscaler components such as Karpenter and Cluster Autoscaler should be removed only if they were installed just for this lesson.

## Review Questions

1. Why is HPA alone not enough when the cluster has no free node capacity?
2. What happens when ResourceQuota blocks new Pods?
3. Why can a LimitRange help teams use HPA safely?
4. Why is memory HPA different from CPU HPA in behavior?
5. When should an app scale on custom metrics instead of CPU or memory?
6. What kind of disruption does a PDB protect against?
7. What is the difference between Cluster Autoscaler and Karpenter?
8. What does EKS Auto Mode manage for you?
9. What should you check when Pods are Pending?

## References

- Kubernetes HPA documentation: `https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/`
- Kubernetes ResourceQuota documentation: `https://kubernetes.io/docs/concepts/policy/resource-quotas/`
- Kubernetes LimitRange documentation: `https://kubernetes.io/docs/concepts/policy/limit-range/`
- Kubernetes PDB documentation: `https://kubernetes.io/docs/tasks/run-application/configure-pdb/`
- Amazon EKS autoscaling overview: `https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html`
- Amazon EKS Cluster Autoscaler best practices: `https://docs.aws.amazon.com/eks/latest/best-practices/cas.html`
- Amazon EKS Karpenter best practices: `https://docs.aws.amazon.com/eks/latest/best-practices/karpenter.html`
- Karpenter getting started: `https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/`
- EKS Auto Mode: `https://docs.aws.amazon.com/eks/latest/userguide/automode.html`
- EKS Auto Mode sample workload: `https://docs.aws.amazon.com/eks/latest/userguide/automode-workload.html`
