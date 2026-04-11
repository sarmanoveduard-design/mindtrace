"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { API_BASE_URL } from "../lib/config";


const DEFAULT_USER_ID = "b9a194ec-8144-455c-beb9-8de7b33a2a88";

type GetOrCreateSessionResponse = {
  id: string;
  user_id: string;
  taxonomy_version_id: string;
  channel: string;
  status: string;
  current_question_order: number;
  is_existing: boolean;
};

function getOrCreateVisitorUserId(): string {
  const storageKey = "mindtrace_visitor_user_id";
  const existingValue = window.localStorage.getItem(storageKey);

  if (existingValue && existingValue.trim().length > 0) {
    return existingValue;
  }

  const newValue = crypto.randomUUID();
  window.localStorage.setItem(storageKey, newValue);
  return newValue;
}

export default function HomePage() {
  const router = useRouter();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorText, setErrorText] = useState("");

  async function handleStartSession() {
    setIsSubmitting(true);
    setErrorText("");

    const visitorUserId = getOrCreateVisitorUserId();
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/sessions/get-or-create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: visitorUserId,
          channel: "web",
          }),
        },
      );

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(
          `Failed to get or create session. Status: ${response.status}. Body: ${errorBody}`,
        );
      }

      const data: GetOrCreateSessionResponse = await response.json();
      router.push(`/session/${data.id}`);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unknown error while getting or creating session.";

      setErrorText(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h1>MindTrace</h1>
      <p>Нажмите, чтобы начать диагностику.</p>

      <div style={{ marginTop: 24, maxWidth: 480 }}>
        <button
          type="button"
          onClick={handleStartSession}
          disabled={isSubmitting}
          style={{
            padding: "12px 20px",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          {isSubmitting ? "Загрузка..." : "Начать сессию"}
        </button>

        {errorText ? (
          <p style={{ marginTop: 16, color: "red" }}>{errorText}</p>
        ) : null}
      </div>
    </main>
  );
}
