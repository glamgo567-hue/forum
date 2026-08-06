import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Alert, BackLink, Button, Field, Input, TagPill, Textarea } from "../components/ui";

export default function AskPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function addTag(raw) {
    const name = raw.trim().toLowerCase();
    if (!name) return;
    if (tags.includes(name)) {
      setTagInput("");
      return;
    }
    if (tags.length >= 5) {
      setError("A question can carry at most 5 tags.");
      return;
    }
    setTags([...tags, name]);
    setTagInput("");
  }

  function handleTagKey(e) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(tagInput);
    } else if (e.key === "Backspace" && !tagInput && tags.length > 0) {
      setTags(tags.slice(0, -1));
    }
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      // Tags typed but not committed with Enter should still count.
      const pending = tagInput.trim().toLowerCase();
      const finalTags = pending && !tags.includes(pending) ? [...tags, pending] : tags;
      const created = await api.createQuestion({ title, body, tags: finalTags });
      navigate(`/questions/${created.id}`);
    } catch (err) {
      setError(err.detail);
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <BackLink to="/">All questions</BackLink>
      <h1 className="font-serif text-2xl font-semibold text-bark-900">Ask a question</h1>
      <Alert>{error}</Alert>

      <form onSubmit={submit} className="space-y-5 rounded-xl border border-sand-200 bg-white px-5 py-5">
        <Field label="Title" hint={`${title.length}/100 — be specific about the problem`}>
          <Input
            value={title}
            maxLength={100}
            required
            placeholder="Why does asyncpg hang on connection close?"
            onChange={(e) => setTitle(e.target.value)}
          />
        </Field>

        <Field label="Details" hint="What you tried, what happened, what you expected.">
          <Textarea
            rows={10}
            value={body}
            required
            placeholder="Include the relevant code and the exact error."
            onChange={(e) => setBody(e.target.value)}
          />
        </Field>

        <Field label="Tags" hint="Press Enter or comma to add. Up to 5.">
          <Input
            value={tagInput}
            placeholder="fastapi"
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagKey}
          />
        </Field>

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tags.map((name) => (
              <TagPill
                key={name}
                name={`${name} ×`}
                onClick={() => setTags(tags.filter((t) => t !== name))}
              />
            ))}
          </div>
        )}

        <Button type="submit" disabled={saving || !title.trim() || !body.trim()}>
          {saving ? "Publishing…" : "Publish question"}
        </Button>
      </form>
    </div>
  );
}
