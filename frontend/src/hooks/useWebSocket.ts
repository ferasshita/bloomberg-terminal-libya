"use client"

import { useEffect, useRef, useState } from "react"

interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: string
}

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(url)
        
        ws.onopen = () => {
          console.log("WebSocket connected")
          setIsConnected(true)
        }
        
        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            setLastMessage(message)
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error)
          }
        }
        
        ws.onerror = (error) => {
          console.error("WebSocket error:", error)
        }
        
        ws.onclose = () => {
          console.log("WebSocket disconnected")
          setIsConnected(false)
          
          // Attempt to reconnect after 5 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log("Attempting to reconnect...")
            connect()
          }, 5000)
        }
        
        wsRef.current = ws
      } catch (error) {
        console.error("Failed to connect to WebSocket:", error)
      }
    }

    connect()

    // Cleanup
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [url])

  // Send ping to keep connection alive
  useEffect(() => {
    if (isConnected && wsRef.current) {
      const pingInterval = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send("ping")
        }
      }, 30000)

      return () => clearInterval(pingInterval)
    }
  }, [isConnected])

  return { isConnected, lastMessage }
}
