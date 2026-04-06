"use client";

import { useState } from "react";
import API from "@/lib/api";

function formatResponse(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")   // bold
    .replace(/\n/g, "<br/>")                 // new lines
    .replace(/- /g, "• ")                    // bullets
}

type Message = {
  role: "user" | "assistant";
  content: string;
  time?: string;
};

type Source = {
  metadata: {
    patient_name: string;
    severity_level: string;
    los_days: number;
    primary_diagnosis: string;
    admission_type: string;
  };
  text: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sources, setSources] = useState<Source[]>([]);

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("token")
      : null;

  const sendMessage = async (query: string) => {
    if (!query) return;

  const newMessages: Message[] = [
  ...messages,
  {
    role: "user",
    content: query,
    time: new Date().toLocaleTimeString(),
  },
  ];

    setMessages(newMessages);

    try {
      const res = await API.post(
        "/query",
        { query },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

  const updatedMessages: Message[] = [
    ...newMessages,
    {
      role: "assistant",
      content: res.data.answer,
      time: new Date().toLocaleTimeString(),
    },
  ];

setMessages(updatedMessages);

      setSources(res.data.sources);
      setInput("");
    } catch {
      alert("Query failed");
    }
  };

  function formatResponse(content: string): string | TrustedHTML {
    throw new Error("Function not implemented.");
  }

  return (
    <div className="flex h-screen bg-black text-white">

      {/* SIDEBAR */}
      <div className="w-64 p-5 border-r border-gray-800 bg-[#0e1117] flex flex-col justify-between">

  {/* TOP */}
  <div>
    <h2 className="text-xl font-semibold mb-6">MediCare AI</h2>

    <div className="space-y-3">
      <button
        onClick={() => setMessages([])}
        className="w-full bg-gray-800 hover:bg-gray-700 transition p-3 rounded-lg"
      >
        ➕ New Chat
      </button>

      <button
        onClick={() => {
          localStorage.clear();
          window.location.href = "/";
        }}
        className="w-full bg-red-600 hover:bg-red-500 transition p-3 rounded-lg"
      >
        🚪 Logout
      </button>
    </div>
  </div>

  {/* BOTTOM */}
    <div className="text-xs text-gray-500">
      Secure Clinical Assistant
    </div>
  </div>

      {/* CHAT */}
      <div className="flex-1 flex flex-col">

        <div className="flex-1 overflow-y-auto p-6 space-y-6">

  {messages.map((msg, i) => (
    <div
      key={i}
      className={`flex ${
        msg.role === "user" ? "justify-end" : "justify-start"
      }`}
    >

      <div
        className={`max-w-[70%] p-4 rounded-xl ${
          msg.role === "user"
            ? "bg-blue-600"
            : "bg-gray-800"
        }`}
      >

        {msg.role === "assistant" ? (
          <div className="space-y-3 text-sm leading-relaxed">

            {msg.content.split("\n").map((line, idx) => {

              let clean = line
                .replace(/\*\*/g, "")
                .replace(/\*/g, "")
                .trim();

              if (!clean) return null;

              const lower = clean.toLowerCase();

              // Decision highlight
              if (lower.includes("should")) {
                const safe = lower.includes("not");

                return (
                  <div
                    key={idx}
                    className={`font-semibold text-base ${
                      safe ? "text-green-400" : "text-red-400"
                    }`}
                  >
                    {safe ? "✅ " : "⚠️ "} {clean}
                  </div>
                );
              }

              // Section headings
              if (clean.endsWith(":")) {
                return (
                  <div key={idx} className="text-blue-400 font-semibold mt-2">
                    {clean}
                  </div>
                );
              }

              // Bullet points
              if (line.includes("*")) {
                return (
                  <div key={idx} className="ml-2 text-gray-300">
                    • {clean}
                  </div>
                );
              }

              return <div key={idx}>{clean}</div>;
            })}

          </div>
        ) : (
          msg.content
        )}

      </div>

    </div>
  ))}
</div>

      <div className="p-4 border-t border-gray-700 flex bg-black">
        <input
          className="flex-1 p-3 rounded-lg bg-gray-800 outline-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about patient records..."
        />
        <button
          onClick={() => sendMessage(input)}
          className="ml-3 bg-blue-600 px-5 rounded-lg"
        >
          Send
        </button>
      </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="w-1/3 p-4 border-l border-gray-700 overflow-y-auto">
  <h2 className="text-lg mb-4 font-semibold">Clinical Insights</h2>

  {sources.map((doc, i) => (
    <div
      key={i}
      className="bg-gray-900 p-4 rounded-lg mb-4 shadow-md space-y-3"
    >

      {/* HEADER */}
      <div className="flex justify-between items-center">
        <p className="text-lg font-semibold">
          {doc.metadata.patient_name}
        </p>

        <span className="text-xs px-2 py-1 rounded bg-gray-700">
          {doc.metadata.admission_type}
        </span>
      </div>

      {/* STATS */}
      <div className="flex justify-between text-sm">
        <span>LOS: {doc.metadata.los_days} days</span>

        <span
          className={
            doc.metadata.severity_level === "severe"
              ? "text-red-400 font-semibold"
              : doc.metadata.severity_level === "moderate"
              ? "text-yellow-400 font-semibold"
              : "text-green-400 font-semibold"
          }
        >
          {doc.metadata.severity_level}
        </span>
      </div>

      {/* DIAGNOSIS */}
      <p className="text-sm">
        <b>Diagnosis:</b> {doc.metadata.primary_diagnosis}
      </p>

      {/* NOTES */}
      <details className="mt-2 text-sm">
        <summary className="cursor-pointer text-gray-400">
          Clinical Notes
        </summary>
        <p className="mt-2 text-gray-300">{doc.text}</p>
      </details>

    </div>
  ))}
</div>

    </div>
  );
}