import { PriceTicker } from "@/components/PriceTicker"
import { NewsFeed } from "@/components/NewsFeed"
import { PriceChart } from "@/components/PriceChart"
import { SignalCard } from "@/components/SignalCard"
import { AIReasoning } from "@/components/AIReasoning"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-foreground">
            🇱🇾 Libyan Financial Terminal
          </h1>
          <p className="text-sm text-muted-foreground">
            Real-time currency market analysis powered by AI
          </p>
        </div>
      </header>

      {/* Price Ticker */}
      <PriceTicker />

      {/* Main Dashboard Grid */}
      <div className="container mx-auto px-4 py-6">
        {/* Desktop Layout: 3-column grid */}
        <div className="hidden lg:grid lg:grid-cols-12 gap-4">
          {/* Left Column: News Feed */}
          <div className="lg:col-span-3">
            <NewsFeed />
          </div>

          {/* Center Column: Chart + AI Reasoning */}
          <div className="lg:col-span-6 space-y-4">
            <PriceChart currencyPair="USD/LYD" />
            <AIReasoning currencyPair="USD/LYD" />
          </div>

          {/* Right Column: Signal Card */}
          <div className="lg:col-span-3">
            <SignalCard currencyPair="USD/LYD" />
          </div>
        </div>

        {/* Mobile/Tablet Layout: Stacked */}
        <div className="lg:hidden space-y-4">
          <SignalCard currencyPair="USD/LYD" />
          <AIReasoning currencyPair="USD/LYD" />
          <PriceChart currencyPair="USD/LYD" />
          <NewsFeed />
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-8">
        <div className="container mx-auto px-4 py-4 text-center text-sm text-muted-foreground">
          <p>
            Libyan Financial Terminal &copy; 2024 | Data sources: Telegram, fulus.ly
          </p>
        </div>
      </footer>
    </main>
  )
}
