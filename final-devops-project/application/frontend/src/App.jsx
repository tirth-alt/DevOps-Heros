import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api.js";

const EMPTY_FORM = { name: "", sku: "", category: "General", quantity: 0, price: 0, reorder_level: 10 };
const money = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(n || 0);

function StatCard({ label, value, tone }) {
  return (
    <div className={`stat stat-${tone}`}>
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
    </div>
  );
}

function ProductForm({ initial, onCancel, onSave, saving }) {
  const [form, setForm] = useState(initial);
  const set = (field) => (e) =>
    setForm({ ...form, [field]: e.target.type === "number" ? Number(e.target.value) : e.target.value });

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <form
        className="modal"
        onSubmit={(e) => {
          e.preventDefault();
          onSave(form);
        }}
      >
        <h2>{initial.id ? "Edit product" : "Add product"}</h2>
        <div className="form-grid">
          <label>Name<input required value={form.name} onChange={set("name")} /></label>
          <label>SKU<input required value={form.sku} onChange={set("sku")} /></label>
          <label>Category<input required value={form.category} onChange={set("category")} /></label>
          <label>Price (₹)<input type="number" min="0" step="0.01" value={form.price} onChange={set("price")} /></label>
          <label>Quantity<input type="number" min="0" value={form.quantity} onChange={set("quantity")} /></label>
          <label>Reorder level<input type="number" min="0" value={form.reorder_level} onChange={set("reorder_level")} /></label>
        </div>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onCancel}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Saving..." : "Save"}</button>
        </div>
      </form>
    </div>
  );
}

export default function App() {
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [lowOnly, setLowOnly] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const params = {};
      if (search) params.q = search;
      if (category) params.category = category;
      if (lowOnly) params.low_stock = "true";
      const [list, summary] = await Promise.all([api.listProducts(params), api.stats()]);
      setProducts(list);
      setStats(summary);
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [search, category, lowOnly]);

  useEffect(() => {
    const timer = setTimeout(load, 250);
    return () => clearTimeout(timer);
  }, [load]);

  const [allCategories, setAllCategories] = useState([]);
  useEffect(() => {
    api.listProducts({}).then((all) => setAllCategories([...new Set(all.map((p) => p.category))].sort())).catch(() => {});
  }, [products.length]);

  const run = async (action) => {
    try {
      await action();
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const save = async (form) => {
    setSaving(true);
    const { id, low_stock, created_at, updated_at, ...data } = form;
    await run(async () => {
      if (id) await api.updateProduct(id, data);
      else await api.createProduct(data);
      setEditing(null);
    });
    setSaving(false);
  };

  const remove = (product) => {
    if (window.confirm(`Delete ${product.name}?`)) run(() => api.deleteProduct(product.id));
  };

  const lowCount = useMemo(() => products.filter((p) => p.low_stock).length, [products]);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <img src="/favicon.svg" alt="" width="32" height="32" />
          <div>
            <h1>StockWise</h1>
            <p>Inventory dashboard</p>
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => setEditing(EMPTY_FORM)}>+ Add product</button>
      </header>

      <main>
        <section className="stats">
          <StatCard label="Products" value={stats?.total_products ?? "–"} tone="blue" />
          <StatCard label="Units in stock" value={stats?.total_units ?? "–"} tone="green" />
          <StatCard label="Inventory value" value={stats ? money(stats.inventory_value) : "–"} tone="purple" />
          <StatCard label="Low stock" value={stats?.low_stock_count ?? "–"} tone="red" />
        </section>

        <section className="toolbar">
          <input
            className="search"
            placeholder="Search by name or SKU"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {allCategories.map((c) => <option key={c}>{c}</option>)}
          </select>
          <label className="toggle">
            <input type="checkbox" checked={lowOnly} onChange={(e) => setLowOnly(e.target.checked)} />
            Low stock only
          </label>
        </section>

        {error && <div className="alert" role="alert">{error}<button onClick={() => setError("")}>×</button></div>}

        <section className="table-wrap">
          {loading ? (
            <p className="empty">Loading...</p>
          ) : products.length === 0 ? (
            <p className="empty">No products found. Add your first product.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Product</th><th>Category</th><th>Price</th><th>Stock</th><th>Status</th><th></th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td data-label="Product"><div className="product-cell"><strong>{p.name}</strong><span className="sku">{p.sku}</span></div></td>
                    <td data-label="Category">{p.category}</td>
                    <td data-label="Price">{money(p.price)}</td>
                    <td data-label="Stock">
                      <div className="stepper">
                        <button aria-label="Remove one" onClick={() => run(() => api.adjustStock(p.id, -1))} disabled={p.quantity === 0}>−</button>
                        <span>{p.quantity}</span>
                        <button aria-label="Add one" onClick={() => run(() => api.adjustStock(p.id, 1))}>+</button>
                      </div>
                    </td>
                    <td data-label="Status">
                      <span className={`badge ${p.low_stock ? "badge-low" : "badge-ok"}`}>
                        {p.low_stock ? `Reorder (≤ ${p.reorder_level})` : "In stock"}
                      </span>
                    </td>
                    <td className="actions">
                      <button className="btn btn-ghost" onClick={() => setEditing(p)}>Edit</button>
                      <button className="btn btn-danger" onClick={() => remove(p)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
        {!loading && products.length > 0 && (
          <p className="footnote">
            Showing {products.length} product{products.length === 1 ? "" : "s"}, {lowCount} need reordering.
          </p>
        )}
      </main>

      <footer>StockWise · Final DevOps Project · Tirth Shah (10316)</footer>

      {editing && <ProductForm initial={editing} saving={saving} onCancel={() => setEditing(null)} onSave={save} />}
    </div>
  );
}
