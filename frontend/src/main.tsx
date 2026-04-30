import { BrowserRouter } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import './index.css'
import MinimalApp from './MinimalApp'

const container = document.getElementById('root')
if (!container) throw new Error('Failed to find the root element')
const root = createRoot(container)

root.render(
  <BrowserRouter>
    <MinimalApp />
  </BrowserRouter>
)
