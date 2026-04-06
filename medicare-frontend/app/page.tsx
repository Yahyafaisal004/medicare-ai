"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import API from "@/lib/api";

export default function Home() {
  const [role, setRole] = useState("doctor");
  const [password, setPassword] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const router = useRouter();

  const handleLogin = async () => {
    try {
      const payload =
        role === "doctor"
          ? { role: "doctor", password }
          : { role: "patient", subject_id: subjectId };

      const res = await API.post("/login", payload);

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("role", role);

      router.push("/chat");
    } catch (err) {
      alert("Login failed");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-black text-white">
      <div className="p-6 bg-gray-900 rounded-xl w-80">
        <h1 className="text-xl mb-4">MediCare AI</h1>

        <select
          className="w-full mb-3 p-2 bg-gray-800"
          onChange={(e) => setRole(e.target.value)}
        >
          <option value="doctor">Doctor</option>
          <option value="patient">Patient</option>
        </select>

        {role === "doctor" ? (
          <input
            type="password"
            placeholder="Doctor Password"
            className="w-full mb-3 p-2 bg-gray-800"
            onChange={(e) => setPassword(e.target.value)}
          />
        ) : (
          <input
            placeholder="Patient ID"
            className="w-full mb-3 p-2 bg-gray-800"
            onChange={(e) => setSubjectId(e.target.value)}
          />
        )}

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 p-2 rounded"
        >
          Login
        </button>
      </div>
    </div>
  );
}