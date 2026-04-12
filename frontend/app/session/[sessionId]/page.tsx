"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { API_BASE_URL } from "../../../lib/config";


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

async function fetchOverview(
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
      `Failed to load overview. Status: ${response.status}. Body: ${errorBody}`,
    );
  }

  return response.json();
}

export default function SessionPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;
  const router = useRouter();

  const [overview, setOverview] = useState<SessionOverview | null>(null);
  const [answerText, setAnswerText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorText, setErrorText] = useState("");

  async function loadOverview() {
    if (!sessionId) {
      return;
    }

    try {
      const data = await fetchOverview(sessionId);
      setOverview(data);
      setErrorText("");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unknown error while loading overview.";
      setErrorText(message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadOverview();
  }, [sessionId]);

  useEffect(() => {
    if (!overview || !sessionId) {
      return;
    }

    if (overview.status.status === "ready") {
      router.replace(`/session/${sessionId}/result`);
      return;
    }

    const intervalId = window.setInterval(() => {
      void loadOverview();
    }, 2000);

    return () => window.clearInterval(intervalId);
  }, [overview, router, sessionId]);

  const currentQuestion = useMemo(() => {
    return overview?.status.current_question ?? null;
  }, [overview]);

  async function handleSubmitAnswer() {
    if (!currentQuestion || !sessionId) {
      return;
    }

    const trimmedAnswer = answerText.trim();
    if (!trimmedAnswer) {
      setErrorText("Введите ответ.");
      return;
    }

    setIsSubmitting(true);
    setErrorText("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/sessions/${sessionId}/answers`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question_id: currentQuestion.id,
            source: "web",
            answer_text: trimmedAnswer,
          }),
        },
      );

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(
          `Failed to submit answer. Status: ${response.status}. Body: ${errorBody}`,
        );
      }

      setAnswerText("");
      await loadOverview();
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unknown error while submitting answer.";
      setErrorText(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading && !overview) {
    return (
      <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
        <h1>Диагностика мышления</h1>
        <p>Загрузка...</p>
      </main>
    );
  }

  if (!overview) {
    return (
      <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
        <h1>Диагностика мышления</h1>
        <p style={{ color: "red" }}>
          {errorText || "Не удалось загрузить сессию."}
        </p>
      </main>
    );
  }

  return (
     <main
        style={{
          padding: "40px 20px",
          maxWidth: 760,
          margin: "0 auto",
          fontFamily: "Arial, sans-serif",
        }}
      >
      <h1>Диагностика мышления</h1>

      <section style={{ marginTop: 24 }}>
        <p style={{ fontSize: 18, margin: 0 }}>
          Вопрос{" "}
          {currentQuestion?.order_no ?? overview.status.answered_questions}{" "}
          из {overview.status.total_questions}
        </p>
      </section>

      {currentQuestion ? (
        <section
          style={{
            marginTop: 24,
            background: "#ffffff",
            border: "1px solid #e5e7eb",
            borderRadius: 16,
            padding: 24,
            boxShadow: "0 8px 24px rgba(15, 23, 42, 0.06)",
          }}
        >
          <h2>
            Вопрос {currentQuestion.order_no}: {currentQuestion.title}
          </h2>

          {currentQuestion.description ? (
            <p>{currentQuestion.description}</p>
          ) : null}

          <textarea
            value={answerText}
            onChange={(event) => setAnswerText(event.target.value)}
            rows={8}
            placeholder="Введите ваш ответ..."
            style={{
              width: "100%",
              marginTop: 16,
              padding: 14,
              fontSize: 16,
              lineHeight: 1.5,
              boxSizing: "border-box",
              border: "1px solid #d1d5db",
              borderRadius: 12,
              outline: "none",
              resize: "vertical",
            }}
          />
          <button
            type="button"
            onClick={handleSubmitAnswer}
            disabled={isSubmitting}
          style={{
            marginTop: 16,
            padding: "12px 18px",
            fontSize: 16,
            fontWeight: 600,
            cursor: "pointer",
            border: "none",
            borderRadius: 12,
            background: "#111827",
            color: "#ffffff",
          }}
          >
            {isSubmitting ? "Отправка..." : "Отправить ответ"}
          </button>
        </section>
      ) : null}

      {overview.status.status !== "ready" && !currentQuestion ? (
        <section style={{ marginTop: 24 }}>
          <h2>Обработка</h2>
          <p>Ответы приняты. Сессия обрабатывается...</p>
        </section>
      ) : null}

      {errorText ? (
        <p style={{ marginTop: 24, color: "red" }}>{errorText}</p>
      ) : null}
    </main>
  );
}
