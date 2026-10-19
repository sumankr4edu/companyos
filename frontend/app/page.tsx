"use client";

import dynamic from "next/dynamic";
import { FormEvent, useMemo, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Evidence = {
  title?: string;
  type?: string;
  description?: string;
  source?: string;
  relationship?: string;
  [key: string]: unknown;
};

type GraphPath = {
  display?: string;
  nodes?: Array<Record<string, unknown>>;
  relationships?: Array<Record<string, unknown>>;
  hops?: number;
  path_count?: number;
  confidence?: number;
  evidence?: Array<Record<string, unknown>>;
  branches?: Array<Record<string, unknown>>;
  unknowns?: string[];
};

type ChatResponse = {
  success?: boolean;
  question?: string;
  answer?: string;

  conversation_id?: string;

  conversation_persistence?: {
    success?: boolean;
    conversation_id?: string;
    error?: string;
    [key: string]: unknown;
  };

  plan?: Record<string, unknown>;
  cypher?: string;
  entities?: string[];

  graph_name?: string;

  graph_evidence?: Evidence[];
  graph_intelligence?: Record<string, unknown>;

  graph_path?: GraphPath;

  explanation?: {
    answer?: string;
    evidence?: Evidence[];
    graph_path?: GraphPath[];
    confidence?: number;
    contradictions?: string[];
    unknowns?: string[];

    why_this_answer?: {
      source?: string;
      graph_evidence_count?: number;
      path_count?: number;
      contradiction_count?: number;
      confidence?: number;
      explanation?: string;
    };
  };

  memory?: Record<string, unknown>;

  provenance?: unknown;
  freshness?: unknown;

  contradictions?: string[];

  confidence?: number;
  evidence_count?: number;

  retrieval_mode?: string;
  graph_first?: boolean;
};

const GraphExplorer = dynamic(
  () => import("@/components/GraphExplorer"),
  {
    ssr: false,
    loading: () => (
      <div className="graph-loading">
        Loading graph visualization...
      </div>
    ),
  },
);

const HERO_QUESTION =
  "Checkout failures increased this week. What happened, who worked on the affected system before, what decision caused the current architecture, and who should investigate it?";

const EXAMPLE_QUESTIONS = [
  {
    label: "Who knows?",
    question: "Who knows the most about our payment system?",
    icon: "◎",
  },
  {
    label: "Why?",
    question: "Why was the payment architecture changed?",
    icon: "◈",
  },
  {
    label: "What breaks?",
    question: "What happens if Payment Service goes down?",
    icon: "◇",
  },
  {
    label: "Who investigates?",
    question: "Who should investigate checkout failures?",
    icon: "→",
  },
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] =
    useState<ChatResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showCypher, setShowCypher] = useState(false);

  /*
   * Phase 22:
   * Keep the current CompanyOS investigation conversation
   * in browser state so subsequent questions can reuse
   * persistent FalkorDB conversation memory.
   */
  const [conversationId, setConversationId] =
    useState<string | null>(null);

  const confidence = Math.round(
    Math.max(
      0,
      Math.min(1, response?.confidence ?? 0),
    ) * 100,
  );

  const evidence =
    response?.explanation?.evidence ??
    response?.graph_evidence ??
    [];

  const contradictions =
    response?.explanation?.contradictions ??
    response?.contradictions ??
    [];

  const unknowns =
    response?.explanation?.unknowns ?? [];

  const path =
    response?.graph_path ??
    response?.explanation?.graph_path?.[0];

  const pathNodes = path?.nodes ?? [];
  const pathRelationships =
    path?.relationships ?? [];

  const graphSummary = useMemo(() => {
    if (!response) {
      return "Awaiting investigation";
    }

    return [
      response.graph_first
        ? "Graph-first"
        : "AI-first",
      response.graph_name || "novatech",
      `${response.evidence_count ?? evidence.length} evidence`,
      `${path?.hops ?? 0} hops`,
    ].join(" · ");
  }, [
    response,
    evidence.length,
    path?.hops,
  ]);

  async function ask(questionOverride?: string) {
    const query = (
      questionOverride ?? question
    ).trim();

    if (!query || loading) {
      return;
    }

    setQuestion(query);
    setLoading(true);
    setError("");
    setResponse(null);
    setShowCypher(false);

    try {
      const res = await fetch(
        `${API_URL}/api/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            "X-User-ID": "suman",
          },

          body: JSON.stringify({
            question: query,
            graph_name: "novatech",

            /*
             * Phase 22 persistent conversation.
             *
             * First question:
             * conversation_id = null
             *
             * Backend creates a FalkorDB conversation
             * and returns its ID.
             *
             * Subsequent questions reuse that ID.
             */
            conversation_id: conversationId,
          }),
        },
      );

      let data: ChatResponse | { detail?: string } = {};

      try {
        data = await res.json();
      } catch {
        throw new Error(
          "The CompanyOS backend returned an invalid response.",
        );
      }

      if (!res.ok) {
        const errorData =
          data as { detail?: string };

        throw new Error(
          errorData?.detail ||
            `Request failed with status ${res.status}`,
        );
      }

      const chatData = data as ChatResponse;

      /*
       * Persist the conversation ID returned by
       * CompanyOS/FalkorDB.
       */
      if (chatData.conversation_id) {
        setConversationId(
          chatData.conversation_id,
        );
      }

      setResponse(chatData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to reach the CompanyOS backend.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    void ask();
  }

  function startNewInvestigation() {
    setConversationId(null);
    setResponse(null);
    setQuestion("");
    setError("");
    setShowCypher(false);
  }

  return (
    <main className="company-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {/* ======================================================
          TOP BAR
          ====================================================== */}

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <div className="brand-name">
              CompanyOS
            </div>

            <div className="brand-caption">
              THE GRAPH-NATIVE COMPANY BRAIN
            </div>
          </div>
        </div>

        <div className="topbar-right">
          <div className="graph-status">
            <span className="status-dot" />
            FalkorDB connected
          </div>

          <div className="company-selector">
            <span className="company-avatar">
              N
            </span>

            NovaTech

            <span className="chevron">
              ⌄
            </span>
          </div>
        </div>
      </header>

      {/* ======================================================
          HERO / COMMAND CENTER
          ====================================================== */}

      <section className="hero">
        <div className="eyebrow">
          <span className="eyebrow-line" />

          COMPANY INTELLIGENCE

          <span className="eyebrow-line" />
        </div>

        <h1>
          Your company&apos;s knowledge,
          <br />
          <span>connected.</span>
        </h1>

        <p>
          Ask a question. Follow the graph.
          Get the evidence.
        </p>

        <form
          className="command-box"
          onSubmit={handleSubmit}
        >
          <div className="command-icon">
            ⌕
          </div>

          <input
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Ask anything about NovaTech..."
            aria-label="Ask CompanyOS"
          />

          <button
            type="submit"
            className="ask-button"
            disabled={
              loading || !question.trim()
            }
          >
            {loading ? (
              <>
                <span className="spinner" />
                Investigating
              </>
            ) : (
              <>
                Ask
                <span>↵</span>
              </>
            )}
          </button>
        </form>

        <div className="suggestion-row">
          {EXAMPLE_QUESTIONS.map((item) => (
            <button
              key={item.label}
              className="suggestion"
              onClick={() =>
                void ask(item.question)
              }
              disabled={loading}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </div>

        {!response && !loading && (
          <button
            className="hero-demo"
            onClick={() =>
              void ask(HERO_QUESTION)
            }
          >
            <span className="demo-pulse" />

            Run the 3-minute demo investigation

            <span>→</span>
          </button>
        )}
      </section>

      {/* ======================================================
          LOADING STATE
          ====================================================== */}

      {loading && (
        <section className="investigation-loading">
          <div className="loading-orbit">
            <div />
            <div />
            <div />
          </div>

          <div>
            <div className="loading-title">
              Following the company graph
            </div>

            <div className="loading-subtitle">
              Planning relationships · Querying
              FalkorDB · Building evidence
            </div>
          </div>
        </section>
      )}

      {/* ======================================================
          ERROR STATE
          ====================================================== */}

      {error && (
        <section className="error-panel">
          <div className="error-icon">
            !
          </div>

          <div>
            <strong>
              Investigation failed
            </strong>

            <p>{error}</p>
          </div>

          <button
            onClick={() => void ask()}
            disabled={loading}
          >
            Retry
          </button>
        </section>
      )}

      {/* ======================================================
          INVESTIGATION WORKSPACE
          ====================================================== */}

      {response && !loading && (
        <section className="workspace">
          {/* Workspace header */}

          <div className="workspace-header">
            <div>
              <div className="workspace-kicker">
                INVESTIGATION RESULT
              </div>

              <h2>
                {response.question}
              </h2>
            </div>

            <div className="workspace-meta">
              <div className="confidence">
                <span>
                  Confidence
                </span>

                <strong>
                  {confidence}%
                </strong>
              </div>

              <div className="graph-first-badge">
                <span className="status-dot" />
                Graph-first
              </div>
            </div>
          </div>

          {/* Persistent conversation controls */}

          <div className="conversation-bar">
            <div className="conversation-status">
              <span className="status-dot" />

              <div>
                <strong>
                  Persistent investigation
                </strong>

                <small>
                  {conversationId
                    ? `Conversation ${conversationId}`
                    : "Conversation state active"}
                </small>
              </div>
            </div>

            <button
              className="new-investigation"
              onClick={
                startNewInvestigation
              }
            >
              + New investigation
            </button>
          </div>

          <div className="workspace-grid">
            {/* ==================================================
                MAIN COLUMN
                ================================================== */}

            <div className="main-column">
              {/* ==================================================
                  ANSWER
                  ================================================== */}

              <article className="answer-card">
                <div className="card-heading">
                  <div className="card-icon answer-icon">
                    ✦
                  </div>

                  <div>
                    <span>
                      ANSWER
                    </span>

                    <h3>
                      What the graph says
                    </h3>
                  </div>
                </div>

                <div className="answer-text">
                  {response.answer ||
                    response.explanation
                      ?.answer ||
                    "No answer was returned."}
                </div>

                <div className="answer-footer">
                  <span>
                    {graphSummary}
                  </span>

                  <span className="verified">
                    <span>✓</span>
                    FalkorDB verified
                  </span>
                </div>
              </article>

              {/* ==================================================
                  GRAPH PATH
                  ================================================== */}

              <article className="path-card">
                <div className="card-heading">
                  <div className="card-icon path-icon">
                    ⌁
                  </div>

                  <div>
                    <span>
                      GRAPH PATH
                    </span>

                    <h3>
                      How the evidence connects
                    </h3>
                  </div>
                </div>

                {path?.display ? (
                  <div className="path-display">
                    {path.display}
                  </div>
                ) : null}

                <div className="graph-visual">
                  {pathNodes.length > 0 ? (
                    <div className="path-chain">
                      {pathNodes.map(
                        (node, index) => {
                          const rawName =
                            node.name ??
                            node.title ??
                            node.id ??
                            node.type ??
                            `Node ${index + 1}`;

                          const name =
                            String(rawName);

                          const rawType =
                            node.type ??
                            node.label ??
                            node.labels ??
                            "ENTITY";

                          const type =
                            String(rawType);

                          return (
                            <div
                              className="path-step"
                              key={`${name}-${index}`}
                            >
                              <div className="node">
                                <div className="node-index">
                                  {String(
                                    index + 1,
                                  ).padStart(
                                    2,
                                    "0",
                                  )}
                                </div>

                                <div className="node-type">
                                  {type
                                    .replace(
                                      /[\[\]"*]/g,
                                      "",
                                    )}
                                </div>

                                <div className="node-name">
                                  {name}
                                </div>
                              </div>

                              {index <
                                pathNodes.length -
                                  1 && (
                                <div className="path-link">
                                  <span>
                                    {String(
                                      pathRelationships[
                                        index
                                      ]?.type ??
                                        pathRelationships[
                                          index
                                        ]?.relationship ??
                                        "RELATED_TO",
                                    )}
                                  </span>

                                  <i>
                                    →
                                  </i>
                                </div>
                              )}
                            </div>
                          );
                        },
                      )}
                    </div>
                  ) : (
                    <div className="empty-state">
                      No explicit graph path
                      was returned.
                    </div>
                  )}
                </div>
              </article>

              {/* ==================================================
                  INTERACTIVE FALKORDB GRAPH
                  ================================================== */}

              <article className="graph-card">
                <div className="card-heading">
                  <div className="card-icon graph-icon">
                    ✣
                  </div>

                  <div>
                    <span>
                      FALKORDB GRAPH
                    </span>

                    <h3>
                      Explore the connected
                      company graph
                    </h3>
                  </div>
                </div>

                <p className="graph-description">
                  This is the actual graph
                  returned by FalkorDB for the
                  investigation. Drag nodes, zoom,
                  pan, and select an entity to
                  inspect its properties.
                </p>

                <GraphExplorer
                  nodes={pathNodes}
                  relationships={
                    pathRelationships
                  }
                />
              </article>

              {/* ==================================================
                  CONTRADICTIONS
                  ================================================== */}

              {contradictions.length >
                0 && (
                <article className="warning-card">
                  <div className="warning-symbol">
                    △
                  </div>

                  <div>
                    <span>
                      CONTRADICTIONS
                    </span>

                    {contradictions.map(
                      (item, index) => (
                        <p key={index}>
                          {item}
                        </p>
                      ),
                    )}
                  </div>
                </article>
              )}

              {/* ==================================================
                  UNKNOWNS
                  ================================================== */}

              {unknowns.length > 0 && (
                <article className="unknown-card">
                  <div className="unknown-symbol">
                    ?
                  </div>

                  <div>
                    <span>
                      UNKNOWN
                    </span>

                    {unknowns.map(
                      (item, index) => (
                        <p key={index}>
                          {item}
                        </p>
                      ),
                    )}
                  </div>
                </article>
              )}
            </div>

            {/* ==================================================
                SIDE COLUMN
                ================================================== */}

            <aside className="side-column">
              {/* ==================================================
                  EVIDENCE
                  ================================================== */}

              <article className="evidence-card">
                <div className="card-heading compact">
                  <div className="card-icon evidence-icon">
                    ◉
                  </div>

                  <div>
                    <span>
                      EVIDENCE
                    </span>

                    <h3>
                      Graph evidence
                    </h3>
                  </div>

                  <div className="count-badge">
                    {evidence.length}
                  </div>
                </div>

                <div className="evidence-list">
                  {evidence.length ===
                  0 ? (
                    <div className="empty-state">
                      No evidence cards
                      returned.
                    </div>
                  ) : (
                    evidence
                      .slice(0, 12)
                      .map(
                        (
                          item,
                          index,
                        ) => (
                          <div
                            className="evidence-item"
                            key={index}
                          >
                            <div className="evidence-number">
                              {String(
                                index + 1,
                              ).padStart(
                                2,
                                "0",
                              )}
                            </div>

                            <div className="evidence-content">
                              <strong>
                                {item.title ||
                                  item.description ||
                                  "Graph relationship"}
                              </strong>

                              {item.relationship && (
                                <span className="relationship">
                                  {
                                    item.relationship
                                  }
                                </span>
                              )}

                              {item.source && (
                                <small>
                                  {
                                    item.source
                                  }
                                </small>
                              )}
                            </div>
                          </div>
                        ),
                      )
                  )}
                </div>
              </article>

              {/* ==================================================
                  REASONING METADATA
                  ================================================== */}

              <article className="trace-card">
                <div className="card-heading compact">
                  <div className="card-icon trace-icon">
                    ⌘
                  </div>

                  <div>
                    <span>
                      REASONING TRACE
                    </span>

                    <h3>
                      Investigation metadata
                    </h3>
                  </div>
                </div>

                <div className="trace-list">
                  <TraceRow
                    label="Intent"
                    value={String(
                      response.plan?.intent ??
                        "graph_search",
                    )}
                  />

                  <TraceRow
                    label="Retrieval"
                    value={
                      response.retrieval_mode ||
                      "graph"
                    }
                  />

                  <TraceRow
                    label="Entities"
                    value={String(
                      response.entities
                        ?.length ?? 0,
                    )}
                  />

                  <TraceRow
                    label="Evidence"
                    value={String(
                      response.evidence_count ??
                        evidence.length,
                    )}
                  />

                  <TraceRow
                    label="Path hops"
                    value={String(
                      path?.hops ?? 0,
                    )}
                  />

                  <TraceRow
                    label="Graph"
                    value={
                      response.graph_name ||
                      "novatech"
                    }
                  />

                  <TraceRow
                    label="Confidence"
                    value={`${confidence}%`}
                  />
                </div>

                <button
                  className="cypher-toggle"
                  onClick={() =>
                    setShowCypher(
                      !showCypher,
                    )
                  }
                >
                  <span>
                    {showCypher
                      ? "Hide"
                      : "Show"}{" "}
                    Cypher
                  </span>

                  <span>
                    {showCypher
                      ? "↑"
                      : "↓"}
                  </span>
                </button>

                {showCypher &&
                  response.cypher && (
                    <pre className="cypher">
                      {response.cypher}
                    </pre>
                  )}
              </article>

              {/* ==================================================
                  MEMORY
                  ================================================== */}

              <article className="memory-card">
                <div className="memory-header">
                  <span className="memory-icon">
                    ◌
                  </span>

                  <div>
                    <span>
                      MEMORY
                    </span>

                    <strong>
                      Company context retained
                    </strong>
                  </div>
                </div>

                <p>
                  CompanyOS stores useful
                  investigation context in
                  FalkorDB so future questions
                  can build on previous work.
                </p>

                <div className="memory-status">
                  <span className="status-dot" />

                  Persistent graph memory
                </div>

                {conversationId && (
                  <div className="conversation-id">
                    Conversation:
                    <code>
                      {conversationId}
                    </code>
                  </div>
                )}
              </article>

              {/* ==================================================
                  EXPLAINABILITY
                  ================================================== */}

              {response.explanation
                ?.why_this_answer && (
                <article className="explain-card">
                  <div className="card-heading compact">
                    <div className="card-icon">
                      ⓘ
                    </div>

                    <div>
                      <span>
                        EXPLAINABILITY
                      </span>

                      <h3>
                        Why this answer?
                      </h3>
                    </div>
                  </div>

                  <div className="explain-source">
                    {
                      response
                        .explanation
                        .why_this_answer
                        .source
                    }
                  </div>

                  {response
                    .explanation
                    .why_this_answer
                    .explanation && (
                    <p>
                      {
                        response
                          .explanation
                          .why_this_answer
                          .explanation
                      }
                    </p>
                  )}
                </article>
              )}
            </aside>
          </div>
        </section>
      )}

      {/* ======================================================
          FOOTER
          ====================================================== */}

      <footer className="footer">
        <div>
          <strong>
            CompanyOS
          </strong>

          <span>·</span>

          Graph-native intelligence for
          connected organizations.
        </div>

        <div className="footer-right">
          <span>FalkorDB</span>

          <span>·</span>

          <span>
            NovaTech Demo Graph
          </span>

          <span>·</span>

          <span>
            Persistent Memory
          </span>

          <span>·</span>

          <span>v0.1</span>
        </div>
      </footer>
    </main>
  );
}

/* ============================================================
   TRACE ROW
   ============================================================ */

function TraceRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="trace-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}