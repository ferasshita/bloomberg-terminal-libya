"use client"

import { useEffect, useState } from "react"
import { useWebSocket } from "@/hooks/useWebSocket"
import { formatCurrency, formatPercent } from "@/lib/utils"
import { TrendingUp, TrendingDown } from "lucide-react"

interface Price {
  pair: string
  value: number
  change: number
}

export function PriceTicker() {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
  const { lastMessage } = useWebSocket(`${wsUrl}/api/v1/ws`)
  
  const [prices, setPrices] = useState<Price[]>([
    { pair: "USD/LYD", value: 0, change: 0 },
    { pair: "EUR/LYD", value: 0, change: 0 },
    { pair: "Gold/LYD", value: 0, change: 0 },
    { pair: "TND/LYD", value: 0, change: 0 },
  ])

  useEffect(() => {
    fetchLatestPrices()
    const interval = setInterval(fetchLatestPrices, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (lastMessage?.type === "price_update" && lastMessage.data) {
      updatePrice(lastMessage.data.currency_pair, lastMessage.data.price)
    }
  }, [lastMessage])

  const fetchLatestPrices = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      
      for (const price of prices) {
        const response = await fetch(
          `${apiUrl}/api/v1/data/latest-price?currency_pair=${price.pair}`
        )
        const data = await response.json()
        
        if (data.price) {
          updatePrice(data.currency_pair, data.price)
        }
      }
    } catch (error) {
      console.error("Failed to fetch prices:", error)
    }
  }

  const updatePrice = (pair: string, newValue: number) => {
    setPrices((prev) =>
      prev.map((p) => {
        if (p.pair === pair) {
          const change = p.value > 0 ? ((newValue - p.value) / p.value) * 100 : 0
          return { ...p, value: newValue, change }
        }
        return p
      })
    )
  }

  return (
    <div className="bg-card border-b border-border">
      <div className="flex items-center justify-around h-16 px-4 overflow-x-auto">
        {prices.map((price) => (
          <div key={price.pair} className="flex items-center gap-3 min-w-[200px]">
            <div>
              <div className="text-xs text-muted-foreground">{price.pair}</div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold">
                  {price.value > 0 ? formatCurrency(price.value) : "—"}
                </span>
                {price.change !== 0 && (
                  <span
                    className={`flex items-center text-sm ${
                      price.change > 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    {price.change > 0 ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {formatPercent(Math.abs(price.change))}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
