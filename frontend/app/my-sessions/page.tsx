"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { API_BASE_URL } from "../../lib/config";

type UserSessionListItem = {
  session_id: string;
  answered_questions: number;
  total_questions: number;
  has_final_profile: boolean;
};

type UserSessionsListResponse = {
  sessions: UserSessionListItem[];
};

function getVisitorUserId(): string | null {
  const storageKey = "mindtrace_visitor_user_id";
  const value = window.localStorage.getItem(storageKey);

  if (!value || value.trim().length === 0) {
    return null;
  }

  return value;
}

async function getUserSessions(
  userId: string,
): Promise<UserSessionsListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/users/${userId}/sessions`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `Failed to load user sessions. Status: ${response.status}. Body: ${errorBody}`,
    );
  }

  return response.json();
}

export default function MySessionsPage() {
  const [data, setData] = useState<UserSessionsListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorText, setErrorText] = useState("");

  useEffect(() => {
    async function loadSessions(): Promise<void> {
      try {
        setIsLoading(true);
        setErrorText("");

        const userId = getVisitorUserId();
        if (userId === null) {
          setData({
            sessions: [],
          });
          return;
        }

        const result = await getUserSessions(userId);
        setData(result);
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Unknown error while loading user sessions.";
        setErrorText(message);
      } finally {
        setIsLoading(false);
      }
    }

    void loadSessions();
  }, []);

  return (
    <main
      style={{
        padding: 24,
        maxWidth: 1100,
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Мои сессии</h1>

      {isLoading ? <p style={{ marginTop: 24 }}>Загрузка...</p> : null}

      {!isLoading && errorText ? (
        <p style={{ marginTop: 24, color: "red" }}>{errorText}</p>
      ) : null}

      {!isLoading && !errorText && data && data.sessions.length === 0 ? (
        <p style={{ marginTop: 24 }}>Сессий пока нет.</p>
      ) : null}

      {!isLoading && !errorText && data ? (
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
                Прогресс: {session.answered_questions}/
                {session.total_questions}
              </p>
              <p>
                Результат: {session.has_final_profile ? "готов" : "ещё не готов"}
              </p>

              <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
                <Link href={`/session/${session.session_id}`}>
                  Открыть сессию
                </Link>

                {session.has_final_profile ? (
                  <Link href={`/session/${session.session_id}/result`}>
                    Открыть результат
                  </Link>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </main>
  );
}
