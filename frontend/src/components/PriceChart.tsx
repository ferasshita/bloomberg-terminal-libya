"use client"

import { useEffect, useRef, useState } from "react"
import { createChart, IChartApi, ISeriesApi } from "lightweight-charts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ChartProps {
  currencyPair?: string
}

export function PriceChart({ currencyPair = "USD/LYD" }: ChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const lineSeriesRef = useRef<ISeriesApi<"Line"> | null>(null)
  const [timeframe, setTimeframe] = useState<"1m" | "5m" | "1h">("1h")

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: "#0a0a0a" },
        textColor: "#d1d4dc",
      },
      grid: {
        vertLines: { color: "#1e222d" },
        horzLines: { color: "#1e222d" },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    })

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    })

    // Add forecast line series
    const lineSeries = chart.addLineSeries({
      color: "#2962FF",
      lineWidth: 2,
      lineStyle: 2, // Dashed
      priceLineVisible: false,
      lastValueVisible: false,
    })

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries
    lineSeriesRef.current = lineSeries

    // Fetch and display data
    fetchChartData()

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      chart.remove()
    }
  }, [currencyPair, timeframe])

  const fetchChartData = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      
      // Fetch historical data
      const response = await fetch(
        `${apiUrl}/api/v1/data/daily?currency_pair=${currencyPair}&days=30`
      )
      const data = await response.json()

      if (data.length > 0 && candlestickSeriesRef.current) {
        const candlestickData = data.map((d: any) => ({
          time: new Date(d.date).getTime() / 1000,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }))

        candlestickSeriesRef.current.setData(candlestickData)
      }

      // Fetch forecast data
      const forecastResponse = await fetch(
        `${apiUrl}/api/v1/analysis/complete?currency_pair=${currencyPair}`
      )
      const forecastData = await forecastResponse.json()

      if (forecastData.forecast_24h && lineSeriesRef.current) {
        const forecastLine = forecastData.forecast_24h.map((f: any) => ({
          time: new Date(f.timestamp).getTime() / 1000,
          value: f.predicted_price,
        }))

        lineSeriesRef.current.setData(forecastLine)
      }
    } catch (error) {
      console.error("Failed to fetch chart data:", error)
    }
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{currencyPair} Chart</CardTitle>
          <div className="flex gap-2">
            <button
              onClick={() => setTimeframe("1m")}
              className={`px-3 py-1 text-xs rounded ${
                timeframe === "1m"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              1M
            </button>
            <button
              onClick={() => setTimeframe("5m")}
              className={`px-3 py-1 text-xs rounded ${
                timeframe === "5m"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              5M
            </button>
            <button
              onClick={() => setTimeframe("1h")}
              className={`px-3 py-1 text-xs rounded ${
                timeframe === "1h"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              1H
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} className="w-full" />
      </CardContent>
    </Card>
  )
}
