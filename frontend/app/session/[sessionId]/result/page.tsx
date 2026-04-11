import Link from "next/link";
import { API_BASE_URL } from "../../../../lib/config";

type SessionOverview = {
  status: {
    session_id: string;
    taxonomy_version_id: string;
    status: string;
    channel: string;
    current_question_order: number;
    answered_questions: number;
    total_questions: number;
    has_final_profile: boolean;
    final_profile_status: string | null;
    current_question: {
      id: string;
      code: string;
      order_no: number;
      title: string;
      description: string | null;
      question_type: string;
      is_required: boolean;
    } | null;
  };
  questions: {
    session_id: string;
    taxonomy_version_id: string;
    current_question_order: number;
    questions: Array<{
      id: string;
      code: string;
      order_no: number;
      title: string;
      description: string | null;
      question_type: string;
      is_required: boolean;
      is_active: boolean;
      has_answer: boolean;
      answer_id: string | null;
      revision_no: number | null;
      ai_status: string | null;
      is_current_question: boolean;
    }>;
  };
    final_profile: {
    schema_version: string;
    taxonomy_version_id: string;
    session_id: string;
    readiness: {
      is_complete: boolean;
      coverage_ratio: number;
      minimum_coverage_reached: boolean;
      can_be_shown_to_user: boolean;
      can_be_reviewed_by_expert: boolean;
    };
    thinking_profile: {
      summary: string;
      dimensions: Array<{
        dimension_code: string;
        label: string;
        score: number;
        confidence: number;
        support_count: number;
        based_on_signal_codes: string[];
      }>;
    };
    thinking_types: Array<{
      type_code: string;
      label: string;
      state: "present" | "absent";
      confidence: number;
      based_on_signal_codes: string[];
    }>;
    user_view: {
      title: string;
      short_summary: string;
      strengths: string[];
      growth_edges: string[];
      disclaimers: string[];
    };
    overall_confidence: number;
  } | null;
};

async function getSessionOverview(
  sessionId: string,
): Promise<SessionOverview> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/sessions/${sessionId}/overview`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `Failed to load result page. Status: ${response.status}. Body: ${errorBody}`,
    );
  }

  return response.json();
}

type PageProps = {
  params: Promise<{
    sessionId: string;
  }>;
};

export default async function SessionResultPage(
  props: PageProps,
) {
  const { sessionId } = await props.params;
  const overview = await getSessionOverview(sessionId);

  if (!overview.final_profile) {
    return (
      <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
        <h1>MindTrace Result</h1>
        <p>Финальный профиль ещё не готов.</p>
      </main>
    );
  }

  return (
    <main
      style={{
        padding: 24,
        maxWidth: 900,
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 16,
        }}
      >
        <h1 style={{ margin: 0 }}>
          {overview.final_profile.user_view.title}
        </h1>

        <div style={{ display: "flex", gap: 16 }}>
          <Link href="/my-sessions">
            К моим сессиям
          </Link>

          <Link href="/">
            Пройти заново
          </Link>
        </div>
      </div>

      <p style={{ fontSize: 18, lineHeight: 1.6 }}>
        {overview.final_profile.user_view.short_summary}
      </p>
      
      {overview.final_profile.thinking_types.length > 0 ? (
        <section style={{ marginTop: 32 }}>
          <h2>Типы мышления</h2>
          <ul>
            {overview.final_profile.thinking_types.map((item) => (
              <li key={item.type_code}>
                <strong>{item.label}</strong>:{" "}
                {item.state === "present" ? "выражен" : "не выражен"}{" "}
                ({Math.round(item.confidence * 100)}%)
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section style={{ marginTop: 32 }}>
        <h2>Сильные стороны</h2>
        <ul>
          {overview.final_profile.user_view.strengths.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Зоны роста</h2>
        <ul>
          {overview.final_profile.user_view.growth_edges.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Важно</h2>
        <ul>
          {overview.final_profile.user_view.disclaimers.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Метаданные</h2>
        <p>Session ID: {overview.status.session_id}</p>
        <p>
          Progress: {overview.status.answered_questions}/
          {overview.status.total_questions}
        </p>
        <p>Overall confidence: {overview.final_profile.overall_confidence}</p>
      </section>
    </main>
  );
}
