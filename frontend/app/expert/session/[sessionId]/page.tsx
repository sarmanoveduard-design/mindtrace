import Link from "next/link";
import { API_BASE_URL } from "../../../../lib/config";

type ExpertSessionDetail = {
  session_id: string;
  taxonomy_version_id: string;
  status: string;
  answers: Array<{
    answer_id: string;
    question_id: string;
    question_code: string;
    question_title: string;
    revision_no: number;
    ai_status: string;
    answer_text: string | null;
    answer_payload: Record<string, unknown> | null;
    extraction: {
      extraction_id: string | null;
      status: string | null;
      confidence_score: number | null;
      normalized_output: Record<string, unknown> | null;
    } | null;
  }>;
  session_aggregate: Record<string, unknown> | null;
  final_profile: Record<string, unknown> | null;
};

async function getExpertSessionDetail(
  sessionId: string,
): Promise<ExpertSessionDetail> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/sessions/${sessionId}/expert-detail`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `Failed to load expert detail. Status: ${response.status}. Body: ${errorBody}`,
    );
  }

  return response.json();
}

type PageProps = {
  params: Promise<{
    sessionId: string;
  }>;
};

export default async function ExpertSessionPage(
  props: PageProps,
) {
  const { sessionId } = await props.params;
  const data = await getExpertSessionDetail(sessionId);

  return (
    <main
      style={{
        padding: 24,
        maxWidth: 1100,
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
          <h1 style={{ margin: 0 }}>Экспертная карточка</h1>

          <Link href="/expert/sessions">
            Назад к списку сессий
          </Link>
        </div>

      <section style={{ marginTop: 24 }}>
        <h2>Сессия</h2>
        <p>Session ID: {data.session_id}</p>
        <p>Статус: {data.status}</p>
        <p>ID версии таксономии: {data.taxonomy_version_id}</p>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Ответы и извлечения</h2>

        {data.answers.map((answer) => (
          <article
            key={answer.answer_id}
            style={{
              marginTop: 20,
              padding: 16,
              border: "1px solid #ccc",
              borderRadius: 8,
            }}
          >
            <h3>
              {answer.question_code}: {answer.question_title}
            </h3>
            <p>Answer ID: {answer.answer_id}</p>
            <p>Revision: {answer.revision_no}</p>
            <p>AI status: {answer.ai_status}</p>

            <h4>Raw answer</h4>
            <p style={{ whiteSpace: "pre-wrap" }}>
              {answer.answer_text ?? "-"}
            </p>

            <h4>Extraction</h4>
            <pre
              style={{
                background: "#f5f5f5",
                padding: 12,
                overflowX: "auto",
                whiteSpace: "pre-wrap",
              }}
            >
              {JSON.stringify(answer.extraction, null, 2)}
            </pre>
          </article>
        ))}
      </section>

      {data.session_aggregate ? (
        <section style={{ marginTop: 32 }}>
          <h2>Агрегация сессии</h2>
          <pre
            style={{
              background: "#f5f5f5",
              padding: 12,
              overflowX: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
            {JSON.stringify(data.session_aggregate, null, 2)}
          </pre>
        </section>
      ) : null}

      {data.final_profile ? (
        <section style={{ marginTop: 32 }}>
          <h2>Финальный профиль</h2>
          <pre
            style={{
              background: "#f5f5f5",
              padding: 12,
              overflowX: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
            {JSON.stringify(data.final_profile, null, 2)}
          </pre>
        </section>
      ) : null}
    </main>
  );
}
