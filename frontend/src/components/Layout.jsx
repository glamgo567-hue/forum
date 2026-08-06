import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button, LinkButton, Reputation } from "./ui";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-sand-50">
      <header className="sticky top-0 z-10 border-b border-sand-200 bg-sand-50/90 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center gap-4 px-4 py-3">
          <Link to="/" className="font-serif text-lg font-semibold text-bark-900">
            devforum
          </Link>

          <nav className="hidden gap-1 sm:flex">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `rounded-lg px-2.5 py-1.5 text-sm transition-colors ${
                  isActive ? "text-bark-900" : "text-bark-500 hover:text-bark-900"
                }`
              }
            >
              Questions
            </NavLink>
          </nav>

          <div className="ml-auto flex items-center gap-3">
            {user ? (
              <>
                <Link
                  to="/profile"
                  className="hidden text-sm text-bark-700 transition-colors hover:text-bark-900 sm:block"
                >
                  {user.username} · <Reputation value={user.reputation} />
                </Link>
                <LinkButton to="/ask">Ask question</LinkButton>
                <Button variant="quiet" onClick={handleLogout}>
                  Log out
                </Button>
              </>
            ) : (
              <>
                <LinkButton to="/login" variant="quiet">
                  Log in
                </LinkButton>
                <LinkButton to="/register">Sign up</LinkButton>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8">
        <Outlet />
      </main>

      <footer className="mx-auto max-w-4xl px-4 pb-10 text-xs text-bark-400">
        devforum — a FastAPI portfolio project
      </footer>
    </div>
  );
}
