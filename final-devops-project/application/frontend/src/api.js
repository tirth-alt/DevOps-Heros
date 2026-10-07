// All calls use relative /api paths. Nginx (Docker) or the Ingress (Kubernetes)
// routes them to the FastAPI backend, so the frontend never needs the backend's address.
async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (response.status === 204) return null;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join(", ") : body.detail;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return body;
}

export const api = {
  listProducts: (params) => request(`/products?${new URLSearchParams(params)}`),
  stats: () => request("/stats"),
  createProduct: (data) => request("/products", { method: "POST", body: JSON.stringify(data) }),
  updateProduct: (id, data) => request(`/products/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  adjustStock: (id, change) => request(`/products/${id}/stock`, { method: "PATCH", body: JSON.stringify({ change }) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: "DELETE" }),
};
