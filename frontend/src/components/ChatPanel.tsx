import { useState, useRef, useEffect } from 'react'
import { useAppStore, ChatMessage } from '../store'
import { geoApi } from '../api'
import { 
  Send, 
  Loader2, 
  User, 
  Bot, 
  Code, 
  Copy, 
  Check,
  Trash2,
  Sparkles,
  BarChart3,
  Map
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import ChartPanel from './ChartPanel'

// Code block component with copy functionality
function CodeBlock({ code, language = 'python' }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative mt-3 rounded-lg overflow-hidden bg-dark-900 border border-dark-500">
      <div className="flex items-center justify-between px-3 py-2 bg-dark-800 border-b border-dark-500">
        <span className="text-xs text-dark-200 font-mono">{language}</span>
        <button
          onClick={handleCopy}
          className="text-dark-200 hover:text-white transition-colors"
          title="Copy code"
        >
          {copied ? <Check className="w-4 h-4 text-accent-success" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm font-mono text-dark-100">
        <code>{code}</code>
      </pre>
    </div>
  )
}

// Single message component
function Message({ message }: { message: ChatMessage }) {
  const { showCode } = useAppStore()
  const isUser = message.role === 'user'

  return (
    <div className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-assistant'}`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg flex-shrink-0 ${isUser ? 'bg-accent-primary/20' : 'bg-dark-600'}`}>
          {isUser ? (
            <User className="w-4 h-4 text-accent-primary" />
          ) : (
            <Bot className="w-4 h-4 text-accent-secondary" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              components={{
                code: ({ children }) => (
                  <code className="bg-dark-600 px-1.5 py-0.5 rounded text-accent-primary text-sm">
                    {children}
                  </code>
                ),
                pre: ({ children }) => <>{children}</>,
                h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-semibold mt-3 mb-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-md font-semibold mt-2 mb-1">{children}</h3>,
                ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>,
                li: ({ children }) => <li className="text-dark-100">{children}</li>,
                strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
                table: ({ children }) => (
                  <table className="w-full border-collapse my-3 text-sm">
                    {children}
                  </table>
                ),
                th: ({ children }) => (
                  <th className="border border-dark-500 bg-dark-700 px-3 py-2 text-left font-semibold">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-dark-500 px-3 py-2">
                    {children}
                  </td>
                ),
                a: ({ children, href }) => (
                  <a href={href} className="text-accent-primary hover:underline" target="_blank" rel="noopener">
                    {children}
                  </a>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
          
          {/* Show code if available and enabled */}
          {message.code && showCode && (
            <CodeBlock code={message.code} language="python" />
          )}

          {/* Show data preview if available */}
          {message.data && !message.chart && (
            <div className="mt-3 p-3 bg-dark-800 rounded-lg border border-dark-500">
              <div className="text-xs text-dark-200 mb-2 font-medium flex items-center gap-1">
                <Map className="w-3 h-3" /> Location Data
              </div>
              <pre className="text-xs font-mono text-dark-100 overflow-x-auto">
                {JSON.stringify(message.data, null, 2)}
              </pre>
            </div>
          )}

          {/* Show indicators */}
          <div className="flex items-center gap-2 mt-2">
            {message.mapLayers && message.mapLayers.length > 0 && (
              <span className="text-xs bg-accent-primary/20 text-accent-primary px-2 py-0.5 rounded-full flex items-center gap-1">
                <Map className="w-3 h-3" /> {message.mapLayers.length} layers added
              </span>
            )}
            {message.chart && (
              <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full flex items-center gap-1">
                <BarChart3 className="w-3 h-3" /> Chart generated
              </span>
            )}
          </div>

          <div className="text-xs text-dark-300 mt-2">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ChatPanel() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  
  const { 
    messages, 
    isLoading, 
    addMessage, 
    setLoading, 
    clearMessages,
    showCode,
    toggleCode,
    addLayer,
    clearLayers,
    setMapAction,
    setChart,
    currentChart,
    showChart,
    toggleChart,
    setViewState
  } = useAppStore()

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle sending a message
  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    addMessage({
      role: 'user',
      content: userMessage,
    })

    setLoading(true)

    try {
      // Call the API
      const response = await geoApi.chat({
        query: userMessage,
      })

      // Add assistant response
      addMessage({
        role: 'assistant',
        content: response.message,
        code: response.code,
        mapLayers: response.map_layers,
        data: response.data,
        chart: response.chart as any,
        mapAction: response.map_action,
      })

      // Clear existing layers and add new ones
      if (response.map_layers && response.map_layers.length > 0) {
        clearLayers()
        response.map_layers.forEach((layer: any) => {
          addLayer({
            id: layer.id,
            name: layer.id,
            type: layer.type || 'geojson',
            visible: true,
            opacity: 1,
            source: layer.source,
            paint: layer.paint,
          })
        })
      }

      // Handle map action (flyTo, fitBounds, etc.)
      if (response.map_action) {
        if (response.map_action.type === 'flyTo' && response.map_action.center) {
          setViewState({
            longitude: response.map_action.center[0],
            latitude: response.map_action.center[1],
            zoom: response.map_action.zoom || 12,
            pitch: response.map_action.pitch || 0,
            bearing: response.map_action.bearing || 0,
          })
        }
        setMapAction(response.map_action)
      }

      // Handle chart data
      if (response.chart) {
        setChart(response.chart as any)
      }

    } catch (error) {
      console.error('Error sending message:', error)
      addMessage({
        role: 'assistant',
        content: '❌ Sorry, there was an error processing your request. Please make sure the backend server is running at http://localhost:8000',
      })
    } finally {
      setLoading(false)
    }
  }

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Example queries - updated with new capabilities
  const exampleQueries = [
    'Show me Astana',
    'Population of Almaty',
    '3D buildings in Astana',
    'Compare Astana vs Almaty',
    'Temperature in Karaganda',
    'Show all cities',
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-500">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-accent-primary" />
          <h2 className="font-semibold">ApexGIS Chat</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleChart}
            className={`p-2 rounded-lg transition-colors ${
              showChart ? 'bg-purple-500/20 text-purple-400' : 'hover:bg-dark-600'
            }`}
            title="Toggle chart display"
          >
            <BarChart3 className="w-4 h-4" />
          </button>
          <button
            onClick={toggleCode}
            className={`p-2 rounded-lg transition-colors ${
              showCode ? 'bg-accent-primary/20 text-accent-primary' : 'hover:bg-dark-600'
            }`}
            title="Toggle code display"
          >
            <Code className="w-4 h-4" />
          </button>
          <button
            onClick={() => {
              clearMessages()
              clearLayers()
              setChart(null)
            }}
            className="p-2 rounded-lg hover:bg-dark-600 transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="chat-message chat-message-assistant">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-dark-600">
                <Loader2 className="w-4 h-4 text-accent-secondary animate-spin" />
              </div>
              <span className="text-dark-200">Analyzing your query...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Chart Panel - show if we have chart data */}
      {currentChart && showChart && (
        <div className="px-6 pb-4">
          <ChartPanel chart={currentChart} />
        </div>
      )}

      {/* Example queries (show when no user messages) */}
      {messages.length === 1 && (
        <div className="px-6 pb-4">
          <div className="text-xs text-dark-300 mb-2">Try asking:</div>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((query) => (
              <button
                key={query}
                onClick={() => setInput(query)}
                className="px-3 py-1.5 text-xs bg-dark-700 hover:bg-dark-600 rounded-full border border-dark-500 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-dark-500">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about cities, population, 3D visualization, heatmaps..."
            className="flex-1 input-dark resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 p-3 rounded-lg bg-accent-primary text-dark-900 hover:bg-accent-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-all h-[60px]"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <div className="text-xs text-dark-300 mt-2">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}
