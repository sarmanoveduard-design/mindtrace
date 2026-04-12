import Link from "next/link";
import { API_BASE_URL } from "../../../lib/config";

type ExpertSessionListItem = {
  session_id: string;
  user_id: string;
  status: string;
  channel: string;
  current_question_order: number;
  answered_questions: number;
  total_questions: number;
  has_final_profile: boolean;
  final_profile_status: string | null;
};

type ExpertSessionsListResponse = {
  sessions: ExpertSessionListItem[];
};

async function getExpertSessions(): Promise<ExpertSessionsListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/expert/sessions`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `Failed to load expert sessions. Status: ${response.status}. Body: ${errorBody}`,
    );
  }

  return response.json();
}

export default async function ExpertSessionsPage() {
  const data = await getExpertSessions();

  return (
    <main
      style={{
        padding: 24,
        maxWidth: 1100,
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Экспертные сессии</h1>

      <div style={{ marginTop: 24 }}>
        {data.sessions.map((session) => (
          <article
            key={session.session_id}
            style={{
              border: "1px solid #ccc",
              borderRadius: 8,
              padding: 16,
              marginBottom: 16,
            }}
          >
            <h2 style={{ marginTop: 0 }}>Сессия</h2>
            <p>
              Прогресс: {session.answered_questions}/{session.total_questions}
            </p>
            <p>
              Результат: {session.has_final_profile ? "готов" : "ещё не готов"}
            </p>

            <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
             <Link href={`/expert/session/${session.session_id}`}>
               Открыть экспертную карточку
             </Link>

             <Link href={`/session/${session.session_id}/result`}>
               Открыть пользовательский результат
             </Link>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}
