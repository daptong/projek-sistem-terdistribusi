import React, {useEffect, useState, useRef} from 'react'
import DeviceList from './components/DeviceList'
import { getDevices } from './services/api'
import { connectWebSocket } from './services/ws'
import './styles.css'

export default function App(){
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [realtime, setRealtime] = useState(false)
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [lastUpdated, setLastUpdated] = useState(null)
  const wsRef = useRef(null)

  const load = async ()=>{
    try{
      setLoading(true)
      const d = await getDevices()
      setDevices(d)
      setLastUpdated(new Date().toISOString())
    }catch(e){
      setDevices([])
    }finally{
      setLoading(false)
    }
  }

  // initial load only; manual refresh via the Refresh button
  useEffect(()=>{ load() }, [])

  // Manage WebSocket connection when realtime toggle changes
  useEffect(()=>{
    // turn on realtime: open WS; turn off: close WS
    if(realtime){
      setWsStatus('connecting')
      wsRef.current = connectWebSocket((msg)=>{
        try{
          if(!msg) return
          if(msg.type === 'mqtt' && msg.topic){
            const parts = msg.topic.split('/')
            const deviceId = parts[2]
            if(!deviceId) return
            setDevices(prev => {
              const idx = prev.findIndex(d => d.id === deviceId || d.device_id === deviceId)
              if(idx === -1) return prev
              const copy = [...prev]
              const payload = msg.payload || {}
              copy[idx] = {
                ...copy[idx],
                last_telemetry: payload,
                state: payload.state || copy[idx].state
              }
              return copy
            })
            setLastUpdated(new Date().toISOString())
          }
        }catch(e){
          console.warn('ws msg handler error', e)
        }
      }, {
        onOpen: ()=> setWsStatus('connected'),
        onClose: ()=> setWsStatus('disconnected')
      })
    }else{
      if(wsRef.current){
        try{ wsRef.current.close() }catch(e){}
        wsRef.current = null
        setWsStatus('disconnected')
      }
    }
    // cleanup on unmount
    return ()=>{
      if(wsRef.current){ try{ wsRef.current.close() }catch(e){} wsRef.current = null }
    }
  }, [realtime])

  return (
    <div className='app-root'>
      <div className='header'>
        <div className='title'>
          <h1>🏡 IoT Home Dashboard</h1>
          <div className='small'>MQTT & Web UI</div>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:'8px'}}>
          <button className='btn' onClick={load}>Refresh</button>
          <label style={{display:'flex',alignItems:'center',gap:'6px'}}>
            <input type='checkbox' checked={realtime} onChange={(e)=>setRealtime(e.target.checked)} />
            <span style={{fontSize:'12px'}}>Real-time</span>
          </label>
          <div style={{fontSize:12,color:'#888'}}>
            {realtime ? `WS: ${wsStatus}` : `Mode: Manual`}
            {lastUpdated ? ` • Updated: ${new Date(lastUpdated).toLocaleTimeString()}` : ''}
          </div>
        </div>
      </div>

      <DeviceList devices={devices} loading={loading} />
    </div>
  )
}
