import Link from "next/link";
import { API_BASE_URL } from "../../../../lib/config";

type SessionOverview = {
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
      <main
        style={{
          padding: 24,
          maxWidth: 900,
          margin: "0 auto",
          fontFamily: "Arial, sans-serif",
        }}
      >
        <h1>Результат диагностики</h1>
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
    </main>
  );
}
