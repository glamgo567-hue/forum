import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Alert, Button, Field, Input } from "../components/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username, password);
      navigate(location.state?.from ?? "/", { replace: true });
    } catch (err) {
      setError(err.detail);
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm space-y-5">
      <h1 className="font-serif text-2xl font-semibold text-bark-900">Log in</h1>
      <Alert>{error}</Alert>
      <form onSubmit={submit} className="space-y-4 rounded-xl border border-sand-200 bg-white px-5 py-5">
        <Field label="Username">
          <Input value={username} required autoComplete="username" onChange={(e) => setUsername(e.target.value)} />
        </Field>
        <Field label="Password">
          <Input type="password" value={password} required autoComplete="current-password" onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? "Logging in…" : "Log in"}
        </Button>
      </form>
      <p className="text-center text-sm text-bark-500">
        No account yet?{" "}
        <Link to="/register" className="text-clay-700 hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
