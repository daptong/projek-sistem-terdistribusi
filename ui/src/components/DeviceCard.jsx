import React, {useState, useEffect} from 'react'
import GateControl from './GateControl'
import { controlDevice } from '../services/api'

export default function DeviceCard({device}){
  const [busy, setBusy] = useState(false)
  const state = device.state || {}
  const [animateClass, setAnimateClass] = useState('')
  const [updateClass, setUpdateClass] = useState('')
  const prevSnapshotRef = React.useRef(null)

  const toggleLamp = async ()=>{
    setBusy(true)
    try{
      const next = state.power === 'on' ? 'off' : 'on'
      // optimistic local animation
      setAnimateClass(next === 'on' ? 'animate-on' : 'animate-off')
      setTimeout(()=>setAnimateClass(''), 900)
      await controlDevice(device.id, device.type, next, {})
    }catch(e){
      console.error(e)
    }finally{
      setBusy(false)
    }
  }

  const online = state.online !== false // default assume online unless explicitly false

  useEffect(()=>{
    // trigger animation when reported state changes
    if(device.type === 'lamp'){
      const p = (state && state.power) || 'off'
      if(p === 'on'){
        setAnimateClass('animate-on')
        const t = setTimeout(()=>setAnimateClass(''),900)
        return ()=>clearTimeout(t)
      }else{
        setAnimateClass('animate-off')
        const t = setTimeout(()=>setAnimateClass(''),900)
        return ()=>clearTimeout(t)
      }
    }
    return undefined
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.power])

  // Trigger a small highlight on the card when device updates arrive (state or telemetry)
  useEffect(()=>{
    try{
      const snap = JSON.stringify({s: device.state || {}, t: device.last_telemetry || {}})
      if(prevSnapshotRef.current && prevSnapshotRef.current !== snap){
        // map device.type to a safe highlight class
        const dt = (device.type || '').toLowerCase()
        const base = dt.startsWith('camera') ? 'camera' : (dt === 'smart_gate' ? 'gate' : dt || 'generic')
        const cls = `highlight-${base}`
        setUpdateClass(cls)
        const t = setTimeout(()=>setUpdateClass(''), 900)
        return ()=>clearTimeout(t)
      }
      prevSnapshotRef.current = snap
    }catch(e){
      // ignore serialization errors
    }
  }, [device.state, device.last_telemetry, device.type])

  const renderIcon = (type) => {
    const t = (type||'').toLowerCase()
    if(t === 'lamp'){
      const isOn = state && state.power === 'on'
      return <div className={`device-icon lamp ${isOn ? 'on' : 'off'} ${animateClass}`}>💡</div>
    }
    if(t === 'thermostat') return <div className='device-icon thermostat'>🌡️</div>
    if(t.startsWith('camera')) return <div className='device-icon camera'>🎥</div>
    if(t === 'smart_gate') return <div className='device-icon gate'>🚪</div>
    if(t === 'tv') return <div className='device-icon tv'>📺</div>
    if(t === 'ac') return <div className='device-icon ac'>❄️</div>
    return <div className='device-icon'>🔌</div>
  }

  return (
    <div className={`card-inner ${updateClass}`}>
      <div className='device-header'>
        {renderIcon(device.type)}
        <div style={{flex:1,display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <div className='device-meta'>
            <div className='device-id'>{device.id}</div>
            <div className='device-type'>{device.type}</div>
          </div>
          <div>
            {online ? <span className='badge-online'>Online</span> : <span className='badge-offline'>Offline</span>}
          </div>
        </div>
      </div>

      <div className='device-state'>
        <pre>{JSON.stringify(state, null, 2)}</pre>
      </div>

      <div className='controls'>
        {device.type === 'lamp' && (
          <div className='device-actions'>
            <button className='btn' onClick={toggleLamp} disabled={busy}>{state.power === 'on' ? 'Turn off' : 'Turn on'}</button>
            <button className='btn secondary' onClick={()=>controlDevice(device.id, device.type, 'set_brightness', {value: 80})}>Set 80%</button>
          </div>
        )}

        {device.type === 'smart_gate' && (
          <GateControl device={device} />
        )}

        {device.type === 'thermostat' && (
          <div style={{display:'flex',gap:8}}>
            <input type='number' placeholder='target °C' defaultValue={state.setpoint || 24} id={`thermo-${device.id}`} style={{padding:6,borderRadius:6,border:'1px solid #ddd'}} />
            <button className='btn' onClick={()=>{const v=document.getElementById(`thermo-${device.id}`).value; controlDevice(device.id, device.type, 'set_temp',{target_temp: Number(v)})}}>Set</button>
          </div>
        )}

        {device.type === 'ac' && (
          <div style={{display:'flex',gap:8}}>
            <input type='number' placeholder='target °C' defaultValue={state.target_temp || 24} id={`ac-${device.id}`} style={{padding:6,borderRadius:6,border:'1px solid #ddd'}} />
            <button className='btn' onClick={()=>{const v=document.getElementById(`ac-${device.id}`).value; controlDevice(device.id, device.type, 'set_temp',{target_temp: Number(v)})}}>Set</button>
          </div>
        )}

        {device.type === 'tv' && (
          <div className='device-actions'>
            <button className='btn' onClick={()=>controlDevice(device.id, device.type, 'power_on')}>Power On</button>
            <button className='btn secondary' onClick={()=>controlDevice(device.id, device.type, 'power_off')}>Power Off</button>
            <button className='btn secondary' onClick={()=>controlDevice(device.id, device.type, 'set_volume',{value: Math.max(0,(state.volume||10)-1)})}>Vol -</button>
            <button className='btn secondary' onClick={()=>controlDevice(device.id, device.type, 'set_volume',{value: (state.volume||10)+1})}>Vol +</button>
          </div>
        )}

        {device.type && device.type.startsWith('camera') && (
          <div className='device-actions'>
            <button className='btn' onClick={()=>controlDevice(device.id, device.type, 'snapshot')}>Snapshot</button>
            <button className='btn secondary' onClick={()=>controlDevice(device.id, device.type, 'start_stream')}>Start Stream</button>
            <button className='btn secondary' onClick={()=>controlDevice(device.id, device.type, 'stop_stream')}>Stop Stream</button>
          </div>
        )}
      </div>
    </div>
  )
}
