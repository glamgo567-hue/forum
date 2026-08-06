import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { Alert, Button, Field, Input } from "../components/ui";

export default function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "", confirm_password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    if (form.password !== form.confirm_password) {
      setError("Those passwords don't match.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api.register(form);
      await login(form.username, form.password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.detail);
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm space-y-5">
      <h1 className="font-serif text-2xl font-semibold text-bark-900">Create an account</h1>
      <Alert>{error}</Alert>
      <form onSubmit={submit} className="space-y-4 rounded-xl border border-sand-200 bg-white px-5 py-5">
        <Field label="Username" hint="3 characters or more.">
          <Input value={form.username} required minLength={3} maxLength={100} autoComplete="username" onChange={set("username")} />
        </Field>
        <Field label="Email">
          <Input type="email" value={form.email} required autoComplete="email" onChange={set("email")} />
        </Field>
        <Field label="Password" hint="8 characters or more.">
          <Input type="password" value={form.password} required minLength={8} autoComplete="new-password" onChange={set("password")} />
        </Field>
        <Field label="Confirm password">
          <Input type="password" value={form.confirm_password} required minLength={8} autoComplete="new-password" onChange={set("confirm_password")} />
        </Field>
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? "Creating account…" : "Create account"}
        </Button>
      </form>
      <p className="text-center text-sm text-bark-500">
        Already registered?{" "}
        <Link to="/login" className="text-clay-700 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
