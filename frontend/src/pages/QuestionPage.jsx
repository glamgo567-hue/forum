import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import { planVote } from "../api/voting";
import { useAuth } from "../context/AuthContext";
import {
  AcceptedBadge,
  Alert,
  BackLink,
  Button,
  Byline,
  CheckIcon,
  Field,
  Input,
  Spinner,
  TagPill,
  Textarea,
  VoteRail,
} from "../components/ui";

export default function QuestionPage() {
  const { id } = useParams();
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();

  const [question, setQuestion] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({ title: "", body: "" });
  const [newAnswer, setNewAnswer] = useState("");
  const [posting, setPosting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [q, a] = await Promise.all([api.getQuestion(id), api.listAnswers(id)]);
      setQuestion(q);
      setAnswers(a);
      setDraft({ title: q.title, body: q.body });
    } catch (err) {
      setError(err.detail);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const isAuthor = user && question && user.id === question.author_id;

  async function voteQuestion(direction) {
    const plan = planVote(question.my_vote, direction);
    const before = question;
    setQuestion({ ...question, score: question.score + plan.delta, my_vote: plan.nextVote });
    try {
      await api.voteQuestion(question.id, plan.method, plan.value);
      refreshUser();
    } catch (err) {
      setQuestion(before);
      setError(err.detail);
    }
  }

  async function voteAnswer(answer, direction) {
    const plan = planVote(answer.my_vote, direction);
    const before = answers;
    setAnswers((list) =>
      list.map((a) =>
        a.id === answer.id ? { ...a, score: a.score + plan.delta, my_vote: plan.nextVote } : a,
      ),
    );
    try {
      await api.voteAnswer(answer.id, plan.method, plan.value);
      refreshUser();
    } catch (err) {
      setAnswers(before);
      setError(err.detail);
    }
  }

  async function acceptAnswer(answerId) {
    setError("");
    try {
      await api.acceptAnswer(answerId);
      // Accepting clears the flag on the previously accepted answer server-side,
      // and the list is ordered accepted-first, so refetch instead of patching locally.
      setAnswers(await api.listAnswers(id));
      refreshUser();
    } catch (err) {
      setError(err.detail);
    }
  }

  async function saveQuestion(e) {
    e.preventDefault();
    setError("");
    try {
      setQuestion(await api.updateQuestion(id, draft));
      setEditing(false);
    } catch (err) {
      setError(err.detail);
    }
  }

  async function removeQuestion() {
    if (!window.confirm("Delete this question and all of its answers?")) return;
    try {
      await api.deleteQuestion(id);
      navigate("/");
    } catch (err) {
      setError(err.detail);
    }
  }

  async function submitAnswer(e) {
    e.preventDefault();
    if (!newAnswer.trim()) return;
    setPosting(true);
    setError("");
    try {
      const created = await api.createAnswer(id, { body: newAnswer.trim() });
      setAnswers((list) => [...list, created]);
      setQuestion((q) => ({ ...q, answer_count: q.answer_count + 1 }));
      setNewAnswer("");
    } catch (err) {
      setError(err.detail);
    } finally {
      setPosting(false);
    }
  }

  if (loading) return <Spinner label="Loading question…" />;
  if (!question) return <Alert>{error || "Question not found"}</Alert>;

  return (
    <div className="space-y-6">
      <BackLink to="/">All questions</BackLink>
      <Alert>{error}</Alert>

      <article className="flex gap-4 rounded-xl border border-sand-200 bg-white px-5 py-5">
        <VoteRail
          score={question.score}
          myVote={question.my_vote}
          disabled={!user || isAuthor}
          onVote={voteQuestion}
        />
        <div className="min-w-0 flex-1">
          {editing ? (
            <form onSubmit={saveQuestion} className="space-y-3">
              <Field label="Title">
                <Input
                  value={draft.title}
                  maxLength={100}
                  required
                  onChange={(e) => setDraft({ ...draft, title: e.target.value })}
                />
              </Field>
              <Field label="Body">
                <Textarea
                  rows={8}
                  value={draft.body}
                  required
                  onChange={(e) => setDraft({ ...draft, body: e.target.value })}
                />
              </Field>
              <div className="flex gap-2">
                <Button type="submit">Save changes</Button>
                <Button type="button" variant="ghost" onClick={() => setEditing(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <>
              <h1 className="font-serif text-2xl font-semibold text-bark-900">
                {question.title}
              </h1>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-bark-900">
                {question.body}
              </p>
              {question.tags.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {question.tags.map((t) => (
                    <Link key={t.id} to={`/?tag=${encodeURIComponent(t.name)}`}>
                      <TagPill name={t.name} />
                    </Link>
                  ))}
                </div>
              )}
              <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-sand-200 pt-3">
                <Byline username={question.author_username} when={question.created_at} />
                {isAuthor && (
                  <div className="ml-auto flex gap-2">
                    <Button variant="ghost" onClick={() => setEditing(true)}>
                      Edit
                    </Button>
                    <Button variant="danger" onClick={removeQuestion}>
                      Delete
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </article>

      <section className="space-y-3">
        <h2 className="font-serif text-lg font-medium text-bark-900">
          {answers.length} {answers.length === 1 ? "answer" : "answers"}
        </h2>

        {answers.map((answer) => (
          <AnswerCard
            key={answer.id}
            answer={answer}
            user={user}
            canAccept={isAuthor && user.id !== answer.author_id}
            onVote={(direction) => voteAnswer(answer, direction)}
            onAccept={() => acceptAnswer(answer.id)}
            onChanged={(updated) =>
              setAnswers((list) => list.map((a) => (a.id === updated.id ? updated : a)))
            }
            onDeleted={() => {
              setAnswers((list) => list.filter((a) => a.id !== answer.id));
              setQuestion((q) => ({ ...q, answer_count: q.answer_count - 1 }));
            }}
            onError={setError}
          />
        ))}
      </section>

      {user ? (
        <form onSubmit={submitAnswer} className="space-y-3 rounded-xl border border-sand-200 bg-white px-5 py-5">
          <Field label="Your answer">
            <Textarea
              rows={6}
              value={newAnswer}
              placeholder="Explain what worked and why."
              onChange={(e) => setNewAnswer(e.target.value)}
            />
          </Field>
          <Button type="submit" disabled={posting || !newAnswer.trim()}>
            {posting ? "Posting…" : "Post answer"}
          </Button>
        </form>
      ) : (
        <div className="rounded-xl border border-sand-200 bg-white px-5 py-5 text-sm text-bark-500">
          <Link to="/login" className="text-clay-700 hover:underline">
            Log in
          </Link>{" "}
          to answer this question.
        </div>
      )}
    </div>
  );
}

function AnswerCard({ answer, user, canAccept, onVote, onAccept, onChanged, onDeleted, onError }) {
  const [editing, setEditing] = useState(false);
  const [body, setBody] = useState(answer.body);
  const isAuthor = user && user.id === answer.author_id;

  async function save(e) {
    e.preventDefault();
    try {
      onChanged(await api.updateAnswer(answer.id, { body }));
      setEditing(false);
    } catch (err) {
      onError(err.detail);
    }
  }

  async function remove() {
    if (!window.confirm("Delete this answer?")) return;
    try {
      await api.deleteAnswer(answer.id);
      onDeleted();
    } catch (err) {
      onError(err.detail);
    }
  }

  return (
    <article
      className={`flex gap-4 rounded-xl border bg-white px-5 py-4 ${
        answer.is_accepted ? "border-sage-700/30" : "border-sand-200"
      }`}
    >
      <div className="flex flex-col items-center gap-2">
        <VoteRail
          score={answer.score}
          myVote={answer.my_vote}
          disabled={!user || isAuthor}
          onVote={onVote}
          size="sm"
        />
        {canAccept && (
          <button
            type="button"
            onClick={onAccept}
            aria-label="Accept this answer"
            title={answer.is_accepted ? "Accepted" : "Accept this answer"}
            className={`rounded-full p-1 transition-colors ${
              answer.is_accepted
                ? "bg-sage-100 text-sage-700"
                : "text-bark-400 hover:bg-sage-100 hover:text-sage-700"
            }`}
          >
            <CheckIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="min-w-0 flex-1">
        {editing ? (
          <form onSubmit={save} className="space-y-3">
            <Textarea rows={6} value={body} required onChange={(e) => setBody(e.target.value)} />
            <div className="flex gap-2">
              <Button type="submit">Save changes</Button>
              <Button type="button" variant="ghost" onClick={() => setEditing(false)}>
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <>
            {answer.is_accepted && (
              <div className="mb-2">
                <AcceptedBadge />
              </div>
            )}
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-bark-900">
              {answer.body}
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-3 border-t border-sand-200 pt-2.5">
              <Byline
                username={answer.author_username}
                when={answer.created_at}
                prefix="answered by"
              />
              {isAuthor && (
                <div className="ml-auto flex gap-2">
                  <Button variant="ghost" onClick={() => setEditing(true)}>
                    Edit
                  </Button>
                  <Button variant="danger" onClick={remove}>
                    Delete
                  </Button>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </article>
  );
}
