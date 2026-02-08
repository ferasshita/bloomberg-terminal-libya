"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatDate } from "@/lib/utils"

interface Message {
  timestamp: string
  channel: string
  text: string
  contains_price: boolean
}

export function NewsFeed() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMessages()
    const interval = setInterval(fetchMessages, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchMessages = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/v1/data/messages?limit=50`)
      const data = await response.json()
      setMessages(data)
      setLoading(false)
    } catch (error) {
      console.error("Failed to fetch messages:", error)
      setLoading(false)
    }
  }

  const getSentimentBadge = (message: Message) => {
    if (message.contains_price) {
      return <Badge variant="success">Price Update</Badge>
    }
    
    const text = message.text.toLowerCase()
    if (text.includes("أزمة") || text.includes("crisis") || text.includes("انهيار")) {
      return <Badge variant="destructive">High Alert</Badge>
    }
    if (text.includes("نقص") || text.includes("shortage")) {
      return <Badge variant="warning">Warning</Badge>
    }
    
    return <Badge variant="outline">News</Badge>
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg">Live News Feed</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="h-[calc(100vh-12rem)] overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-muted-foreground">Loading...</div>
          ) : messages.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">No messages</div>
          ) : (
            <div className="space-y-2 p-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className="border-b border-border pb-3 last:border-0"
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <span className="text-xs font-medium text-primary">
                      {message.channel}
                    </span>
                    {getSentimentBadge(message)}
                  </div>
                  <p className="text-sm text-foreground mb-1">{message.text}</p>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(message.timestamp)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
