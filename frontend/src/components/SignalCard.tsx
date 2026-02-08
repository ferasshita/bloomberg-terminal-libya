"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface SignalData {
  signal: "BUY" | "SELL" | "HOLD"
  confidence: number
  rsi: number
  market_panic_index: number
  reasoning: string
}

interface SignalCardProps {
  currencyPair?: string
}

export function SignalCard({ currencyPair = "USD/LYD" }: SignalCardProps) {
  const [signalData, setSignalData] = useState<SignalData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSignal()
    const interval = setInterval(fetchSignal, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [currencyPair])

  const fetchSignal = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(
        `${apiUrl}/api/v1/analysis/signal?currency_pair=${currencyPair}`
      )
      const data = await response.json()
      setSignalData(data)
      setLoading(false)
    } catch (error) {
      console.error("Failed to fetch signal:", error)
      setLoading(false)
    }
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case "BUY":
        return "text-green-500"
      case "SELL":
        return "text-red-500"
      default:
        return "text-yellow-500"
    }
  }

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case "BUY":
        return <TrendingUp className="w-12 h-12" />
      case "SELL":
        return <TrendingDown className="w-12 h-12" />
      default:
        return <Minus className="w-12 h-12" />
    }
  }

  const getPanicColor = (index: number) => {
    if (index < 30) return "bg-green-500"
    if (index < 60) return "bg-yellow-500"
    return "bg-red-500"
  }

  if (loading) {
    return (
      <Card className="h-full">
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  if (!signalData) {
    return (
      <Card className="h-full">
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">No signal data</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg">Trading Signal</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Main Signal */}
        <div className="text-center">
          <div className={`flex justify-center mb-4 ${getSignalColor(signalData.signal)}`}>
            {getSignalIcon(signalData.signal)}
          </div>
          <h2 className={`text-4xl font-bold mb-2 ${getSignalColor(signalData.signal)}`}>
            {signalData.signal}
          </h2>
          <p className="text-sm text-muted-foreground">
            Confidence: {signalData.confidence.toFixed(1)}%
          </p>
          <Progress
            value={signalData.confidence}
            className="mt-2"
          />
        </div>

        {/* Market Panic Index */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">Market Panic Index</span>
            <span className="text-sm font-bold">
              {signalData.market_panic_index.toFixed(0)}/100
            </span>
          </div>
          <div className="h-4 bg-secondary rounded-full overflow-hidden">
            <div
              className={`h-full ${getPanicColor(signalData.market_panic_index)}`}
              style={{ width: `${signalData.market_panic_index}%` }}
            />
          </div>
        </div>

        {/* RSI */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">RSI (14)</span>
            <span className="text-sm font-bold">{signalData.rsi.toFixed(1)}</span>
          </div>
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary"
              style={{ width: `${signalData.rsi}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>Oversold (30)</span>
            <span>Overbought (70)</span>
          </div>
        </div>

        {/* Reasoning */}
        <div className="pt-4 border-t">
          <h3 className="text-sm font-semibold mb-2">Analysis</h3>
          <p className="text-sm text-muted-foreground">{signalData.reasoning}</p>
        </div>
      </CardContent>
    </Card>
  )
}
