# Sub-Session 06: Ingress

This sub-session creates one Ingress that routes traffic to multiple internal Services.

## Routing

```text
/api/users -> user-service:5001
/api/apps  -> app-service:5002
/          -> frontend:80
```

The frontend and APIs are still `ClusterIP` Services. The Ingress controller creates and manages the external load balancer.

## Apply

From `sessions/03-ingress`:

```bash
kubectl apply -f subsessions/06-ingress/
```

## Check

```bash
kubectl get ingress -n app-ingress
kubectl describe ingress message-board-ingress -n app-ingress
```

Wait until an address appears:

```bash
kubectl get ingress message-board-ingress -n app-ingress
```

## Test

```bash
export APP_DNS=<ingress-address>

curl http://$APP_DNS/api/users
curl http://$APP_DNS/api/users/stats
curl http://$APP_DNS/api/apps
curl http://$APP_DNS/api/apps/stats
```

Open:

```text
http://<ingress-address>
```

If you own a custom domain, create a DNS record that points to the Ingress load balancer address.
