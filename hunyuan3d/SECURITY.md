# Security Policy and Best Practices

## Container Security

### 1. Base Image Security

The Docker image is based on `nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04`:
- Official NVIDIA image with security updates
- Ubuntu 22.04 LTS with long-term support
- Regular security patches applied

### 2. Non-Root User

Container runs as non-root user `hunyuan` (UID 1000):
```dockerfile
USER hunyuan
```

**Benefits:**
- Prevents privilege escalation attacks
- Limits access to host resources
- Follows principle of least privilege

### 3. Capabilities

All Linux capabilities are dropped:
```yaml
capabilities:
  drop:
  - ALL
```

Only add back capabilities if absolutely necessary.

### 4. Read-Only Root Filesystem

While not fully read-only (due to model caching needs), sensitive directories are protected:
```yaml
readOnlyRootFilesystem: false  # Models need cache write access
```

**Writable directories:**
- `/cache` - Model and cache storage
- `/models` - Model weights
- `/tmp` - Temporary files

### 5. Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  allowPrivilegeEscalation: false
  seccompProfile:
    type: RuntimeDefault
```

## Image Scanning

### Using Trivy

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image for vulnerabilities
trivy image hunyuan3d:latest

# Scan with specific severity
trivy image --severity HIGH,CRITICAL hunyuan3d:latest

# Generate report
trivy image --format json --output report.json hunyuan3d:latest
```

### Using Grype

```bash
# Install Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan image
grype hunyuan3d:latest
```

### Using Docker Scout

```bash
# Enable Docker Scout
docker scout quickview hunyuan3d:latest

# Get detailed CVE report
docker scout cves hunyuan3d:latest
```

## Kubernetes Security

### 1. Pod Security Standards

Apply pod security standards to namespace:

```bash
kubectl label namespace hunyuan3d \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

**Note:** Use `baseline` instead of `restricted` if you encounter compatibility issues with GPU workloads.

### 2. Network Policies

Restrict network traffic (included in deployment.yaml):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hunyuan3d-netpol
spec:
  podSelector:
    matchLabels:
      app: hunyuan3d
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 7860
  egress:
  # DNS
  - ports:
    - protocol: UDP
      port: 53
  # HTTPS for model downloads
  - ports:
    - protocol: TCP
      port: 443
```

### 3. Secrets Management

**Never commit secrets to Git.**

#### Create secrets securely:

```bash
# From file
kubectl create secret generic hf-token \
  --from-file=token=/path/to/token/file \
  --namespace hunyuan3d

# From literal
kubectl create secret generic hf-token \
  --from-literal=token=YOUR_TOKEN \
  --namespace hunyuan3d
```

#### Use external secret managers:

- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Secret Manager**

Example with External Secrets Operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: hf-token
  namespace: hunyuan3d
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: hf-token
  data:
  - secretKey: token
    remoteRef:
      key: hunyuan3d/hf-token
```

### 4. RBAC (Role-Based Access Control)

Create service account with minimal permissions:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hunyuan3d
  namespace: hunyuan3d
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: hunyuan3d-role
  namespace: hunyuan3d
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: hunyuan3d-rolebinding
  namespace: hunyuan3d
subjects:
- kind: ServiceAccount
  name: hunyuan3d
  namespace: hunyuan3d
roleRef:
  kind: Role
  name: hunyuan3d-role
  apiGroup: rbac.authorization.k8s.io
```

### 5. Resource Quotas

Limit resource consumption:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: hunyuan3d-quota
  namespace: hunyuan3d
spec:
  hard:
    requests.cpu: "32"
    requests.memory: 128Gi
    requests.nvidia.com/gpu: "4"
    limits.cpu: "64"
    limits.memory: 256Gi
    limits.nvidia.com/gpu: "4"
    persistentvolumeclaims: "10"
```

### 6. Limit Ranges

Set default limits:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: hunyuan3d-limits
  namespace: hunyuan3d
spec:
  limits:
  - max:
      memory: 64Gi
      cpu: "16"
    min:
      memory: 4Gi
      cpu: "1"
    default:
      memory: 32Gi
      cpu: "8"
    defaultRequest:
      memory: 16Gi
      cpu: "4"
    type: Container
```

## TLS/HTTPS Configuration

### Using Cert-Manager

1. **Install cert-manager:**

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

2. **Create ClusterIssuer:**

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

3. **Update Ingress for TLS:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hunyuan3d
  namespace: hunyuan3d
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - hunyuan3d.example.com
    secretName: hunyuan3d-tls
  rules:
  - host: hunyuan3d.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hunyuan3d
            port:
              number: 80
```

## Audit Logging

Enable Kubernetes audit logging for security monitoring:

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  namespaces: ["hunyuan3d"]
  verbs: ["create", "update", "patch", "delete"]
  resources:
  - group: ""
    resources: ["pods", "secrets", "configmaps"]
```

## Compliance Checks

### CIS Kubernetes Benchmark

Run kube-bench for CIS compliance:

```bash
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs -f job/kube-bench
```

### Policy Enforcement with OPA/Gatekeeper

Example policy to enforce security constraints:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

## Incident Response

### 1. Monitor for Anomalies

- Watch for unusual network traffic
- Monitor resource consumption spikes
- Track failed authentication attempts
- Review audit logs regularly

### 2. Container Breakout Prevention

- Keep kernel and container runtime updated
- Use AppArmor or SELinux profiles
- Enable seccomp filtering
- Monitor for privilege escalation attempts

### 3. Emergency Procedures

If container is compromised:

```bash
# Isolate pod
kubectl label pod <pod-name> -n hunyuan3d quarantine=true

# Apply network policy to block traffic
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine
  namespace: hunyuan3d
spec:
  podSelector:
    matchLabels:
      quarantine: "true"
  policyTypes:
  - Ingress
  - Egress
EOF

# Collect forensics
kubectl exec -n hunyuan3d <pod-name> -- ps aux
kubectl exec -n hunyuan3d <pod-name> -- netstat -an
kubectl logs -n hunyuan3d <pod-name> > incident-logs.txt

# Delete compromised pod
kubectl delete pod -n hunyuan3d <pod-name>
```

## Security Checklist

- [ ] Image scanned for vulnerabilities
- [ ] Running as non-root user
- [ ] All capabilities dropped
- [ ] Resource limits configured
- [ ] Network policies applied
- [ ] Secrets externalized (not in Git)
- [ ] TLS/HTTPS enabled for production
- [ ] RBAC configured with least privilege
- [ ] Pod security standards enforced
- [ ] Audit logging enabled
- [ ] Regular security updates scheduled
- [ ] Incident response plan documented
- [ ] Backup and recovery tested
- [ ] Monitoring and alerting configured

## Regular Maintenance

### Monthly Tasks

- [ ] Review and update dependencies
- [ ] Scan images for new vulnerabilities
- [ ] Review access logs and audit trails
- [ ] Update base image to latest patch
- [ ] Review and rotate secrets
- [ ] Test backup and restore procedures

### Quarterly Tasks

- [ ] Security audit by external team
- [ ] Penetration testing
- [ ] Review and update security policies
- [ ] Compliance certification review
- [ ] Disaster recovery drill

## References

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [OWASP Docker Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [NIST Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** open a public issue
2. Email security@example.com with details
3. Include steps to reproduce
4. Allow time for patch before disclosure
