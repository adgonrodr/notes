# 1) Make it an internal LoadBalancer and pick the VNet subnet by NAME
kubectl -n ingress-nginx annotate svc ingress-nginx-controller \
  "service.beta.kubernetes.io/azure-load-balancer-internal=true" \
  "service.beta.kubernetes.io/azure-load-balancer-internal-subnet=<SUBNET_NAME>" \
  --overwrite

# 2) (Optional but recommended) assign a specific private IP in that subnet
kubectl -n ingress-nginx annotate svc ingress-nginx-controller \
  "service.beta.kubernetes.io/azure-load-balancer-ipv4=10.232.104.23" \
  --overwrite

# 3) Ensure Service type is LoadBalancer (and remove any spec.externalIPs misuse)
kubectl -n ingress-nginx patch svc ingress-nginx-controller \
  --type=json -p='[{"op":"remove","path":"/spec/externalIPs"}]'
kubectl -n ingress-nginx patch svc ingress-nginx-controller \
  -p '{"spec":{"type":"LoadBalancer"}}'

# 4) Watch it get an IP from your VNet/subnet
kubectl -n ingress-nginx get svc ingress-nginx-controller -w





kubectl -n ingress-nginx patch deploy ingress-nginx-controller --type merge -p '
spec:
  template:
    spec:
      securityContext:
        seccompProfile:
          type: RuntimeDefault
      volumes:
      - name: tmp
        emptyDir: {}
      - name: varcache
        emptyDir: {}
      - name: varrun
        emptyDir: {}
      containers:
      - name: controller
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
            add: ["NET_BIND_SERVICE"]
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: varcache
          mountPath: /var/cache/nginx
        - name: varrun
          mountPath: /var/run
'



# Add an ephemeral volume for the SSL dir and mount it
kubectl -n ingress-nginx patch deploy ingress-nginx-controller --type='json' -p='[
 {"op":"add","path":"/spec/template/spec/volumes/-","value":{"name":"ssl","emptyDir":{}}},
 {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-","value":{"name":"ssl","mountPath":"/etc/ingress-controller/ssl"}}
]'

# Rollout + check
kubectl -n ingress-nginx rollout status deploy/ingress-nginx-controller
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller | tail -n 50


# create or use your wildcard cert
kubectl -n ingress-nginx create secret tls default-ssl \
  --cert=your.crt --key=your.key

# tell the controller to use it (append an arg without touching existing ones)
kubectl -n ingress-nginx patch deploy ingress-nginx-controller --type='json' -p='[
 {"op":"add","path":"/spec/template/spec/containers/0/args","value":[]},
 {"op":"add","path":"/spec/template/spec/containers/0/args/-",
  "value":"--default-ssl-certificate=ingress-nginx/default-ssl"}
]'

kubectl -n ingress-nginx rollout status deploy/ingress-nginx-controller


kubectl -n ingress-nginx patch deploy ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/env","value":[
    {"name":"POD_NAME","valueFrom":{"fieldRef":{"fieldPath":"metadata.name"}}},
    {"name":"POD_NAMESPACE","valueFrom":{"fieldRef":{"fieldPath":"metadata.namespace"}}},
    {"name":"POD_IP","valueFrom":{"fieldRef":{"fieldPath":"status.podIP"}}}
  ]}
]'