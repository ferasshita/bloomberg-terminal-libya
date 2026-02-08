"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface AIReasoningProps {
  currencyPair?: string
}

export function AIReasoning({ currencyPair = "USD/LYD" }: AIReasoningProps) {
  const [reasoning, setReasoning] = useState<string>("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchReasoning()
    const interval = setInterval(fetchReasoning, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [currencyPair])

  const fetchReasoning = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(
        `${apiUrl}/api/v1/analysis/complete?currency_pair=${currencyPair}`
      )
      const data = await response.json()
      setReasoning(data.ai_reasoning || "No analysis available")
      setLoading(false)
    } catch (error) {
      console.error("Failed to fetch AI reasoning:", error)
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">AI Market Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center text-muted-foreground">Analyzing...</div>
        ) : (
          <p className="text-sm leading-relaxed">{reasoning}</p>
        )}
      </CardContent>
    </Card>
  )
}
