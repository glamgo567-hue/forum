import { Link } from "react-router-dom";

const buttonBase =
  "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50";

const buttonVariants = {
  primary: "bg-clay-300 text-clay-800 hover:bg-clay-400",
  ghost: "border border-sand-200 bg-white text-bark-900 hover:bg-sand-50",
  quiet: "text-bark-500 hover:text-bark-900",
  danger: "border border-sand-200 bg-white text-clay-700 hover:bg-sand-100",
};

export function Button({ variant = "primary", className = "", ...props }) {
  return <button className={`${buttonBase} ${buttonVariants[variant]} ${className}`} {...props} />;
}

// Buttons that navigate have to render as a single anchor. Wrapping <Button>
// in a <Link> produces <a><button></a>, which is invalid HTML and gives the
// browser two nested interactive elements to reason about.
export function LinkButton({ to, variant = "primary", className = "", children, ...props }) {
  return (
    <Link to={to} className={`${buttonBase} ${buttonVariants[variant]} ${className}`} {...props}>
      {children}
    </Link>
  );
}

export function Field({ label, hint, children }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-bark-900">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-bark-500">{hint}</span>}
    </label>
  );
}

const inputBase =
  "w-full rounded-lg border border-sand-200 bg-white px-3 py-2 text-sm text-bark-900 placeholder:text-bark-400 focus:border-clay-400 focus:outline-none";

export function Input(props) {
  return <input className={inputBase} {...props} />;
}

export function Textarea({ className = "", ...props }) {
  return <textarea className={`${inputBase} resize-y ${className}`} {...props} />;
}

export function TagPill({ name, onClick, active = false }) {
  const styles = active
    ? "bg-clay-300 text-clay-800"
    : "bg-sand-100 text-clay-700 hover:bg-sand-300";
  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${styles}`}
      >
        {name}
      </button>
    );
  }
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${styles}`}>{name}</span>
  );
}

export function Alert({ children, tone = "error" }) {
  if (!children) return null;
  const tones = {
    error: "border-clay-300 bg-sand-100 text-clay-800",
    info: "border-sand-200 bg-white text-bark-700",
  };
  return (
    <div className={`rounded-lg border px-3 py-2 text-sm ${tones[tone]}`} role="alert">
      {children}
    </div>
  );
}

export function Spinner({ label = "Loading…" }) {
  return <p className="py-10 text-center text-sm text-bark-500">{label}</p>;
}

export function Empty({ title, body, action }) {
  return (
    <div className="rounded-xl border border-sand-200 bg-white px-6 py-12 text-center">
      <p className="font-serif text-lg text-bark-900">{title}</p>
      {body && <p className="mt-1 text-sm text-bark-500">{body}</p>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  );
}

export function Reputation({ value }) {
  return <span className="font-mono text-bark-700">{value} rep</span>;
}

export function AcceptedBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-sage-100 px-2.5 py-0.5 text-xs font-medium text-sage-700">
      <CheckIcon /> accepted
    </span>
  );
}

export function CheckIcon({ className = "h-3.5 w-3.5" }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path
        fillRule="evenodd"
        d="M16.7 5.3a1 1 0 0 1 0 1.4l-7.5 7.5a1 1 0 0 1-1.4 0L3.3 9.7a1 1 0 1 1 1.4-1.4l3.8 3.8 6.8-6.8a1 1 0 0 1 1.4 0Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function relativeTime(iso) {
  // The API returns naive UTC timestamps, so pin them to UTC before comparing.
  const stamp = /[Zz+]|-\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`;
  const seconds = Math.round((Date.now() - new Date(stamp).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const units = [
    ["m", 60],
    ["h", 3600],
    ["d", 86400],
  ];
  let label = `${Math.round(seconds / 60)}m ago`;
  for (const [suffix, size] of units) {
    if (seconds >= size) label = `${Math.floor(seconds / size)}${suffix} ago`;
  }
  if (seconds >= 2592000) return new Date(stamp).toLocaleDateString();
  return label;
}

export function joinedOn(iso) {
  const stamp = /[Zz+]|-\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`;
  return new Date(stamp).toLocaleDateString(undefined, { year: "numeric", month: "long" });
}

export function Byline({ username, when, prefix = "asked by" }) {
  return (
    <span className="text-xs text-bark-500">
      {prefix} <span className="text-bark-700">{username}</span> · {relativeTime(when)}
    </span>
  );
}

export function VoteRail({ score, myVote, onVote, disabled, size = "md" }) {
  const arrow = (direction) => {
    const active = myVote === direction;
    const cls = active ? "text-clay-700" : "text-bark-400";
    return (
      <button
        type="button"
        disabled={disabled}
        onClick={() => onVote(direction)}
        aria-label={direction === 1 ? "Upvote" : "Downvote"}
        aria-pressed={active}
        className={`rounded transition-colors hover:text-clay-700 disabled:hover:text-bark-400 ${cls} ${
          disabled ? "cursor-not-allowed" : ""
        }`}
      >
        <svg
          className={size === "sm" ? "h-4 w-4" : "h-5 w-5"}
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          {direction === 1 ? (
            <path d="M10 4.5 3.5 12h13L10 4.5Z" />
          ) : (
            <path d="M10 15.5 3.5 8h13L10 15.5Z" />
          )}
        </svg>
      </button>
    );
  };

  return (
    <div className="flex w-8 shrink-0 flex-col items-center gap-0.5">
      {arrow(1)}
      <span className="font-mono text-sm font-medium text-bark-900">{score}</span>
      {arrow(-1)}
    </div>
  );
}

export function BackLink({ to, children }) {
  return (
    <Link to={to} className="text-sm text-bark-500 transition-colors hover:text-bark-900">
      ← {children}
    </Link>
  );
}
