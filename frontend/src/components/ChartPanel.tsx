import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line, Bar, Doughnut, Pie } from 'react-chartjs-2'
import { useAppStore, ChartData } from '../store'
import { X, Maximize2, Minimize2 } from 'lucide-react'
import { useState } from 'react'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Chart.js default dark theme
ChartJS.defaults.color = '#9ca3af'
ChartJS.defaults.borderColor = 'rgba(255, 255, 255, 0.1)'

interface ChartPanelProps {
  chart: ChartData
}

export default function ChartPanel({ chart }: ChartPanelProps) {
  const { setChart } = useAppStore()
  const [isExpanded, setIsExpanded] = useState(false)

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: chart.type !== 'bar' && chart.type !== 'horizontalBar',
        position: 'top' as const,
        labels: {
          color: '#9ca3af',
          font: { size: 11 }
        }
      },
      title: {
        display: true,
        text: chart.title,
        color: '#ffffff',
        font: { size: 14, weight: 'bold' as const }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#9ca3af',
        borderColor: 'rgba(0, 212, 170, 0.3)',
        borderWidth: 1
      }
    },
    scales: chart.type === 'doughnut' || chart.type === 'pie' ? undefined : {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#9ca3af', font: { size: 10 } }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#9ca3af', font: { size: 10 } }
      }
    }
  }

  const horizontalOptions = {
    ...options,
    indexAxis: 'y' as const,
  }

  const data = {
    labels: chart.labels,
    datasets: chart.datasets.map(ds => ({
      ...ds,
      borderWidth: ds.borderColor ? 2 : 0,
    }))
  }

  const renderChart = () => {
    switch (chart.type) {
      case 'line':
        return <Line options={options} data={data} />
      case 'bar':
        return <Bar options={options} data={data} />
      case 'horizontalBar':
        return <Bar options={horizontalOptions} data={data} />
      case 'doughnut':
        return <Doughnut options={options} data={data} />
      case 'pie':
        return <Pie options={options} data={data} />
      default:
        return <Bar options={options} data={data} />
    }
  }

  return (
    <div className={`glass-panel ${isExpanded ? 'fixed inset-4 z-50' : 'relative'}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-dark-500">
        <span className="text-xs font-medium text-dark-200">📊 Chart</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-dark-600 rounded transition-colors"
            title={isExpanded ? 'Minimize' : 'Expand'}
          >
            {isExpanded ? <Minimize2 className="w-3 h-3" /> : <Maximize2 className="w-3 h-3" />}
          </button>
          <button
            onClick={() => setChart(null)}
            className="p-1 hover:bg-dark-600 rounded transition-colors"
            title="Close"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      </div>
      
      {/* Chart Container */}
      <div className={`p-3 ${isExpanded ? 'h-[calc(100%-40px)]' : 'h-64'}`}>
        {renderChart()}
      </div>
    </div>
  )
}
