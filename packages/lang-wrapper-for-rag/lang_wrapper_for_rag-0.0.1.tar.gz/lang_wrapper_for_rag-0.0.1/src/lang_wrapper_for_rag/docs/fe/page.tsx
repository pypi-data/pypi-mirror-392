"use client";

import { useState, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  const [messages, setMessages] = useState<
    { id: string; role: "user" | "assistant"; content: string }[]
  >([]);

  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const mutation = useMutation({
    mutationFn: async (payload: {
      question: string;
      history: { id: string; role: "user" | "assistant"; content: string }[];
    }) => {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("HTTP " + res.status);
      }

      return res.json();
    },
    retry: 2,
    retryDelay: 500,
  });

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    mutation.mutate(
      {
        question: userMessage.content,
        history: messages,
      },
      {
        onSuccess: (data) => {
          const assistantMessage = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: data.answer,
          };
          setMessages((prev) => [...prev, assistantMessage]);
        },
        onError: () => {
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: "Hiba történt. Kérlek próbáld újra.",
            },
          ]);
        },
      }
    );
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-2xl p-4 space-y-4">
        <ScrollArea className="h-[60vh] pr-4">
          <div className="flex flex-col gap-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`p-3 rounded-lg max-w-[80%] ${
                  msg.role === "user"
                    ? "bg-blue-500 text-white self-end"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.content}
              </div>
            ))}

            {mutation.isPending && (
              <div className="p-3 rounded-lg bg-gray-300 text-black max-w-[80%]">
                Thinking...
              </div>
            )}

            <div ref={scrollRef} />
          </div>
        </ScrollArea>

        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message…"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !mutation.isPending) handleSend();
            }}
          />

          <Button onClick={handleSend} disabled={mutation.isPending}>
            {mutation.isPending ? "..." : "Send"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
