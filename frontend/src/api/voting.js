// The backend splits voting across three verbs instead of an upsert:
//   POST   — no vote yet (409 if one exists)
//   PATCH  — change an existing vote (404 if none exists)
//   DELETE — withdraw an existing vote (404 if none exists)
// So the current value of my_vote decides which one a click should send.
export function planVote(myVote, direction) {
  if (myVote === null || myVote === undefined) {
    return { method: "POST", value: direction, nextVote: direction, delta: direction };
  }
  if (myVote === direction) {
    return { method: "DELETE", value: null, nextVote: null, delta: -myVote };
  }
  return { method: "PATCH", value: direction, nextVote: direction, delta: direction - myVote };
}
