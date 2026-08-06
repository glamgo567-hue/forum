import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { planVote } from "../api/voting";
import { useAuth } from "../context/AuthContext";
import {
  Alert,
  Button,
  Byline,
  Empty,
  Input,
  LinkButton,
  Spinner,
  TagPill,
  VoteRail,
} from "../components/ui";

const PAGE_SIZE = 10;

export default function QuestionsPage() {
  const { user, refreshUser } = useAuth();
  const [params, setParams] = useSearchParams();
  const tag = params.get("tag");
  const page = Math.max(0, Number(params.get("page") ?? 0));

  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setQuestions(await api.listQuestions({ skip: page * PAGE_SIZE, limit: PAGE_SIZE, tag }));
    } catch (err) {
      setError(err.detail);
    } finally {
      setLoading(false);
    }
  }, [page, tag]);

  useEffect(() => {
    load();
  }, [load]);

  function setParam(key, value) {
    const next = new URLSearchParams(params);
    if (value === null) next.delete(key);
    else next.set(key, value);
    if (key !== "page") next.delete("page");
    setParams(next);
  }

  async function handleVote(question, direction) {
    const plan = planVote(question.my_vote, direction);
    const before = questions;
    setQuestions((qs) =>
      qs.map((q) =>
        q.id === question.id
          ? { ...q, score: q.score + plan.delta, my_vote: plan.nextVote }
          : q,
      ),
    );
    try {
      await api.voteQuestion(question.id, plan.method, plan.value);
      refreshUser();
    } catch (err) {
      setQuestions(before);
      setError(err.detail);
    }
  }

  // The API has no search parameter, so this narrows the page already loaded.
  const term = search.trim().toLowerCase();
  const visible = term
    ? questions.filter(
        (q) =>
          q.title.toLowerCase().includes(term) ||
          q.tags.some((t) => t.name.toLowerCase().includes(term)),
      )
    : questions;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="font-serif text-2xl font-semibold text-bark-900">
          {tag ? `Questions tagged ${tag}` : "Latest questions"}
        </h1>
        <div className="ml-auto w-full sm:w-64">
          <Input
            type="search"
            placeholder="Filter this page"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Filter questions on this page"
          />
        </div>
      </div>

      {tag && (
        <div className="flex items-center gap-2 text-sm text-bark-500">
          <TagPill name={tag} active />
          <button
            type="button"
            onClick={() => setParam("tag", null)}
            className="text-bark-500 underline-offset-2 hover:text-bark-900 hover:underline"
          >
            clear filter
          </button>
        </div>
      )}

      <Alert>{error}</Alert>

      {loading ? (
        <Spinner label="Loading questions…" />
      ) : visible.length === 0 ? (
        <Empty
          title={term ? "Nothing matches that filter" : "No questions here yet"}
          body={
            term
              ? "Filtering only looks at the questions on this page."
              : "Be the first to ask one."
          }
          action={
            !term && (
              <LinkButton to={user ? "/ask" : "/login"}>Ask question</LinkButton>
            )
          }
        />
      ) : (
        <ul className="space-y-2.5">
          {visible.map((question) => (
            <li
              key={question.id}
              className="flex gap-4 rounded-xl border border-sand-200 bg-white px-5 py-4"
            >
              <VoteRail
                score={question.score}
                myVote={question.my_vote}
                disabled={!user || user.id === question.author_id}
                onVote={(direction) => handleVote(question, direction)}
              />
              <div className="min-w-0 flex-1">
                <Link
                  to={`/questions/${question.id}`}
                  className="font-serif text-base font-medium text-bark-900 hover:text-clay-700"
                >
                  {question.title}
                </Link>
                <p className="mt-1 line-clamp-2 text-sm text-bark-500">{question.body}</p>
                {question.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {question.tags.map((t) => (
                      <TagPill
                        key={t.id}
                        name={t.name}
                        active={t.name === tag}
                        onClick={() => setParam("tag", t.name)}
                      />
                    ))}
                  </div>
                )}
                <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs text-bark-500">
                    {question.answer_count}{" "}
                    {question.answer_count === 1 ? "answer" : "answers"}
                  </span>
                  <Byline username={question.author_username} when={question.created_at} />
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div className="flex items-center justify-between pt-2">
        <Button
          variant="ghost"
          disabled={page === 0}
          onClick={() => setParam("page", page - 1)}
        >
          Newer
        </Button>
        <span className="font-mono text-xs text-bark-500">page {page + 1}</span>
        <Button
          variant="ghost"
          disabled={questions.length < PAGE_SIZE}
          onClick={() => setParam("page", page + 1)}
        >
          Older
        </Button>
      </div>
    </div>
  );
}
