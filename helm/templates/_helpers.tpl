{{- define "synkronized.pod.resources" }}

{{- if eq .Values.size "micro" }}
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "250m"
{{- else if eq .Values.size "small" }}
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "1024Mi"
    cpu: "500m"
{{- else if eq .Values.size "medium" }}
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "2048Mi"
    cpu: "1"
{{- else if eq .Values.size "large" }}
resources:
  requests:
    memory: "512Mi"
    cpu: "1"
  limits:
    memory: "4096Mi"
    cpu: "2"
{{- else }}
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "1024Mi"
    cpu: "500m"
{{- end }}

{{- end }}