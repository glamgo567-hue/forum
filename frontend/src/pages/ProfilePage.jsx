import { useAuth } from "../context/AuthContext";
import { joinedOn } from "../components/ui";

export default function ProfilePage() {
  const { user } = useAuth();
  if (!user) return null;

  const stats = [
    { label: "Reputation", value: user.reputation },
    { label: "Member since", value: joinedOn(user.created_at) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-clay-300 font-serif text-xl font-semibold text-clay-800">
          {user.username.slice(0, 2).toLowerCase()}
        </div>
        <div>
          <h1 className="font-serif text-2xl font-semibold text-bark-900">{user.username}</h1>
          <p className="text-sm text-bark-500">{user.email}</p>
        </div>
      </div>

      <dl className="grid gap-3 sm:grid-cols-2">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-xl border border-sand-200 bg-white px-5 py-4">
            <dt className="text-xs text-bark-500">{stat.label}</dt>
            <dd className="mt-1 font-mono text-xl text-bark-900">{stat.value}</dd>
          </div>
        ))}
      </dl>

      <p className="text-sm text-bark-500">
        Reputation follows votes on your posts: an upvote gives 10 on an answer and 5 on a
        question, and 20 more the first time one of your answers is accepted. A downvote costs 5
        either way.
      </p>
    </div>
  );
}
