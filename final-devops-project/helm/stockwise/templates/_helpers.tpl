{{- define "stockwise.name" -}}{{ .Chart.Name }}{{- end -}}

{{- define "stockwise.fullname" -}}
{{- if contains .Chart.Name .Release.Name -}}{{ .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else -}}{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}{{- end -}}
{{- end -}}

{{- define "stockwise.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
app.kubernetes.io/part-of: {{ include "stockwise.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/* Selector labels for one component: pass (dict "ctx" $ "component" "backend") */}}
{{- define "stockwise.selectorLabels" -}}
app.kubernetes.io/name: {{ include "stockwise.name" .ctx }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "stockwise.backendName" -}}{{ include "stockwise.fullname" . }}-backend{{- end -}}
{{- define "stockwise.frontendName" -}}{{ include "stockwise.fullname" . }}-frontend{{- end -}}
{{- define "stockwise.postgresName" -}}{{ include "stockwise.fullname" . }}-postgres{{- end -}}

{{- define "stockwise.secretName" -}}
{{- if .Values.postgres.existingSecret -}}{{ .Values.postgres.existingSecret }}
{{- else -}}{{ include "stockwise.fullname" . }}-db{{- end -}}
{{- end -}}

{{- define "stockwise.backendImage" -}}
{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}
{{- end -}}

{{- define "stockwise.frontendImage" -}}
{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Chart.AppVersion }}
{{- end -}}

{{/* Environment shared by the backend and the migration job */}}
{{- define "stockwise.dbEnv" -}}
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "stockwise.secretName" . }}
      key: {{ .Values.postgres.existingSecretKey }}
- name: DATABASE_URL
  value: "postgresql+psycopg://{{ .Values.postgres.username }}:$(DB_PASSWORD)@{{ include "stockwise.postgresName" . }}:5432/{{ .Values.postgres.database }}"
{{- end -}}

{{- define "stockwise.containerSecurity" -}}
allowPrivilegeEscalation: false
runAsNonRoot: true
capabilities:
  drop: ["ALL"]
{{- end -}}
